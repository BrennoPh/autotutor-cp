import os
from itertools import combinations
import pytest
from core.accounts import Accounts, AccessError
from core.progress_store import ProgressStore
from core.classrooms import Classrooms
from core.catalog import catalog, external_problems
from core.team_builder import form_trios, score_team, TOPICS


def setup_school():
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB'])
    accounts=Accounts(store)
    teacher=accounts.register('teacher','Professora','test-password','teacher')
    other=accounts.register('other','Outro professor','test-password','teacher')
    students=[accounts.register('student'+str(i),'Aluno '+str(i),'test-password') for i in range(4)]
    school=Classrooms(store,accounts)
    classroom=school.create(teacher,'Turma A')
    code=school.list_for(teacher)[0]['invite_code']
    for student in students:school.join(student,code)
    return store,accounts,school,teacher,other,students,classroom


def test_accounts_sessions_passwords_and_legacy():
    store=ProgressStore(os.environ['AUTOTUTOR_PROGRESS_DB'])
    store.save('0123456789abcdef0123456789abcdef',{'material':'Meu material'})
    accounts=Accounts(store)
    uid=accounts.register('aluno','Aluno','test-password',claim_legacy=True)
    assert accounts.user(uid)['profile_id']=='0123456789abcdef0123456789abcdef'
    with pytest.raises(AccessError):accounts.register('outro','Outro','test-password',claim_legacy=True)
    token=accounts.login('ALUNO','test-password')
    assert accounts.current(token)['id']==uid
    with store.connect() as db:
        row=db.execute('SELECT password_hash,salt FROM users').fetchone()
        assert row[0]!='test-password' and len(row[1])==64
        assert db.execute('SELECT token_hash FROM sessions').fetchone()[0]!=token
    accounts.logout(token)
    assert accounts.current(token) is None
    token=accounts.login('aluno','test-password')
    with store.connect() as db:db.execute('UPDATE sessions SET expires_at=0')
    assert accounts.current(token) is None
    for _ in range(5):
        with pytest.raises(ValueError):accounts.login('aluno','incorrect')
    with pytest.raises(ValueError,match='15 minutos'):accounts.login('aluno','test-password')


def test_permissions_assignments_and_verified_external():
    store,accounts,school,teacher,other,students,cid=setup_school()
    with pytest.raises(AccessError):school.create(students[0],'Invalid')
    for outsider in (other,):
        with pytest.raises(AccessError):school.roster(outsider,cid)
        with pytest.raises(AccessError):school.assignments(outsider,cid)
    with pytest.raises(AccessError):school.members(students[0],cid)
    assert 'invite_code' not in school.list_for(students[0])[0]
    p=next(p for p in __import__('core.catalog',fromlist=['catalog']).catalog() if p.get('external'))
    school.create_assignment(teacher,cid,'Lista 1',[p['id'],'dp'])
    assert len(school.assignments(students[0],cid)[0]['problem_ids'])==2
    with pytest.raises(AccessError):school.create_assignment(students[0],cid,'Outra',['dp'])
    with pytest.raises(ValueError):school.record_external(students[0],p['id'],'solved','https://evil.example/proof')
    school.record_external(students[0],p['id'],'solved')
    assert not school.external_for(students[0])[p['id']]['verified']
    with pytest.raises(AccessError):school.verify_external(other,cid,students[0],p['id'])
    school.verify_external(teacher,cid,students[0],p['id'])
    assert school.external_for(students[0])[p['id']]['verified']
    assert school.external_for(students[1])=={}
    roster=school.roster(teacher,cid)
    assert next(m for m in roster if m['id']==students[0])['verified_external']==[p['id']]
    school.record_external(students[0],p['id'],'in_progress')
    assert not school.external_for(students[0])[p['id']]['verified']
    payload={'teams':[students[:3]],'waiting':[students[3]]}
    school.save_formation(teacher,cid,'Complementaridade',payload)
    assert school.formations(students[3],cid)[0]['teams']==[]
    assert len(school.formations(students[0],cid)[0]['teams'][0])==3
    with pytest.raises(ValueError):school.save_formation(teacher,cid,'Complementaridade',{'teams':[[students[0]]*3]})


def test_catalog_real_sources_unique_and_external_boundary():
    problems=catalog();external=external_problems()
    assert len(problems)>=500
    assert len({p['id'] for p in problems})==len(problems)
    assert len({p['url'] for p in external})==len(external)
    assert sum(p['source']=='CSES' for p in external)==400
    assert all(p['external'] and p['url'].startswith('https://') and 'std_cpp' not in p for p in external)


def candidates(n):
    return [dict(id=str(i),name='Aluno '+str(i),skills={t:((i+j*3)%11)/10 for j,t in enumerate(TOPICS)},local_solved=[str(i)],evidence=1) for i in range(n)]


def test_best_trio_and_exact_partition_match_exhaustive():
    students=candidates(6)
    best=form_trios(students,mode='Melhor trio')
    expected=max(score_team(list(t),'Complementaridade') for t in combinations(students,3))
    assert best['details'][0]['score']==pytest.approx(expected,abs=.00001)
    formed=form_trios(students)
    possible=[]
    for others in combinations(range(1,6),2):
        first=[students[i] for i in (0,*others)]
        rest=[s for s in students if s not in first]
        possible.append(score_team(first,'Complementaridade')+score_team(rest,'Complementaridade'))
    assert sum(t['score'] for t in formed['details'])==pytest.approx(max(possible),abs=.00002)


@pytest.mark.parametrize('n',[3,4,5,12,16])
def test_teams_have_no_duplicates_and_disclose_search(n):
    students=candidates(n)
    result=form_trios(students)
    all_ids=[i for t in result['teams'] for i in t]+result['waiting']
    assert len(all_ids)==len(set(all_ids))==n
    assert len(result['waiting'])==n%3
    assert result==form_trios(students)
    assert ('Heurística' in result['method'])==(n>12)
