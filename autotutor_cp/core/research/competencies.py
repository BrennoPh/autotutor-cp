"""Editorial competency graph and interpretable, uncalibrated BKT prototype."""
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
import json,math

@lru_cache(maxsize=1)
def graph():
    result=json.loads((Path(__file__).resolve().parents[2]/'data/research/competencies.json').read_text())
    by_id={n['id']:n for n in result['nodes']}
    def visit(identifier,path):
        if identifier in path:raise ValueError('Ciclo no grafo de competências.')
        if identifier not in by_id:raise ValueError('Pré-requisito inexistente.')
        for prior in by_id[identifier]['prerequisites']:visit(prior,path|{identifier})
    for identifier in by_id:visit(identifier,set())
    return result

def specification(target,difficulty='Intermediário',pedagogical_type='introdutório'):
    from core.problem_bank import load_problems
    g=graph();mapping=g['targets'].get(target)
    if not mapping:raise ValueError('Competência-alvo não cadastrada.')
    seed=next(p for p in load_problems() if p['id']==mapping['contract_id'])
    by_id={n['id']:n for n in g['nodes']};prereqs=sorted({p for c in mapping['competencies'] for p in by_id[c]['prerequisites']})
    return {'schema_version':'research.problem.v1','target':target,'topic':mapping['topic'],'contract_id':seed['id'],
        'target_competencies':mapping['competencies'],'prerequisites':prereqs,'difficulty':difficulty,'pedagogical_type':pedagogical_type,
        'learning_objective':'Aplicar e justificar '+by_id[mapping['competencies'][0]]['title'],
        'contract':{'objective':seed['math_essence'],'statement':seed['statement'],'constraints':seed['constraints'],'time_limit_sec':seed['time_limit_sec'],'memory_limit_mb':seed['memory_limit_mb']}}

@dataclass(frozen=True)
class BKTParameters:
    prior:float=.2
    learn:float=.15
    guess:float=.2
    slip:float=.1
    def __post_init__(self):
        if any(not math.isfinite(x) or not 0<x<1 for x in (self.prior,self.learn,self.guess,self.slip)):raise ValueError('Parâmetros BKT precisam estar entre zero e um.')

def knowledge_state(events,parameters=None):
    """Latest outcome per item avoids multiplying evidence from repeated submissions.

    Outcomes are observed performance, never proof of a cognitive diagnosis.
    Parameters are hypothetical; only synthetic profiles are used in the pilot.
    """
    p=parameters or BKTParameters();valid={n['id'] for n in graph()['nodes']};latest={}
    for event in events:
        if event.get('competency') not in valid or not isinstance(event.get('item_id'),str) or not event['item_id'] or type(event.get('correct')) is not bool:raise ValueError('Evidência inválida.')
        latest[(event['competency'],event['item_id'])]=event
    states={c:{'probability':p.prior,'distinct_items':0} for c in valid}
    for event in latest.values():
        state=states[event['competency']];prior=state['probability']
        likelihood=1-p.slip if event['correct'] else p.slip
        other=p.guess if event['correct'] else 1-p.guess
        posterior=prior*likelihood/(prior*likelihood+(1-prior)*other)
        state['probability']=posterior+(1-posterior)*p.learn;state['distinct_items']+=1
    for state in states.values():
        state['status']='evidência insuficiente' if state['distinct_items']<3 else 'estimativa experimental, sem diagnóstico validado'
    return {'model':'BKT editorial, não calibrado','parameters':p.__dict__,'states':states,'scope':'Desempenho e probabilidade hipotética, não certificação de domínio.'}

def probable_gaps(events):
    result=knowledge_state(events)
    result['support_candidates']=sorted([c for c,s in result['states'].items() if s['distinct_items']>=3 and s['probability']<.6],key=lambda c:result['states'][c]['probability'])
    return result
