"""Anonymized, evidence-bound formative assessment with teacher review.

Model prose is a proposal, never a grade. Numeric facts live in typed citations;
qualitative interpretations still require the teacher's judgment.
"""
import hashlib
import json
import re
import uuid
from jsonschema import validate, ValidationError
from core.accounts import AccessError
from core.learning_engine import learning_stats, load_curriculum
from core.research.provider import configured_provider, ResearchError

VERSION = 'learner-assessment.v1'
METRICS = ('answered', 'correct', 'distinct_problems', 'accepted_problems', 'submissions', 'compile_errors')
LEVELS = ('Inconclusivo', 'Iniciante', 'Em desenvolvimento')
DECISIONS = ('approved', 'revision_requested', 'rejected')


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def evidence_snapshot(state):
    """Drop names, IDs, code, free text and reading claims before any API call."""
    topics = []
    for index, stat in enumerate(learning_stats(state.get('quiz_attempts', []), state.get('history', []))):
        topics.append(dict(evidence_id=f't{index:02d}', topic_id=stat['id'],
                           **{metric: int(stat[metric]) for metric in METRICS}))
    distinct = sum(t['answered'] + t['distinct_problems'] for t in topics)
    return {'version': VERSION, 'topics': topics, 'distinct_items': distinct,
            'sufficient_evidence': distinct >= 3,
            'scope': 'Questionários locais e vereditos registrados; não demonstram domínio geral. Leituras e declarações externas excluídas.'}


def assessment_schema(snapshot):
    text = {'type': 'string', 'minLength': 1, 'maxLength': 500}
    observation = {'type': 'object', 'properties': {
        'evidence_id': {'type': 'string', 'enum': [t['evidence_id'] for t in snapshot['topics']]},
        'metric': {'type': 'string', 'enum': list(METRICS)},
        'value': {'type': 'integer', 'minimum': 0}, 'interpretation': text},
        'required': ['evidence_id', 'metric', 'value', 'interpretation'], 'additionalProperties': False}
    action = {'type': 'object', 'properties': {
        'topic_id': {'type': 'string', 'enum': [t['id'] for t in load_curriculum()]},
        'evidence_ids': {'type': 'array', 'items': {'type': 'string', 'enum': [t['evidence_id'] for t in snapshot['topics']]}, 'minItems': 1, 'maxItems': 3, 'uniqueItems': True},
        'action': text}, 'required': ['topic_id', 'evidence_ids', 'action'], 'additionalProperties': False}
    properties = {'level': {'type': 'string', 'enum': list(LEVELS)},
                  'confidence': {'type': 'string', 'enum': ['baixa', 'média']}, 'summary': text,
                  'observations': {'type': 'array', 'items': observation, 'minItems': 1, 'maxItems': 8},
                  'next_steps': {'type': 'array', 'items': action, 'minItems': 1, 'maxItems': 4}}
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def validate_assessment(answer, snapshot):
    try:
        validate(answer, assessment_schema(snapshot))
    except ValidationError as exc:
        raise ResearchError('Avaliação recusada: estrutura ou competência inválida.') from exc
    if not snapshot['sufficient_evidence'] and (answer['level'] != 'Inconclusivo' or answer['confidence'] != 'baixa'):
        raise ResearchError('Avaliação recusada: evidências insuficientes exigem nível inconclusivo e confiança baixa.')
    by_id = {t['evidence_id']: t for t in snapshot['topics']}
    for observation in answer['observations']:
        if observation['value'] != by_id[observation['evidence_id']][observation['metric']]:
            raise ResearchError('Avaliação recusada: contagem não corresponde à evidência local.')
    # Counts must be in independently checked typed fields, never invented in prose.
    prose = [answer['summary']] + [o['interpretation'] for o in answer['observations']] + [a['action'] for a in answer['next_steps']]
    for text in prose:
        if re.search(r'\d|%|\bpor cento\b|\b(zero|dois|duas|três|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|quatorze|catorze|quinze|dezesseis|dezasseis|dezessete|dezassete|dezoito|dezenove|vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa|cem|cento|duzent[oa]s|trezent[oa]s|quatrocent[oa]s|quinhent[oa]s|seiscent[oa]s|setecent[oa]s|oitocent[oa]s|novecent[oa]s|mil|milhão|milhões|metade|dobro)\b', text, re.I):
            raise ResearchError('Avaliação recusada: deixe contagens apenas nas citações numéricas verificáveis.')
    return answer


