"""SQLite profiles, generated artifacts and model-call history. API keys are excluded."""
from datetime import datetime
from contextlib import contextmanager
import json
from pathlib import Path
import re
import sqlite3
import uuid
from zoneinfo import ZoneInfo

DB_PATH = Path(__file__).resolve().parents[1] / 'data' / 'progress.sqlite3'
FIELDS = ('history','quiz_attempts','completed_lessons','study_hours','problems','results',
          'feedback','feedback_sources','helpers','recommendations','material','material_source',
          'drafts','ai_events','model_capabilities','level','diagnostic_draft','learning_topic','theme_dark','lab_preferences',
          'onboarding_completed','diagnostic_score','strong_topics','gap_topics')


class ProgressStore:
    def __init__(self, path=DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)')
            db.execute('CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL)')
            db.execute('CREATE INDEX IF NOT EXISTS artifacts_profile ON artifacts(profile_id,created_at)')
            db.execute('CREATE TABLE IF NOT EXISTS model_calls (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, provider TEXT NOT NULL, model TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL)')
            db.execute('CREATE INDEX IF NOT EXISTS calls_profile ON model_calls(profile_id,created_at)')
            db.execute('CREATE TABLE IF NOT EXISTS library_state (profile_id TEXT NOT NULL,item_id TEXT NOT NULL,status TEXT NOT NULL,note TEXT NOT NULL,updated_at TEXT NOT NULL,PRIMARY KEY(profile_id,item_id))')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            db.execute('PRAGMA journal_mode=WAL')
            with db:
                yield db
        finally:
            db.close()

    def profiles(self):
        with self.connect() as db:
            return [r[0] for r in db.execute('SELECT id FROM profiles ORDER BY updated_at DESC,rowid DESC')]

    def latest_profile_id(self):
        profiles = self.profiles()
        return profiles[0] if profiles else None

    def load(self, profile_id):
        self.validate_id(profile_id)
        with self.connect() as db:
            row = db.execute('SELECT payload FROM profiles WHERE id=?', (profile_id,)).fetchone()
        return json.loads(row[0]) if row else {}

    def save(self, profile_id, state):
        self.validate_id(profile_id)
        payload = json.dumps({k:state[k] for k in FIELDS if k in state}, ensure_ascii=False, allow_nan=False)
        with self.connect() as db:
            db.execute('INSERT INTO profiles (id,payload) VALUES (?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,updated_at=CURRENT_TIMESTAMP',
                       (profile_id, payload))

    def add_artifact(self, profile_id, kind, title, payload):
        self.validate_id(profile_id)
        identifier = uuid.uuid4().hex
        with self.connect() as db:
            db.execute('INSERT INTO artifacts VALUES (?,?,?,?,?,?)',
                       (identifier, profile_id, kind, title, json.dumps(payload,ensure_ascii=False,allow_nan=False), self.now()))
        # Capture only a sanitized activity summary. Full content remains in the
        # existing private artifact store and is never copied to the memory index.
        from core.learner_memory import LearnerMemory
        LearnerMemory(self).capture_artifact(profile_id, kind, title, payload, identifier)
        return identifier

    def artifacts(self, profile_id, kind=None, limit=50):
        self.validate_id(profile_id)
        with self.connect() as db:
            rows = db.execute('SELECT id,kind,title,payload,created_at FROM artifacts WHERE profile_id=? '
                              + ('AND kind=? ' if kind else '') + 'ORDER BY rowid DESC LIMIT ?',
                              (profile_id,kind,limit) if kind else (profile_id,limit)).fetchall()
        return [dict(id=r[0],kind=r[1],title=r[2],payload=json.loads(r[3]),time=r[4]) for r in rows]

    def log_model_call(self, profile_id, record):
        self.validate_id(profile_id)
        # Explicit whitelist; no SDK client, credential, request header or cookie is stored.
        clean = {k:record[k] for k in ('provider','model','system','prompt','response','error','context_chars') if k in record}
        with self.connect() as db:
            db.execute('INSERT INTO model_calls VALUES (?,?,?,?,?,?)',
                       (uuid.uuid4().hex,profile_id,record['provider'],record['model'],json.dumps(clean,ensure_ascii=False),self.now()))
        from core.learner_memory import LearnerMemory
        LearnerMemory(self).capture_model_call(profile_id, clean)

    def learning_evidence(self, profile_id, query=None):
        """Owner-scoped numeric evidence and AI Memory retention briefing; no private code."""
        from core.learning_engine import learning_stats
        state = self.load(profile_id)
        stats = learning_stats(state.get('quiz_attempts', []), state.get('history', []))
        measured = [{k: s[k] for k in ('title', 'answered', 'correct', 'distinct_problems', 'accepted_problems')}
                    for s in stats if s['answered'] or s['distinct_problems']]
        from core.learner_memory import LearnerMemory
        memory = LearnerMemory(self).brief(profile_id, query or '', max_chars=1200)
        return {'measured_topics': measured[:16],
                'recent_verdicts': [{'topic': str(h.get('topic', ''))[:80], 'verdict': str(h.get('verdict', ''))[:10]}
                                    for h in state.get('history', [])[-6:]],
                'ai_memory': memory,
                'scope': 'Amostra limitada: leituras não comprovam domínio. Ajuste pré-requisitos e exemplos com base nas lacunas retidas na memória; preserve o pedido e o nível escolhidos.'}

    def context(self, profile_id, query, max_chars=7000):
        from core.learning_engine import learning_stats
        state = self.load(profile_id)
        stats = learning_stats(state.get('quiz_attempts',[]),state.get('history',[]))
        measured = [{k:s[k] for k in ('title','answered','correct','accuracy','distinct_problems','accepted_problems')}
                    for s in stats if s['answered'] or s['distinct_problems']]
        recent = [{k:str(h.get(k,''))[:150] for k in ('problem','topic','verdict','time')} for h in state.get('history',[])[-6:]]
        terms = set(re.findall(r'\w{2,}', query.casefold()))
        artifacts = self.artifacts(profile_id, kind='material', limit=100)
        artifacts.sort(key=lambda a:len(terms & set(re.findall(r'\w{2,}',(a['title']+' '+a['payload'].get('concept','')).casefold()))),reverse=True)
        excerpts = [{'title':a['title'],'concept':a['payload'].get('concept'),
                     'excerpt':a['payload'].get('content','')[:850]} for a in artifacts[:3]]
        plans=self.artifacts(profile_id,kind='topic_plan',limit=1)
        current_plan={'title':plans[0]['title'],'style':plans[0]['payload'].get('preferences',{}).get('style')} if plans else None
        from core.learner_memory import LearnerMemory
        memory=LearnerMemory(self).brief(profile_id,query,max_chars=min(1600,max(450,max_chars//3)))
        value = {'current_topic_plan':current_plan,'chosen_level':state.get('level'),'measured_topics':measured,'recent_submissions':recent,
                 'read_lessons':state.get('completed_lessons',[]),'related_previous_materials':excerpts,
                 'learner_memory':memory,
                 'instruction':'Use estes dados como evidência limitada; adapte explicações às dificuldades observadas e não trate leituras como domínio comprovado.'}
        # Keep complete JSON, removing excerpts first if the budget is reached.
        while excerpts and len(json.dumps(value,ensure_ascii=False)) > max_chars:
            excerpts.pop()
        while recent and len(json.dumps(value,ensure_ascii=False)) > max_chars:
            recent.pop(0)
        while measured and len(json.dumps(value,ensure_ascii=False)) > max_chars:
            measured.pop()
        text = json.dumps(value,ensure_ascii=False)
        return text if len(text) <= max_chars else '{}' 

    def export_profile(self, profile_id):
        self.validate_id(profile_id)
        with self.connect() as db:
            artifacts = db.execute('SELECT id,kind,title,payload,created_at FROM artifacts WHERE profile_id=? ORDER BY rowid',(profile_id,)).fetchall()
            calls = db.execute('SELECT id,payload,created_at FROM model_calls WHERE profile_id=? ORDER BY rowid',(profile_id,)).fetchall()
            study=db.execute('SELECT item_id,status,note,updated_at FROM library_state WHERE profile_id=?',(profile_id,)).fetchall()
            has_plans=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='topic_plan_progress'").fetchone()
            plan_progress=db.execute('SELECT plan_id,session_index,activity_index,completed,updated_at FROM topic_plan_progress WHERE profile_id=?',(profile_id,)).fetchall() if has_plans else []
        from core.learner_memory import LearnerMemory
        return {'schema_version':3,'topic_plan_progress':[dict(plan_id=r[0],session_index=r[1],activity_index=r[2],completed=bool(r[3]),time=r[4]) for r in plan_progress],'library_state':[dict(item_id=r[0],status=r[1],note=r[2],time=r[3]) for r in study],'profile_id':profile_id,'state':self.load(profile_id),
                'artifacts':[dict(id=r[0],kind=r[1],title=r[2],payload=json.loads(r[3]),time=r[4]) for r in artifacts],
                'model_calls':[dict(id=r[0],payload=json.loads(r[1]),time=r[2]) for r in calls],
                'ai_memory':LearnerMemory(self).export(profile_id)}

    def counts(self, profile_id):
        self.validate_id(profile_id)
        with self.connect() as db:
            return {table:db.execute(f'SELECT COUNT(*) FROM {table} WHERE profile_id=?',(profile_id,)).fetchone()[0]
                    for table in ('artifacts','model_calls')}

    @staticmethod
    def now():
        return datetime.now(ZoneInfo('America/Maceio')).isoformat(timespec='seconds')

    @staticmethod
    def validate_id(value):
        if not isinstance(value,str) or uuid.UUID(value).hex != value:
            raise ValueError('Identificador de perfil inválido.')
