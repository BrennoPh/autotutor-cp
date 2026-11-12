"""Explicit opt-in evaluation using synthetic data only. Does not train the model."""
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.llm_client import LLMClient,AIUnavailable
from core.codigen_tutor import CodigenTutor
from core.ai_coach import learner_evidence,analyze_learner,propose_teams,analyze_class
from core.learning_engine import questions_for,grade_answers
from core.rag_retriever import OIAssistantRAG
from core.problem_bank import load_problems


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--tasks',nargs='+')
    args=parser.parse_args()
    audit=[];llm=LLMClient('Ollama',model='qwen2.5:3b',require_model=True,audit_callback=audit.append);checks=[]
    def run(name,fn):
        if args.tasks and name not in args.tasks:return
        start=time.perf_counter();llm.events.clear();audit.clear()
        try:result=fn();error=None
        except Exception as exc:result=None;error=str(exc)
        checks.append(dict(task=name,seconds=round(time.perf_counter()-start,2),result=result,error=error,events=list(llm.events),raw_responses=[a.get('response') for a in audit]))
        print(json.dumps(checks[-1],ensure_ascii=False),flush=True)
        Path('.runtime').mkdir(exist_ok=True)
        Path('.runtime/qwen-evaluation.json').write_text(json.dumps(dict(model=llm.model,synthetic_inputs=True,checks=checks),ensure_ascii=False,indent=2))
    run('connection',llm.test_connection)
    run('prefix_explanation',lambda:CodigenTutor(llm).generate_material('Explicação','Prefix Sum','Iniciante','',
        learning_request='Use índices começando em 1. Em [2,4,1], explique por que a soma do intervalo [2,3] é 5 e por que usar P[R]-P[L] estaria errado. Mostre os valores de P.',
        length='Curto',depth='Passo a passo',include_examples=True,include_exercises=False))
    run('false_premise',lambda:llm.complete('Você ensina algoritmos em português. Corrija premissas erradas e justifique com um exemplo numérico, em até 130 palavras.',
        'Como a soma de [2,3] no vetor [2,4,1] é 7, posso usar P[3]-P[2], certo? Os índices começam em 1.'))
    qs=questions_for('diagnostic');answers={q['id']:(q['answer'] if q['topic'] in ('fundamentals','structures','prefix') else (q['answer']+1)%len(q['options'])) for q in qs}
    evidence=learner_evidence([grade_answers(answers)],[{'topic':'Prefix Sum','problem_id':'synthetic','verdict':'WA'}],[],3)
    run('learner_analysis',lambda:analyze_learner(llm,evidence))
    roster=[dict(id=str(i),name='Sintético '+str(i),local_solved=['p'+str(i)] if i<3 else [],external_solved=[],verified_external=[],quiz_correct=i,quiz_answered=4,submissions=i+1,
                 topic_statistics=[dict(id='prefix' if i%2 else 'graph',correct=i,answered=4,accepted_problems=int(i<3),distinct_problems=1,compile_errors=0,submissions=i+1)]) for i in range(4)]
    run('class_analysis',lambda:analyze_class(llm,roster))
    run('team_proposal',lambda:propose_teams(llm,roster,'Complementaridade','Turma inteira'))
    run('rag_recommendations',lambda:[dict(id=x['problem']['id'],reason=x['reason']) for x in OIAssistantRAG(load_problems(),llm).retrieve('Soma em intervalos de vetor imutável usando prefixos')])
    Path('.runtime').mkdir(exist_ok=True)
    Path('.runtime/qwen-evaluation.json').write_text(json.dumps(dict(model=llm.model,synthetic_inputs=True,scope='Execução, formatos e amostras para revisão humana; não certifica qualidade pedagógica.',checks=checks),ensure_ascii=False,indent=2))
    return int(any(c['error'] for c in checks))

if __name__=='__main__':raise SystemExit(main())
