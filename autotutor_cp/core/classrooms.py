"""Teacher-owned classes, explicit enrollment and permission-checked progress views."""
import json
import secrets
import uuid
from core.accounts import AccessError
from core.catalog import catalog_map, valid_proof
from core.learning_engine import learning_stats


class Classrooms:
    def __init__(self,store,accounts):
        self.store=store;self.accounts=accounts
        with store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS classrooms (id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, name TEXT NOT NULL, description TEXT NOT NULL, invite_code TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS memberships (classroom_id TEXT NOT NULL, user_id TEXT NOT NULL, joined_at TEXT NOT NULL, PRIMARY KEY(classroom_id,user_id))')
            db.execute('CREATE TABLE IF NOT EXISTS assignments (id TEXT PRIMARY KEY,classroom_id TEXT NOT NULL,title TEXT NOT NULL,problem_ids TEXT NOT NULL,created_at TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS external_progress (user_id TEXT NOT NULL,problem_id TEXT NOT NULL,status TEXT NOT NULL,proof_url TEXT NOT NULL,verified_by TEXT,updated_at TEXT NOT NULL,PRIMARY KEY(user_id,problem_id))')
            db.execute('CREATE TABLE IF NOT EXISTS formations (id TEXT PRIMARY KEY,classroom_id TEXT NOT NULL,strategy TEXT NOT NULL,payload TEXT NOT NULL,created_at TEXT NOT NULL)')

    def _class(self,viewer_id,class_id,teacher_only=False):
        self.accounts.user(viewer_id)
        with self.store.connect() as db:
            row=db.execute('SELECT id,owner_id,name,description,invite_code,created_at FROM classrooms WHERE id=?',(class_id,)).fetchone()
            if not row:raise AccessError('Turma não encontrada.')
            owner=row[1]==viewer_id
            member=db.execute('SELECT 1 FROM memberships WHERE classroom_id=? AND user_id=?',(class_id,viewer_id)).fetchone()
        if not owner and (teacher_only or not member):raise AccessError('Você não tem acesso a esta turma.')
        value=dict(zip(('id','owner_id','name','description','invite_code','created_at'),row))
        if not owner:value.pop('invite_code')
        return value

    def create(self,teacher_id,name,description=''):
        if self.accounts.user(teacher_id)['role']!='teacher':raise AccessError('Somente professores podem criar turmas.')
        name=name.strip();description=description.strip()
        if not 2<=len(name)<=100 or len(description)>1000:raise ValueError('Informe um nome de 2 a 100 caracteres e uma descrição de até 1000.')
        identifier=uuid.uuid4().hex
        with self.store.connect() as db:
            db.execute('INSERT INTO classrooms VALUES (?,?,?,?,?,?)',(identifier,teacher_id,name,description,secrets.token_hex(5).upper(),self.store.now()))
        return identifier

    def list_for(self,user_id):
        self.accounts.user(user_id)
        with self.store.connect() as db:
            rows=db.execute('SELECT DISTINCT c.id FROM classrooms c LEFT JOIN memberships m ON m.classroom_id=c.id WHERE c.owner_id=? OR m.user_id=? ORDER BY c.created_at DESC',(user_id,user_id)).fetchall()
        return [self._class(user_id,r[0]) for r in rows]

    def join(self,user_id,code):
        user=self.accounts.user(user_id)
        if user['role']!='student':raise AccessError('A entrada por código é destinada às contas de aluno.')
        with self.store.connect() as db:
            row=db.execute('SELECT id FROM classrooms WHERE invite_code=?',(code.strip().upper(),)).fetchone()
            if not row:raise ValueError('Código de turma inválido.')
            db.execute('INSERT OR IGNORE INTO memberships VALUES (?,?,?)',(row[0],user_id,self.store.now()))
        return row[0]

    def members(self,teacher_id,class_id):
        self._class(teacher_id,class_id,True)
        with self.store.connect() as db:
            rows=db.execute('SELECT u.id,u.username,u.name,u.role,u.profile_id FROM users u JOIN memberships m ON m.user_id=u.id WHERE m.classroom_id=? ORDER BY u.name,u.id',(class_id,)).fetchall()
        return [dict(zip(('id','username','name','role','profile_id'),row)) for row in rows]

    def create_assignment(self,teacher_id,class_id,title,problem_ids):
        self._class(teacher_id,class_id,True)
        available=catalog_map();problem_ids=list(dict.fromkeys(problem_ids))
        if not title.strip() or len(title)>120 or not 1<=len(problem_ids)<=100 or any(p not in available for p in problem_ids):
            raise ValueError('Informe um título e selecione de 1 a 100 problemas do catálogo.')
        with self.store.connect() as db:
            db.execute('INSERT INTO assignments VALUES (?,?,?,?,?)',(uuid.uuid4().hex,class_id,title.strip(),json.dumps(problem_ids),self.store.now()))

    def assignments(self,viewer_id,class_id):
        self._class(viewer_id,class_id)
        with self.store.connect() as db:rows=db.execute('SELECT id,title,problem_ids,created_at FROM assignments WHERE classroom_id=? ORDER BY rowid DESC',(class_id,)).fetchall()
        return [dict(id=r[0],title=r[1],problem_ids=json.loads(r[2]),time=r[3]) for r in rows]

    def record_external(self,user_id,problem_id,status,proof_url=''):
        self.accounts.user(user_id)
        problem=catalog_map().get(problem_id)
        if not problem or not problem.get('external') or status not in ('in_progress','solved'):
            raise ValueError('Problema externo ou status inválido.')
        proof=valid_proof(problem,proof_url)
        with self.store.connect() as db:
            db.execute('INSERT INTO external_progress VALUES (?,?,?,?,NULL,?) ON CONFLICT(user_id,problem_id) DO UPDATE SET status=excluded.status,proof_url=excluded.proof_url,verified_by=NULL,updated_at=excluded.updated_at',
                       (user_id,problem_id,status,proof,self.store.now()))

    def external_for(self,user_id):
        self.accounts.user(user_id)
        with self.store.connect() as db:rows=db.execute('SELECT problem_id,status,proof_url,verified_by,updated_at FROM external_progress WHERE user_id=?',(user_id,)).fetchall()
        return {r[0]:dict(status=r[1],proof_url=r[2],verified=bool(r[3]),updated_at=r[4]) for r in rows}

    def verify_external(self,teacher_id,class_id,student_id,problem_id):
        self._class(teacher_id,class_id,True)
        with self.store.connect() as db:
            if not db.execute('SELECT 1 FROM memberships WHERE classroom_id=? AND user_id=?',(class_id,student_id)).fetchone():raise AccessError('Aluno fora desta turma.')
            changed=db.execute('UPDATE external_progress SET verified_by=?,updated_at=? WHERE user_id=? AND problem_id=? AND status=\'solved\'',(teacher_id,self.store.now(),student_id,problem_id)).rowcount
            if not changed:raise ValueError('Não há conclusão externa a confirmar.')

    def roster(self,teacher_id,class_id):
        members=self.members(teacher_id,class_id)
        problems=catalog_map()
        result=[]
        for member in members:
            state=self.store.load(member['profile_id'])
            history=state.get('history',[])
            # Solved once remains evidence; repeated ACs on one problem do not inflate the count.
            local_solved={h.get('problem_id') or h.get('problem') for h in history if h.get('verdict')=='AC'}
            external=self.external_for(member['id'])
            declared={pid for pid,p in external.items() if p['status']=='solved' and problems.get(pid,{}).get('external')}
            verified={pid for pid in declared if external[pid]['verified']}
            stats=learning_stats(state.get('quiz_attempts',[]),history)
            from core.ai_coach import learner_evidence,cached_analysis
            evidence=learner_evidence(state.get('quiz_attempts',[]),history,state.get('completed_lessons',[]),state.get('study_hours',3))
            analysis=cached_analysis(self.store,member['profile_id'],evidence)
            strengths={s['title']:s['accuracy'] for s in stats if s['answered']}
            measured=sum(s['answered'] for s in stats);correct=sum(s['correct'] for s in stats)
            result.append(dict(member,local_solved=sorted(local_solved),external_solved=sorted(declared),verified_external=sorted(verified),
                skills=strengths,topic_statistics=stats,level=analysis['level'] if analysis else 'Não avaliado',
                level_source=('IA · '+analysis['model']) if analysis else 'aguardando análise de IA',quiz_answered=measured,quiz_correct=correct,
                submissions=len(history),lessons=len(state.get('completed_lessons',[])),external=external,
                evidence=len(local_solved)+len(verified)+measured))
        return result

    def save_formation(self,teacher_id,class_id,strategy,payload):
        members={m['id'] for m in self.members(teacher_id,class_id)}
        participants=[uid for team in payload.get('teams',[]) for uid in team]+payload.get('waiting',[])
        if not participants or len(set(participants))!=len(participants) or not set(participants)<=members:
            raise ValueError('A formação contém participantes inválidos ou repetidos.')
        if any(len(team)!=3 for team in payload.get('teams',[])):raise ValueError('Cada trio precisa conter três alunos.')
        identifier=uuid.uuid4().hex
        with self.store.connect() as db:
            db.execute('INSERT INTO formations VALUES (?,?,?,?,?)',(identifier,class_id,strategy,json.dumps(payload,ensure_ascii=False),self.store.now()))
        return identifier

    def formations(self,viewer_id,class_id):
        classroom=self._class(viewer_id,class_id)
        teacher=classroom['owner_id']==viewer_id
        with self.store.connect() as db:
            rows=db.execute('SELECT strategy,payload,created_at FROM formations WHERE classroom_id=? ORDER BY rowid DESC LIMIT 10',(class_id,)).fetchall()
            names={r[0]:r[1] for r in db.execute('SELECT id,name FROM users')}
        result=[]
        for strategy,payload,date in rows:
            value=json.loads(payload)
            teams=value['teams'] if teacher else [t for t in value['teams'] if viewer_id in t]
            result.append(dict(strategy=strategy,teams=[[names.get(uid,'Conta indisponível') for uid in t] for t in teams],time=date,
                               waiting=[names.get(uid,'Conta indisponível') for uid in value.get('waiting',[]) if teacher or uid==viewer_id]))
        return result
