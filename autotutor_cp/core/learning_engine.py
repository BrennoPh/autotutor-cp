"""Question grading, prerequisite-aware planning and transparent learner statistics."""
from collections import Counter
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import json
from zoneinfo import ZoneInfo

CONTENT = Path(__file__).resolve().parents[1] / 'data' / 'learning_content.json'
PROBLEM_TOPICS = {'dp':'dp','prefix':'prefix','binary':'binary','greedy':'greedy','graph':'graph','tree':'tree'}


@lru_cache(maxsize=1)
def load_curriculum():
    return json.loads(CONTENT.read_text(encoding='utf-8'))['topics']


def question_bank():
    return {q['id']:dict(q, topic=t['id']) for t in load_curriculum() for q in t['questions']}


def questions_for(kind, topic_id=None):
    return [dict(q, topic=t['id']) for t in load_curriculum() if topic_id is None or t['id'] == topic_id
            for q in t['questions'] if q['kind'] == kind]


def grade_answers(answers, kind='diagnostic', topic_id=None):
    if kind not in ('diagnostic','review'):
        raise ValueError('Tipo de questionário inválido.')
    if kind == 'review' and topic_id not in {t['id'] for t in load_curriculum()}:
        raise ValueError('Selecione um módulo válido para a revisão.')
    questions = questions_for(kind, topic_id)
    if not questions or set(answers) != {q['id'] for q in questions}:
        raise ValueError('Responda todas as perguntas antes de concluir o questionário.')
    details = []
    for q in questions:
        answer = answers[q['id']]
        if type(answer) is not int or not 0 <= answer < len(q['options']):
            raise ValueError('Escolha uma alternativa para cada pergunta.')
        details.append({'question_id':q['id'],'topic':q['topic'],'selected':answer,
                        'correct':answer == q['answer']})
    return {'kind':kind,'topic_id':topic_id,'time':datetime.now(ZoneInfo('America/Maceio')).isoformat(timespec='seconds'),
            'answers':details,'correct':sum(a['correct'] for a in details),'total':len(details)}


def learning_stats(attempts, history):
    """Each question and each problem contributes its latest outcome only."""
    bank = question_bank()
    latest = {}
    for attempt in attempts:
        for answer in attempt.get('answers', []):
            qid = answer.get('question_id')
            if qid in bank:
                # Recompute correctness; stored bools are never trusted when restoring data.
                latest[qid] = {'topic':bank[qid]['topic'], 'correct':answer.get('selected') == bank[qid]['answer']}
    latest_problems = {}
    for h in history:
        pid = h.get('problem_id') or h.get('problem')
        if pid:
            latest_problems[pid] = h
    result = []
    for topic in load_curriculum():
        answers = [a for a in latest.values() if a['topic'] == topic['id']]
        submissions = [h for h in history if h.get('topic') == topic['title']]
        distinct = [h for h in latest_problems.values() if h.get('topic') == topic['title']]
        correct = sum(a['correct'] for a in answers)
        accepted = sum(h.get('verdict') == 'AC' for h in distinct)
        result.append({'id':topic['id'],'title':topic['title'],'answered':len(answers),'correct':correct,
            'accuracy':correct / len(answers) if answers else None,
            'submissions':len(submissions),'distinct_problems':len(distinct),'accepted_problems':accepted,
            'acceptance':accepted / len(distinct) if distinct else None,
            'compile_errors':sum(h.get('verdict') == 'CE' for h in submissions)})
    return result


def estimate_level(attempts):
    diagnostic = next((a for a in reversed(attempts) if a.get('kind') == 'diagnostic'), None)
    if not diagnostic:
        return None
    bank = question_bank()
    answers = {a['question_id']:a['selected'] for a in diagnostic['answers'] if a['question_id'] in bank}
    total = len(answers)
    if total != len(questions_for('diagnostic')):
        return None
    correct = sum(answer == bank[qid]['answer'] for qid,answer in answers.items())
    foundation = [answer == bank[qid]['answer'] for qid,answer in answers.items() if bank[qid]['topic'] == 'fundamentals']
    score = correct / total
    if sum(foundation) / len(foundation) < .5 or score < .5:
        level = 'Iniciante'
    elif score < .8:
        level = 'Intermediário'
    else:
        level = 'Avançado'
    return {'level':level,'correct':correct,'total':total,'score':score}


