import uuid
import pytest
from core.progress_store import ProgressStore
from core.library import Library, resources, deep_guides, references_for, study_entry, content_links, safe_url
from core.problem_bank import load_problems,validate_input
from core.autocode_engine import AutoCodeEngine
from core.mini_judge import MiniJudge,JudgeError


def test_library_archives_are_paginated_private_and_include_older_items(tmp_path):
    store=ProgressStore(tmp_path/'library.sqlite3');a=uuid.uuid4().hex;b=uuid.uuid4().hex;library=Library(store)
    ids=[store.add_artifact(a,'material','Texto '+str(i),{'content':'Conteúdo '+str(i),'concept':'DP','source':'Gemini'}) for i in range(27)]
    store.add_artifact(b,'material','Privado',{'content':'Segredo'})
    result=library.page(a)
    assert result['total']==27 and len(result['items'])==12
    assert library.page(a,page=3)['items'][-1]['id']==ids[0]
    assert library.page(a,search='Segredo')['total']==0
    library.set_state(a,ids[0],'Estudado','Revisar a prova')
    assert library.page(a,status='Estudado')['items'][0]['id']==ids[0]
    assert Library(ProgressStore(store.path)).get_state(a,ids[0])['note']=='Revisar a prova'
    with pytest.raises(PermissionError):library.set_state(b,ids[0],'Estudado')
    assert store.export_profile(a)['library_state'][0]['note']=='Revisar a prova'
    assert not store.export_profile(b)['library_state']


def test_resources_guides_bookmarks_and_link_validation(tmp_path):
    assert len(resources())>=40 and len(deep_guides())==9
    assert sum(len(s['body'].split()) for g in deep_guides() for s in g['sections'])>3500
    assert len({r['url'] for r in resources()})==len(resources())
    assert all(safe_url(r['url']) and r['source_url'] and r['verification'] for r in resources())
    assert {r['kind'] for r in references_for('DP')}>={'Artigo','Vídeo'}
    assert not safe_url('javascript:alert(1)') and not safe_url('https://user:pass@example.com/')
    unknown=content_links('[Vídeo](https://example.com/new)')
    assert 'não verificado' in unknown[0]['verification']
    store=ProgressStore(tmp_path/'db.sqlite3');library=Library(store);pid=uuid.uuid4().hex
    ref=references_for('DP')[0]
    first=library.save_resource(pid,ref);second=library.save_resource(pid,ref)
    assert first==second and library.page(pid)['total']==1
    library.set_state(pid,deep_guides()[0]['id'],'Estudando','Comecei')
    assert library.get_state(pid,deep_guides()[0]['id'])['status']=='Estudando'


def test_generated_problem_library_does_not_reveal_solutions():
    p=dict(load_problems()[0]);p['std_cpp']='PRIVATE_REFERENCE';p['brute_cpp']='PRIVATE_ORACLE'
    entry=study_entry(dict(id='example',kind='problem',title=p['title'],payload=p,time='now'))
    assert entry['content']==p['statement']
    assert 'PRIVATE_REFERENCE' not in str(entry) and 'PRIVATE_ORACLE' not in str(entry)


def test_new_pack_contracts_and_rejection_of_corrupt_reference(tmp_path):
    pack=[p for p in load_problems() if p.get('local_task')]
    assert len(pack)==24
    for p in pack:
        for example in p['examples']:assert validate_input(p,example['input'])
        assert not p['external'] and p['attribution']['url'].startswith('https://cses.fi/')
    bad=dict(pack[0],std_cpp='#include <iostream>\nint main(){std::cout<<-1;}')
    with pytest.raises(JudgeError,match='divergência'):AutoCodeEngine(judge=MiniJudge(tmp_path/'judge')).double_validate(bad)
    for name,text in [('missing','3\n1 1\n'),('rmq','2 1\n1 2\n0 2\n'),('rooms','2 3\n...\n..\n'),('coins2','2 8\n1 1\n')]:
        with pytest.raises(ValueError):validate_input(next(p for p in pack if p['local_task']==name),text)
