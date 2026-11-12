"""Small explicit opt-in experiment; default is offline with deterministic fixtures."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.research.provider import ResearchConfig,configured_provider,BudgetLedger,ResearchError,Generation
from core.research.pipeline import ResearchPipeline,save_run
from core.research.competencies import graph,specification
from core.research.retrieval import ResearchRetriever,ranking_metrics
from core.problem_bank import load_problems

class OfflineFixture:
    """Checks the integration with known references. Never reported as AI quality."""
    def __init__(self,target):self.target=target
    def generate(self,system,prompt,schema=None):
        spec=specification(self.target);seed=next(p for p in load_problems() if p['id']==spec['contract_id'])
        value={'title':seed['title'],'contract_id':seed['id'],'topic':seed['topic'],
            'statement':{'description':seed['math_essence'],'input':'Gramática do contrato original.','output':'Resultado do contrato original.','constraints':seed['statement']},
            'reference_solution':{'code_cpp':seed['std_cpp'],'explanation':seed['approach_summary'],'time_complexity':seed['complexity'],'space_complexity':'O(N)'},
            'examples':[{'input':x['input'],'output':x['expected_output']} for x in seed['examples']],
            'target_competencies':spec['target_competencies'],'prerequisites':spec['prerequisites'],'estimated_difficulty':'Intermediário',
            'learning_objective':spec['learning_objective'],'hints':['Identifique as operações.','Compare os casos mínimos.']}
        return Generation(json.dumps(value,ensure_ascii=False),{},'offline-fixture-not-a-model',0,'synthetic-fixture')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Enviar chamadas reais exclusivamente à cota gratuita declarada da API.')
    parser.add_argument('--local',action='store_true',help='Executar baseline Ollama explicitamente, sem API externa.')
    parser.add_argument('--retrieval-only',action='store_true')
    parser.add_argument('--target',choices=list(graph()['targets']),default='Soma de prefixos')
    parser.add_argument('--strategies',nargs='+',choices=('direct','examples','rag','structured','iterative','free_direct'),default=['direct','rag','structured'])
    parser.add_argument('--retrieval-method',choices=ResearchRetriever.METHODS,default='bm25')
    parser.add_argument('--output',type=Path,default=Path('.runtime/research/experiments'))
    args=parser.parse_args()
    if args.live and args.local:parser.error('Escolha API ou local, uma execução por vez.')
    args.output.mkdir(parents=True,exist_ok=True)
    if args.retrieval_only:
        retriever=ResearchRetriever();spec=specification(args.target);results=[]
        for method in ('bm25','semantic','hybrid','hybrid_rerank','hybrid_mmr','competencies'):
            try:
                _,refs=retriever.retrieve(args.target,method,competencies=spec['target_competencies'])
                results.append(dict(retriever.last_report,ranking_quality=ranking_metrics([x['id'] for x in refs],{})))
            except ResearchError as exc:results.append({'method':method,'error':str(exc)})
        (args.output/'retrieval.json').write_text(json.dumps({'target':args.target,'results':results,'human_labels':False},ensure_ascii=False,indent=2));print('Comparação de recuperação salva; métricas de relevância não calculadas sem rótulos.');return 0
    if args.live:provider=configured_provider();config=ResearchConfig.from_env()
    elif args.local:provider=configured_provider(ResearchConfig(provider='Ollama',model='llama3.2:1b'));config=None
    else:provider=OfflineFixture(args.target);config=None
    pipeline=ResearchPipeline(provider);summary=[]
    for strategy in args.strategies:
        record,problem=pipeline.run(args.target,strategy,args.retrieval_method,max_revisions=int(strategy=='iterative'))
        record['execution_mode']='api_free_tier' if args.live else 'local_model' if args.local else 'offline_fixture'
        if config:record['configuration']=config.public()
        folder=save_run(record,problem,args.output)
        summary.append({'run_id':record['run_id'],'strategy':strategy,'validated':record['validated'],'error':record.get('error'),
            'attempts':len(record['attempts']),'seconds':record['total_seconds'],'path':str(folder)})
        print(json.dumps(summary[-1],ensure_ascii=False),flush=True)
        if record.get('error'):break
        if args.live:time.sleep(config.min_interval)
    report={'execution_mode':'api_free_tier' if args.live else 'local_model' if args.local else 'offline_fixture','target':args.target,'runs':summary,
        'financial_policy':'Gasto autorizado zero; somente cota gratuita informada pelo usuário.',
        'limits':'Uma tarefa por estratégia, sem repetição estatística ou avaliação humana. Não demonstra superioridade nem aprendizagem.'}
    if args.live:report['ledger']=BudgetLedger().report()
    (args.output/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return int(any(x['error'] for x in summary))

if __name__=='__main__':raise SystemExit(main())
