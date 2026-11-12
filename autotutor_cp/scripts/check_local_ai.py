"""Opt-in smoke test with synthetic prompts; never reads the user's profiles."""
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.llm_client import LLMClient
from core.codigen_tutor import CodigenTutor
from core.rag_retriever import OIAssistantRAG
from core.problem_bank import load_problems


def main():
    audit=[];llm=LLMClient('Ollama',audit_callback=audit.append);results=[]
    def run(name,action):
        llm.events.clear();audit.clear();start=time.perf_counter();value=action()
        results.append({'task':name,'seconds':round(time.perf_counter()-start,2),'source':llm.last_source,
                        'error':llm.last_error,'events':list(llm.events),'responses':[r.get('response') for r in audit],'result':value})
    run('connection',llm.test_connection)
    run('structured_json',lambda:llm.complete('Responda somente com um objeto JSON.','Retorne {"sum":5,"language":"português"}.',True))
    run('short_material',lambda:CodigenTutor(llm).generate_material('Explicação','Prefix Sum','Iniciante','',
        learning_request='Explique por que a soma do intervalo [2,3] em [2,4,1] é 5 usando prefixos. Não forneça programa completo.',length='Curto',depth='Passo a passo',include_examples=True,include_exercises=False))
    def recommendations():
        items=OIAssistantRAG(load_problems(),llm).retrieve('Prefix Sum: somas de intervalos de um vetor fixo, prefixo[R] menos prefixo[L-1]')
        return [{'id':r['problem']['id'],'title':r['problem']['title'],'score':r['score'],'reason':r['reason']} for r in items]
    run('rag_recommendations',recommendations)
    print(json.dumps({'model':llm.model,'synthetic_inputs':True,'scope':'Verifica execução e formatos; não valida correção conceitual dos textos.','checks':results},ensure_ascii=False,indent=2))
    return int(any(r['error'] or any(e['source']=='local' for e in r['events']) for r in results))


if __name__=='__main__':raise SystemExit(main())