class LearnerAssessmentService:
    def __init__(self, store, accounts, classrooms, provider=None):
        self.store, self.accounts, self.classrooms = store, accounts, classrooms
        self.provider = provider  # Lazily constructed: rendering UI never makes requests.
        with store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS learner_assessments (id TEXT PRIMARY KEY,classroom_id TEXT NOT NULL,student_id TEXT NOT NULL,evidence_hash TEXT NOT NULL,payload TEXT NOT NULL,created_at TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS learner_assessment_reviews (id TEXT PRIMARY KEY,assessment_id TEXT NOT NULL,teacher_id TEXT NOT NULL,decision TEXT NOT NULL,comment TEXT NOT NULL,created_at TEXT NOT NULL)')

    def _authorize(self, viewer_id, class_id, student_id, teacher_only=False):
        classroom = self.classrooms._class(viewer_id, class_id, teacher_only)
        student = self.accounts.user(student_id)
        with self.store.connect() as db:
            member = db.execute('SELECT 1 FROM memberships WHERE classroom_id=? AND user_id=?', (class_id, student_id)).fetchone()
        if student['role'] != 'student' or not member:
            raise AccessError('Aluno não pertence a esta turma.')
        if viewer_id not in (student_id, classroom['owner_id']):
            raise AccessError('Você não pode acessar a avaliação deste aluno.')
        return student

    def evidence(self, viewer_id, class_id, student_id):
        student = self._authorize(viewer_id, class_id, student_id)
        return evidence_snapshot(self.store.load(student['profile_id']))

    def _rows(self, class_id, student_id):
        with self.store.connect() as db:
            rows = db.execute('SELECT id,payload,created_at FROM learner_assessments WHERE classroom_id=? AND student_id=? ORDER BY rowid DESC', (class_id, student_id)).fetchall()
        return [dict(id=r[0], **json.loads(r[1]), created_at=r[2]) for r in rows]

    def list_for(self, viewer_id, class_id, student_id):
        snapshot = self.evidence(viewer_id, class_id, student_id)
        key = hashlib.sha256(encoded(snapshot).encode()).hexdigest()
        return [dict(row, stale=row['evidence_hash'] != key) for row in self._rows(class_id, student_id)]

    def get(self, viewer_id, assessment_id):
        with self.store.connect() as db:
            row = db.execute('SELECT classroom_id,student_id FROM learner_assessments WHERE id=?', (assessment_id,)).fetchone()
        if not row:
            raise AccessError('Avaliação não encontrada.')
        return next(a for a in self.list_for(viewer_id, *row) if a['id'] == assessment_id)

    def generate(self, viewer_id, class_id, student_id, *, synthetic=False, allow_real_data=False):
        snapshot = self.evidence(viewer_id, class_id, student_id)
        if not synthetic and not allow_real_data:
            raise ResearchError('Autorize explicitamente o envio somente das estatísticas anônimas; nenhum dado foi enviado.')
        # Synthetic is an audit label set by controlled validation fixtures, not anonymization.
        key = hashlib.sha256(encoded(snapshot).encode()).hexdigest()
        provider = self.provider or configured_provider()  # Uses the shared free-only BudgetLedger.
        config = getattr(provider, 'config', None)
        model = getattr(config, 'model', getattr(provider, 'model', 'injected-test-provider'))
        for row in self._rows(class_id, student_id):
            if row['evidence_hash'] == key and row['requested_model'] == model and row['synthetic'] == synthetic and row['status'] in ('pending', 'approved'):
                return dict(row, stale=False, cached=True)
        system = ('Você propõe avaliação FORMATIVA de programação competitiva básica para revisão humana. '
                  'Nunca atribua nota definitiva, diagnóstico psicológico ou domínio comprovado. Use somente os dados. '
                  'Cite fatos numéricos em observations com evidence_id, metric e value exatos. '
                  'Nas frases não escreva números, percentuais nem quantificadores numéricos por extenso; '
                  'use os campos numéricos tipados. Nível Inconclusivo e confiança baixa se sufficient_evidence=false. '
                  'Priorize fundamentos, vetores, ordenação, prefixos, busca, grafos e DP introdutória. '
                  'Não inclua competências fora dos IDs oferecidos. Evidências limitadas, sem inferir causas de erros. '
                  'Responda JSON em português.')
        curriculum = [{'topic_id': t['id'], 'title': t['title']} for t in load_curriculum()]
        prompt = encoded(dict(snapshot, curriculum=curriculum))
        generation = provider.generate(system, prompt, assessment_schema(snapshot))
        try:
            answer = validate_assessment(json.loads(generation.text), snapshot)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ResearchError('Avaliação recusada: JSON inválido.') from exc
        identifier = uuid.uuid4().hex
        payload = dict(version=VERSION, evidence_hash=key, snapshot=snapshot, assessment=answer,
                       model=generation.model_version, requested_model=model, usage=generation.usage,
                       request_id=generation.request_id, seconds=generation.elapsed_seconds,
                       synthetic=synthetic, status='pending', teacher_comment='', reviews=[],
                       limitations='Proposta de IA, sem nota definitiva. Interpretações qualitativas dependem de revisão docente.')
        with self.store.connect() as db:
            db.execute('INSERT INTO learner_assessments VALUES (?,?,?,?,?,?)', (identifier, class_id, student_id, key, encoded(payload), self.store.now()))
        return dict(self.get(viewer_id, identifier), cached=False)

    def review(self, teacher_id, assessment_id, decision, comment):
        assessment = self.get(teacher_id, assessment_id)
        with self.store.connect() as db:
            row = db.execute('SELECT classroom_id,student_id FROM learner_assessments WHERE id=?', (assessment_id,)).fetchone()
        self._authorize(teacher_id, *row, teacher_only=True)
        if decision not in DECISIONS or not isinstance(comment, str) or not 1 <= len(comment.strip()) <= 2000:
            raise ValueError('Escolha aprovar, pedir revisão ou rejeitar e escreva comentário de até 2000 caracteres.')
        if decision == 'approved' and assessment['stale']:
            raise ValueError('As evidências mudaram. Gere nova avaliação antes de aprovar.')
        now = self.store.now()
        # Preserve every review independently; changing status never rewrites the model's proposal.
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            student = self.accounts.user(row[1])
            current = db.execute('SELECT payload FROM profiles WHERE id=?', (student['profile_id'],)).fetchone()
            current_snapshot = evidence_snapshot(json.loads(current[0]) if current else {})
            current_hash = hashlib.sha256(encoded(current_snapshot).encode()).hexdigest()
            if decision == 'approved' and current_hash != assessment['evidence_hash']:
                raise ValueError('As evidências mudaram. Gere nova avaliação antes de aprovar.')
            db.execute('INSERT INTO learner_assessment_reviews VALUES (?,?,?,?,?,?)', (uuid.uuid4().hex, assessment_id, teacher_id, decision, comment.strip(), now))
            payload = json.loads(db.execute('SELECT payload FROM learner_assessments WHERE id=?', (assessment_id,)).fetchone()[0])
            payload.update(status=decision, teacher_comment=comment.strip())
            payload['reviews'].append(dict(teacher_id=teacher_id, decision=decision, comment=comment.strip(), created_at=now))
            db.execute('UPDATE learner_assessments SET payload=? WHERE id=?', (encoded(payload), assessment_id))
        return self.get(teacher_id, assessment_id)
