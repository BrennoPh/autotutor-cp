"""Offline synthetic learner/teacher journeys; fixtures never measure LLM quality.

Run .venv/bin/python scripts/validate_student_agents.py --output .runtime/student_agents
Only a disposable temporary database is used. No external API or Ollama is called.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.accounts import Accounts, AccessError
from core.classrooms import Classrooms
from core.codigen_tutor import CodigenTutor
from core.isolated_judge import IsolatedMiniJudge, isolation_available
from core.learner_assessment import LearnerAssessmentService
from core.library import Library, study_entry
from core.learning_engine import question_bank
from core.practice_context import study_context, queue_practice
from core.progress_store import ProgressStore
from core.research.competencies import specification
from core.research.pipeline import ResearchPipeline, validate_problem
from core.research.provider import Generation, ResearchError
from core.study_pages import material as open_material
from scripts.run_research_pilot import OfflineFixture


SCENARIOS = (
    {'agent': 'aluna_prefixos', 'target': 'Soma de prefixos', 'concept': 'Prefix Sum',
     'request': 'Quero aprender soma de prefixos com o vetor [2, 4, 1] e uma questão iniciante.',
     'explanation': '# Soma de prefixos\nO prefixo vazio vale zero. Para [2, 4, 1], os prefixos são [0, 2, 6, 7]. A soma das posições 2 a 3 é 7 - 2 = 5. Construção O(n), consulta O(1), memória O(n).',
     'probe': {'prefixes': [0, 2, 6, 7], 'answer': 5}},
    {'agent': 'aluno_bfs', 'target': 'BFS', 'concept': 'Grafos',
     'request': 'Explique BFS em um caminho 0-1-2 e proponha uma questão de grafos básica.',
     'explanation': '# BFS\nEm um grafo não ponderado, uma fila explora distâncias em camadas. Marque ao enfileirar. No caminho 0-1-2, partindo de 0, as distâncias são [0, 1, 2]. Tempo O(V+E), memória O(V+E) com listas de adjacência.',
     'probe': {'distances': [0, 1, 2]}},
    {'agent': 'aluna_dp', 'target': 'DP', 'concept': 'DP',
     'request': 'Quero DP introdutória escolhendo valores não adjacentes de [2, 7, 9, 3, 1].',
     'explanation': '# DP introdutória\nUm estado resume a melhor soma de um prefixo sem escolher posições adjacentes. Compare ignorar o valor com escolhê-lo e usar o estado de duas posições antes. Para [2, 7, 9, 3, 1], a melhor soma é 12. Tempo O(n), memória O(1) guardando dois estados.',
     'probe': {'optimum': 12}},
    {'agent': 'aluno_simulacao', 'target': 'Fundamentos e simulação', 'concept': 'Matemática',
     'request': 'Explique simulação da sequência que divide pares por 2 e transforma ímpares em 3n+1, começando em 6.',
     'explanation': '# Simulação\nPartindo de 6, aplicar as regras até 1 produz [6, 3, 10, 5, 16, 8, 4, 2, 1]. Represente exatamente a regra e cuide do limite numérico. Não há aqui uma prova geral de término para qualquer inteiro positivo.',
     'probe': {'sequence': [6, 3, 10, 5, 16, 8, 4, 2, 1]}},
)


class MaterialFixture:
    """Transport fixture routes through the production material prompt builder."""
    provider = 'Gemini'
    require_model = True
    def __init__(self, text): self.text, self.prompts = text, []
    def complete(self, system, prompt, **kwargs):
        self.prompts.append(prompt)
        return self.text
    def report_fallback(self, message):
        raise AssertionError('Fixture unexpectedly rejected: ' + message)


class AssessmentFixture:
    """Numeric citations are filled from anonymized production snapshots."""
    model = 'offline-assessment-fixture'
    def __init__(self, invented=False): self.calls, self.invented = 0, invented
    def generate(self, system, prompt, schema=None):
        self.calls += 1
        snapshot = json.loads(prompt); topic = snapshot['topics'][0]
        value = {'level': 'Inconclusivo' if not snapshot['sufficient_evidence'] else 'Iniciante',
                 'confidence': 'baixa', 'summary': 'Evidências limitadas para acompanhamento docente.',
                 'observations': [{'evidence_id': topic['evidence_id'], 'metric': 'answered',
                                   'value': topic['answered'] + (99 if self.invented else 0),
                                   'interpretation': 'Recomenda-se revisar fundamentos.'}],
                 'next_steps': [{'topic_id': topic['topic_id'], 'evidence_ids': [topic['evidence_id']],
                                 'action': 'Revisar vetores e praticar simulação.'}]}
        return Generation(json.dumps(value, ensure_ascii=False), {}, self.model, 0, 'synthetic-assessment')


def numeric_probe_correct(target, probe):
    """Independent tiny reference computations, not a general prose verifier."""
    if target == 'Soma de prefixos':
        prefix = [0]
        for value in [2, 4, 1]: prefix.append(prefix[-1] + value)
        return probe == {'prefixes': prefix, 'answer': sum([4, 1])}
    if target == 'BFS':
        from collections import deque
        graph = [[1], [0, 2], [1]]; distances = [-1] * 3; distances[0] = 0
        queue = deque([0])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph[vertex]:
                if distances[neighbor] < 0:
                    distances[neighbor] = distances[vertex] + 1; queue.append(neighbor)
        return probe == {'distances': distances}
    if target == 'DP':
        values = [2, 7, 9, 3, 1]
        feasible = [sum(v for i, v in enumerate(values) if mask >> i & 1)
                    for mask in range(1 << len(values)) if not mask & (mask << 1)]
        return probe == {'optimum': max(feasible)}
    if target == 'Fundamentos e simulação':
        sequence = [6]
        while sequence[-1] != 1:
            value = sequence[-1]; sequence.append(value // 2 if value % 2 == 0 else 3 * value + 1)
        return probe == {'sequence': sequence}
    return False


def declared_topic_correct(value, target):
    """Exact explicit topic check; does not prove semantic/algorithmic alignment."""
    spec = specification(target)
    return value.get('topic') == spec['topic'] and value.get('contract_id') == spec['contract_id']


def run_simulation():
    report = {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
              'execution_mode': 'offline_fixture_agents', 'synthetic': True,
              'external_calls': 0, 'ollama_calls': 0, 'financial_cost_authorized': 0,
              'agents': [], 'checks': [], 'limitations': [
                  'Agentes são roteiros determinísticos; as respostas são fixtures conhecidas, não saídas novas de IA.',
                  'As verificações numéricas avaliam sondas pequenas explícitas, não toda a prosa nem qualidade pedagógica.',
                  'Testes finitos e contratos não provam correção geral, originalidade ou aprendizagem de estudantes.',
                  'Nenhum estudante real, histórico real ou banco de produção foi usado.']}
    def check(name, passed, detail=''):
        report['checks'].append({'name': name, 'passed': bool(passed), 'detail': detail})
    if not isolation_available():
        report['status'] = 'blocked'; report['error'] = 'Sandbox indisponível; não executar código no host.'
        return report
    with tempfile.TemporaryDirectory(prefix='autotutor-synthetic-agents-') as temporary:
        root = Path(temporary); store = ProgressStore(root/'simulation.sqlite3')
        accounts = Accounts(store); school = Classrooms(store, accounts); library = Library(store)
        teacher = accounts.register('professor_sintetico', 'Professor sintético', 'fixture-only-password', 'teacher')
        outsider = accounts.register('professor_externo', 'Professor externo sintético', 'fixture-only-password', 'teacher')
        classroom = school.create(teacher, 'Fundamentos — simulação isolada')
        code = school.list_for(teacher)[0]['invite_code']; students = []; first_material = None
        for scenario in SCENARIOS:
            uid = accounts.register(scenario['agent'], scenario['agent'], 'fixture-only-password')
            school.join(uid, code); profile = accounts.user(uid)['profile_id']; students.append((uid, profile))
            client = MaterialFixture(scenario['explanation'])
            with patch('core.knowledge.KnowledgeBase.context', return_value=('', [])), patch('core.library.references_for_query', return_value=[]):
                text = CodigenTutor(client).generate_material('Explicação', scenario['concept'], 'Iniciante', '',
                    learning_request=scenario['request'], length='Curto', depth='Visão geral')
            check(scenario['agent'] + ': pedido preservado no prompt', scenario['request'] in client.prompts[0])
            check(scenario['agent'] + ': exemplo numérico independente', numeric_probe_correct(scenario['target'], scenario['probe']))
            artifact = store.add_artifact(profile, 'material', scenario['target'],
                {'content': text, 'concept': scenario['concept'], 'learning_request': scenario['request'], 'source': 'Fixture sintética — não modelo'})
            first_material = first_material or (profile, artifact)
            entry = store.artifacts(profile, 'material')[0]; context = study_context(entry); state = {}; destinations = []
            queue_practice(state, context, destinations.append)
            check(scenario['agent'] + ': leitura encaminha objetivo para prática', state['pending_learning_request'] == scenario['request'] and destinations == ['Laboratório IA'])
            # Exercise the real generation/validation pipeline, replacing only model transport.
            pipeline = ResearchPipeline(OfflineFixture(scenario['target']), judge=IsolatedMiniJudge(root/'judge'))
            record, problem = pipeline.run(scenario['target'], 'direct', difficulty='Iniciante')
            check(scenario['agent'] + ': solução passa oráculo independente', problem is not None,
                  json.dumps(record['attempts'][0]['validation'], ensure_ascii=False))
            if problem:
                value = json.loads(record['attempts'][0]['response'])
                check(scenario['agent'] + ': tópico e contrato preservados', declared_topic_correct(value, scenario['target']))
                store.add_artifact(profile, 'problem', problem['title'], problem)
                public = study_entry(store.artifacts(profile, 'problem')[0])
                check(scenario['agent'] + ': biblioteca oculta solução de referência', problem['std_cpp'] not in str(public))
            check(scenario['agent'] + ': material salvo e reaberto', open_material(ProgressStore(store.path), profile, artifact) is not None)
            library.set_state(profile, artifact, 'Estudando', 'Revisão sintética')
            check(scenario['agent'] + ': biblioteca persiste estado', Library(ProgressStore(store.path)).get_state(profile, artifact)['status'] == 'Estudando')
            report['agents'].append({'name': scenario['agent'], 'role': 'student', 'target': scenario['target'],
                                     'request': scenario['request'], 'validated': bool(problem),
                                     'independent_cases': record['attempts'][0]['validation'].get('total_cases', 0),
                                     'source': 'offline fixture, not LLM output'})
        owner, artifact = first_material
        other_profile = students[-1][1]
        check('Material privado inacessível a outro aluno', open_material(store, other_profile, artifact) is None)
        try: library.set_state(other_profile, artifact, 'Estudado')
        except PermissionError: check('Outro aluno não altera biblioteca alheia', True)
        else: check('Outro aluno não altera biblioteca alheia', False)
        check('Professor vê somente os quatro membros sintéticos', len(school.roster(teacher, classroom)) == 4)
        try: school.roster(outsider, classroom)
        except AccessError: check('Professor externo bloqueado', True)
        else: check('Professor externo bloqueado', False)
        assessment_provider = AssessmentFixture()
        assessments = LearnerAssessmentService(store, accounts, school, provider=assessment_provider)
        proposals = []
        questions = list(question_bank().values())[:3]
        for index, (uid, profile) in enumerate(students):
            answers = [{'question_id': q['id'], 'selected': q['answer'] if index != 2 else (q['answer'] + 1) % len(q['options'])}
                       for q in questions[:(0, 1, 3, 2)[index]]]
            store.save(profile, {'quiz_attempts': [{'answers': answers}], 'history': []})
            proposal = assessments.generate(teacher, classroom, uid, synthetic=True)
            proposals.append(proposal)
            check(f'Avaliação do aluno sintético {index}: começa pendente', proposal['status'] == 'pending')
            again = assessments.generate(teacher, classroom, uid, synthetic=True)
            check(f'Avaliação do aluno sintético {index}: cache evita nova chamada', again['cached'] and again['id'] == proposal['id'])
            decision = ('approved', 'revision_requested', 'rejected', 'approved')[index]
            reviewed = assessments.review(teacher, proposal['id'], decision, 'Parecer docente sintético de teste.')
            check(f'Avaliação do aluno sintético {index}: parecer docente persistido',
                  assessments.get(uid, proposal['id'])['status'] == decision and len(reviewed['reviews']) == 1)
        check('Avaliação usa somente chamadas fixture explícitas', assessment_provider.calls == 4)
        try: assessments.review(students[0][0], proposals[0]['id'], 'approved', 'Tentativa sem permissão.')
        except AccessError: check('Aluno não aprova avaliação', True)
        else: check('Aluno não aprova avaliação', False)
        try: assessments.get(students[1][0], proposals[0]['id'])
        except AccessError: check('Aluno não lê avaliação alheia', True)
        else: check('Aluno não lê avaliação alheia', False)
        forged = LearnerAssessmentService(store, accounts, school, provider=AssessmentFixture(invented=True))
        # Force a fresh generation instead of returning the approved fixture cache.
        forged.provider.model = 'offline-forged-fixture'
        before = len(assessments.list_for(teacher, classroom, students[0][0]))
        try: forged.generate(teacher, classroom, students[0][0], synthetic=True)
        except ResearchError: check('Contagem inventada recusada pelo avaliador do produto', True)
        else: check('Contagem inventada recusada pelo avaliador do produto', False)
        check('Avaliação inválida não persistida', len(assessments.list_for(teacher, classroom, students[0][0])) == before)
        # Fault injection deliberately bypasses the fixture's normal correct values.
        fixture = OfflineFixture('Soma de prefixos')
        value = json.loads(fixture.generate('', '').text)
        changed = deepcopy(value); changed['topic'] = 'DP'
        validation, invalid_problem = validate_problem(changed, specification('Soma de prefixos'), IsolatedMiniJudge(root/'negative-topic'))
        check('Tópico declarado trocado rejeitado pelo validador do produto', invalid_problem is None and not validation['compiled'],
              'Igualdade de metadados; alinhamento semântico do enunciado ainda exige revisão.')
        changed = deepcopy(value); changed['target_competencies'] = ['dp_state']
        validation, invalid_problem = validate_problem(changed, specification('Soma de prefixos'), IsolatedMiniJudge(root/'negative-competencies'))
        check('Competências-alvo ausentes rejeitadas pelo validador do produto', invalid_problem is None and not validation['compiled'])
        changed = deepcopy(value); changed['examples'][0]['output'] = '999999999\n'
        validation, invalid_problem = validate_problem(changed, specification('Soma de prefixos'), IsolatedMiniJudge(root/'negative'))
        check('Exemplo errado rejeitado pelo validador do produto', invalid_problem is None and not validation['examples_valid'])
        check('Resultado numérico inventado detectado pela sonda', not numeric_probe_correct('DP', {'optimum': 99}), 'A sonda não valida texto livre.')
        check('Problema inválido não foi arquivado', all(len(store.artifacts(profile, 'problem')) == 1 for _, profile in students))
        report['agents'].append({'name': 'professor_sintetico', 'role': 'teacher', 'members': 4,
                                 'scope': 'Permissões e acesso a evidências; revisão pedagógica humana não simulada como resultado real.'})
    report['temporary_database_destroyed'] = True
    report['passed'] = sum(item['passed'] for item in report['checks'])
    report['total'] = len(report['checks']); report['status'] = 'passed' if report['passed'] == report['total'] else 'failed'
    return report


def save_report(report, output):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    (output/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Validação com agentes sintéticos', '',
             f"Resultado: {report['status']}. Verificações aprovadas: {report.get('passed', 0)}/{report.get('total', 0)}.", '',
             'Chamadas externas: 0. Chamadas ao Ollama: 0. Banco temporário, destruído ao terminar.', '',
             'Os agentes usam fixtures e roteiros explícitos. Isto verifica integração e barreiras técnicas; não mede qualidade de um modelo nem aprendizagem.', '']
    lines += [f"- {'PASSOU' if item['passed'] else 'FALHOU'}: {item['name']}" for item in report['checks']]
    lines += ['', '## Limitações', ''] + ['- '+item for item in report['limitations']]
    (output/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.runtime/student_agents'))
    args = parser.parse_args(); report = run_simulation(); save_report(report, args.output)
    print(json.dumps({key: report.get(key) for key in ('status', 'passed', 'total', 'external_calls')}, ensure_ascii=False))
    return 0 if report['status'] == 'passed' else 1

if __name__ == '__main__': raise SystemExit(main())
