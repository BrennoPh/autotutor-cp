"""Formative model proposals remain numeric-faithful, private and reviewable."""
import json
from copy import deepcopy
import pytest
from core.accounts import Accounts, AccessError
from core.classrooms import Classrooms
from core.progress_store import ProgressStore
from core.learning_engine import question_bank
from core.learner_assessment import (LearnerAssessmentService, evidence_snapshot,
                                     validate_assessment, ResearchError)
from core.research.provider import Generation


class FixtureProvider:
    model = 'fixture-basic'
    def __init__(self): self.calls = []
    def generate(self, system, prompt, schema):
        self.calls.append((system, prompt, schema))
        return Generation(json.dumps(answer(json.loads(prompt))), {'totalTokenCount': 10}, self.model, .01, 'fixture-request')


def answer(snapshot):
    topic = snapshot['topics'][0]
    return dict(level='Inconclusivo' if not snapshot['sufficient_evidence'] else 'Iniciante', confidence='baixa',
                summary='Evidências limitadas exigem acompanhamento docente.',
                observations=[dict(evidence_id=topic['evidence_id'], metric='answered', value=topic['answered'],
                                   interpretation='Revisar a base e observar o raciocínio.')],
                next_steps=[dict(topic_id=topic['topic_id'], evidence_ids=[topic['evidence_id']],
                                 action='Estudar vetores e praticar simulação.')])


@pytest.fixture
def classroom(tmp_path):
    store = ProgressStore(tmp_path/'test.sqlite3'); accounts = Accounts(store); classes = Classrooms(store, accounts)
    teacher = accounts.register('professor', 'Professor Privado', 'password1', 'teacher')
    other = accounts.register('outro_prof', 'Outro Professor', 'password1', 'teacher')
    alice = accounts.register('alice', 'ALICE_SECRET', 'password1')
    bob = accounts.register('bob', 'BOB_SECRET', 'password1')
    class_id = classes.create(teacher, 'Turma Privada')
    invite = classes._class(teacher, class_id)['invite_code']
    classes.join(alice, invite); classes.join(bob, invite)
    provider = FixtureProvider()
    service = LearnerAssessmentService(store, accounts, classes, provider)
    return store, accounts, classes, service, provider, teacher, other, alice, bob, class_id


def test_anonymous_stats_recompute_correctness_and_deduplicate():
    qid, question = next(iter(question_bank().items()))
    state = {'quiz_attempts': [{'answers': [{'question_id': qid, 'selected': question['answer'], 'correct': False}]}]*3,
             'history': [{'problem_id': 'private-problem', 'topic': 'PRIVATE_FREE_TEXT', 'verdict': 'AC', 'code': 'PRIVATE_CODE'}],
             'completed_lessons': ['PRIVATE_LESSON']}
    snap = evidence_snapshot(state)
    assert sum(t['answered'] for t in snap['topics']) == 1
    assert sum(t['correct'] for t in snap['topics']) == 1
    assert 'PRIVATE' not in json.dumps(snap)
    assert not snap['sufficient_evidence']


@pytest.mark.parametrize('mutation', ['fake_count', 'unknown_id', 'unknown_competency', 'unfounded_level', 'untyped_numeric_claim'])
def test_bad_model_proposals_rejected(mutation):
    snap = evidence_snapshot({}); proposed = answer(snap)
    if mutation == 'fake_count': proposed['observations'][0]['value'] = 99
    if mutation == 'unknown_id': proposed['observations'][0]['evidence_id'] = 'foreign'
    if mutation == 'unknown_competency': proposed['next_steps'][0]['topic_id'] = 'BlockCutTree'
    if mutation == 'unfounded_level': proposed['level'] = 'Iniciante'
    if mutation == 'untyped_numeric_claim': proposed['summary'] = 'Você acertou 99 questões.'
    with pytest.raises(ResearchError): validate_assessment(proposed, snap)


def test_explicit_data_authorization_no_request_without_it(classroom):
    _, _, _, service, provider, teacher, _, alice, _, cid = classroom
    with pytest.raises(ResearchError): service.generate(teacher, cid, alice)
    assert not provider.calls


def test_persistence_cache_and_no_identifiers_sent(classroom):
    store, accounts, classes, service, provider, teacher, _, alice, _, cid = classroom
    first = service.generate(teacher, cid, alice, synthetic=True)
    assert first['status'] == 'pending' and first['usage']['totalTokenCount'] == 10
    text = provider.calls[0][1]
    for secret in ('ALICE_SECRET', alice, accounts.user(alice)['profile_id'], cid, teacher): assert secret not in text
    reopened = LearnerAssessmentService(ProgressStore(store.path), accounts, classes, provider)
    second = reopened.generate(teacher, cid, alice, synthetic=True)
    assert second['id'] == first['id'] and second['cached']
    assert len(provider.calls) == 1


def test_only_student_itself_or_owner_can_access_and_review(classroom):
    _, _, _, service, _, teacher, other, alice, bob, cid = classroom
    assessment = service.generate(teacher, cid, alice, synthetic=True)
    assert service.get(alice, assessment['id'])['id'] == assessment['id']
    for viewer in (other, bob):
        with pytest.raises(AccessError): service.get(viewer, assessment['id'])
        with pytest.raises(AccessError): service.generate(viewer, cid, alice, synthetic=True)
    with pytest.raises(AccessError): service.review(alice, assessment['id'], 'approved', 'Comentário')
    assert service.review(teacher, assessment['id'], 'revision_requested', 'Explique melhor as limitações.')['status'] == 'revision_requested'
    approved = service.review(teacher, assessment['id'], 'approved', 'Revisado para acompanhamento, sem nota.')
    assert approved['status'] == 'approved' and len(approved['reviews']) == 2
    assert approved['assessment'] == assessment['assessment']


def test_changed_evidence_invalidates_cache_and_prevents_stale_approval(classroom):
    store, accounts, _, service, provider, teacher, _, alice, _, cid = classroom
    first = service.generate(teacher, cid, alice, synthetic=True)
    qid, question = next(iter(question_bank().items()))
    store.save(accounts.user(alice)['profile_id'], {'quiz_attempts': [{'answers': [{'question_id': qid, 'selected': question['answer']}]}]})
    assert service.get(alice, first['id'])['stale']
    with pytest.raises(ValueError): service.review(teacher, first['id'], 'approved', 'Aprovar')
    second = service.generate(teacher, cid, alice, synthetic=True)
    assert second['id'] != first['id'] and len(provider.calls) == 2


def test_rejected_result_not_reused(classroom):
    _, _, _, service, provider, teacher, _, alice, _, cid = classroom
    first = service.generate(teacher, cid, alice, synthetic=True)
    service.review(teacher, first['id'], 'rejected', 'Conteúdo inadequado à observação.')
    next_result = service.generate(teacher, cid, alice, synthetic=True)
    assert first['id'] != next_result['id'] and len(provider.calls) == 2


@pytest.mark.parametrize('text', ['Acertou vinte por cento.', 'Resolveu duzentos problemas.'])
def test_spelled_out_numeric_claims_rejected(text):
    snapshot = evidence_snapshot({}); proposed = answer(snapshot)
    proposed['summary'] = text
    with pytest.raises(ResearchError): validate_assessment(proposed, snapshot)


def test_legitimate_indefinite_article_allowed():
    snapshot = evidence_snapshot({}); proposed = answer(snapshot)
    proposed['summary'] = 'Faça uma revisão de fundamentos.'
    assert validate_assessment(proposed, snapshot) == proposed