def build_roadmap(attempts, history, completed):
    stats = {s['id']:s for s in learning_stats(attempts, history)}
    curriculum = load_curriculum()
    known = {tid for tid,s in stats.items() if (s['answered'] >= 2 and s['accuracy'] >= .75) or s['accepted_problems'] > 0}
    finished = set(completed)
    order = {t['id']:i for i,t in enumerate(curriculum)}
    remaining = {t['id']:t for t in curriculum}
    plan = []
    # Topological sorting, with weak/unknown ready topics ahead of optional reviews.
    while remaining:
        available = [t for t in remaining.values() if all(p not in remaining for p in t['prerequisites'])]
        if not available:
            raise ValueError('O currículo contém um ciclo de pré-requisitos.')
        available.sort(key=lambda t:(t['id'] in finished, t['id'] in known,
                                     stats[t['id']]['accuracy'] if stats[t['id']]['accuracy'] is not None else .5,
                                     order[t['id']]))
        topic = available[0]
        tid = topic['id']
        stat = stats[tid]
        gaps = [p for p in topic['prerequisites'] if p not in known and p not in finished]
        if tid in finished:
            status = 'Aula concluída'
            reason = 'Você marcou a leitura como concluída. Os questionários e a prática continuam sendo evidências separadas.'
        elif tid in known:
            status = 'Revisão sugerida'
            reason = 'Há acertos em questões ou uma solução aceita neste tópico. Use a revisão para conferir se consegue explicar o raciocínio.'
        elif gaps:
            status = 'Depois da base'
            reason = 'Comece pelos pré-requisitos: ' + ', '.join(next(t['title'] for t in curriculum if t['id'] == p) for p in gaps) + '.'
        elif stat['accuracy'] is not None and stat['accuracy'] < .6:
            status = 'Reforçar agora'
            reason = f'Você acertou {stat["correct"]} de {stat["answered"]} questões distintas deste assunto. Refaça o exemplo e a fixação.'
        else:
            status = 'Próximo assunto'
            reason = 'Ainda há pouca evidência sobre este conceito. Estude a aula, responda à fixação e pratique no juiz.'
        if stat['submissions'] and stat['accepted_problems'] == 0:
            reason += f' Há {stat["submissions"]} submissões neste tópico, ainda sem um problema aceito.'
        plan.append({'topic':topic,'stats':stat,'status':status,'reason':reason,'blocked_by':gaps})
        del remaining[tid]
    # Completed lessons remain visible at the end without affecting prerequisite reasoning.
    return [p for p in plan if p['topic']['id'] not in finished] + [p for p in plan if p['topic']['id'] in finished]


def next_step(attempts, history, completed):
    plan = build_roadmap(attempts, history, completed)
    candidates = [p for p in plan if p['status'] in ('Reforçar agora','Próximo assunto') and not p['blocked_by']]
    return candidates[0] if candidates else next((p for p in plan if p['status'] != 'Aula concluída'), None)


def verdict_counts(history):
    counts = Counter(h['verdict'] for h in history)
    return [{'Veredito':v,'Submissões':counts[v]} for v in ('AC','WA','TLE','RE','CE') if counts[v]]


def lesson_markdown(topic):
    text = f'# {topic["title"]}\n\n{topic["summary"]}\n\n## Objetivos\n'
    text += '\n'.join('- ' + item for item in topic['objectives']) + '\n\n'
    for section in topic['sections']:
        text += f'## {section["title"]}\n\n{section["body"]}\n\n'
    example = topic['example']
    text += f'## Exemplo passo a passo\n\n{example["story"]}\n\n'
    text += '\n'.join(f'{i}. {value}' for i,value in enumerate(example['trace'],1))
    text += '\n\n```cpp\n' + example['code'] + '\n```\n\n## Erros frequentes\n'
    text += '\n'.join('- ' + value for value in topic['pitfalls'])
    text += '\n\n## Prática\n\n' + topic['challenge'] + '\n\n## Vídeos complementares\n'
    text += '\n'.join(f'- [{v["title"]}]({v["url"]}) — {v["publisher"]}' for v in topic['videos'])
    return text

