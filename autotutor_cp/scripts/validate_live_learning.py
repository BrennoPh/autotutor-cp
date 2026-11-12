"""Opt-in real API student scenarios, public synthetic data, shared free-only provider.

No call is made without --live. Stops immediately on provider/quota errors. A
scripted professor is a workflow test, never a human pedagogical reviewer.
"""
import argparse,json,tempfile,time,sys,secrets
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.accounts import Accounts,AccessError
from core.classrooms import Classrooms
from core.progress_store import ProgressStore
from core.learner_assessment import LearnerAssessmentService
from core.learning_engine import questions_for,grade_answers
from core.research.provider import ResearchConfig,configured_provider,BudgetLedger,ResearchError
from core.research.pipeline import ResearchPipeline,save_run
from core.research.lessons import generate_lesson,CASES,LessonValidationError

SCENARIOS=[('Soma de prefixos','Quero aprender a somar intervalos com prefixos, sem erros de índice.'),
           ('BFS','Quero aprender BFS com fila e distâncias em grafos sem pesos.'),
           ('DP','Quero entender estados e transições de DP em problemas iniciais.'),
           ('Fundamentos e simulação','Quero resolver um problema Ad Hoc contando repetições consecutivas.')]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--live',action='store_true');parser.add_argument('--output',type=Path,default=Path('.runtime/live_student_agents'));parser.add_argument('--topics',nargs='+',choices=list(CASES),default=list(CASES))
    args=parser.parse_args()
    if not args.live:
        print('Plano: quatro agentes de aluno pedem estudo e problema; duas avaliações formativas e pareceres simulados. Use --live para chamadas reais à cota gratuita.');return 0
    config=ResearchConfig.from_env();provider=configured_provider(config)
    folder=args.output/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');folder.mkdir(parents=True,exist_ok=False)
    report={'synthetic':True,'mode':'real_gemini_api','human_review':False,'configuration':config.public(),'scenarios':[],
            'limitations':'Testes finitos e revisão simulada. Não demonstra aprendizagem nem acurácia geral; teoria e justificativas precisam de revisão independente.'}
    def save():
        report['ledger']=BudgetLedger().report();(folder/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    def wait_interval():
        operations=BudgetLedger().report()['operations']
        if operations:
            last=datetime.fromisoformat(operations[-1]['started_utc']).timestamp()
            delay=max(0,config.min_interval-(time.time()-last)+.2)
            if delay:time.sleep(delay)
    with tempfile.TemporaryDirectory(prefix='autotutor-live-synthetic-') as temp:
        store=ProgressStore(Path(temp)/'actors.sqlite3');accounts=Accounts(store);school=Classrooms(store,accounts)
        teacher=accounts.register('synthetic_teacher','Professor simulado',secrets.token_urlsafe(20),'teacher')
        class_id=school.create(teacher,'Validação sintética - fundamentos');code=school._class(teacher,class_id)['invite_code'];students=[]
        for i in range(5):
            uid=accounts.register(f'synthetic_student_{i}',f'Aluno sintético {i}',secrets.token_urlsafe(20));school.join(uid,code);students.append(uid)
        try:
            for index,(target,request) in enumerate([s for s in SCENARIOS if s[0] in args.topics]):
                uid=students[index];profile=accounts.user(uid)['profile_id'];row={'actor':f'learner_{index}','target':target,'request':request,'checks':{}}
                report['scenarios'].append(row);wait_interval()
                try:
                    lesson=generate_lesson(provider,target,request)
                    material_id=store.add_artifact(profile,'material',lesson['title'],lesson)
                    (folder/f'lesson_{index}.json').write_text(json.dumps(lesson,ensure_ascii=False,indent=2))
                    row['checks']['lesson_fixed_example']=lesson['validation']['numerical_example_valid']
                    row['checks']['material_saved']=any(x['id']==material_id for x in store.artifacts(profile,kind='material'))
                    row['checks']['material_private']=not any(x['id']==material_id for x in store.artifacts(accounts.user(students[-1])['profile_id'],kind='material'))
                    print(target+': estudo recebido, exemplo conferido.',flush=True)
                except LessonValidationError as exc:
                    row['checks']['lesson_fixed_example']=False;row['lesson_failure']=str(exc)
                    (folder/f'lesson_{index}_rejected.json').write_text(json.dumps(exc.record,ensure_ascii=False,indent=2))
                    print(target+': estudo recusado, não publicado.',flush=True)
                save();wait_interval()
                run,problem=ResearchPipeline(provider).run(target,'structured',learning_request=request+' Gere uma questão sobre esse mesmo assunto.')
                run['execution_mode']='real_gemini_api_synthetic_learner';path=save_run(run,problem,folder/'problems')
                row['problem_run']=str(path.relative_to(folder));row['checks']['problem_validated']=run['validated']
                row['checks']['requested_topic_preserved']=bool(problem and problem['requested_concept']==target)
                if not problem:
                    row['failure']=run.get('error') or run['attempts'][-1]['validation'].get('error');save()
                    if run.get('error'):break
                    continue
                store.add_artifact(profile,'problem',problem['title'],problem)
                qs=questions_for('diagnostic');attempt=grade_answers({q['id']:(q['answer'] if j%2 else (q['answer']+1)%len(q['options'])) for j,q in enumerate(qs)})
                store.save(profile,{'quiz_attempts':[attempt],'history':[{'problem_id':problem['id'],'topic':problem['topic'],'verdict':'AC'}]})
                row['total_cases']=run['attempts'][-1]['validation']['total_cases'];save();print(target+': problema verificado.',flush=True)
            else:
                service=LearnerAssessmentService(store,accounts,school,provider)
                report['assessments']=[]
                for actor,uid in [('empty_learner',students[-1]),('mixed_evidence_learner',students[0])]:
                    wait_interval();assessment=service.generate(uid,class_id,uid,synthetic=True)
                    preserved=assessment['assessment'];repeat=service.generate(uid,class_id,uid,synthetic=True)
                    decision='approved' if actor=='empty_learner' else 'revision_requested'
                    reviewed=service.review(teacher,assessment['id'],decision,'[SIMULAÇÃO] Fluxo conferido por roteiro automatizado. Não constitui parecer de professor humano.')
                    unauthorized=False
                    try:service.get(students[1],assessment['id'])
                    except AccessError:unauthorized=True
                    report['assessments'].append({'actor':actor,'result':assessment,'scripted_teacher_review':reviewed,
                        'checks':{'cache_reused':repeat['cached'],'proposal_preserved':reviewed['assessment']==preserved,'other_student_denied':unauthorized,
                                  'empty_inconclusive':actor!='empty_learner' or preserved['level']=='Inconclusivo'}})
                    print(actor+': avaliação e revisão simulada registradas.',flush=True);save()
        except ResearchError as exc:
            report['stopped_reason']=str(exc);print('Validação interrompida: '+str(exc),flush=True)
        finally:
            report['synthetic_database_destroyed_on_exit']=True;save()
    print('Relatório: '+str(folder/'report.json'),flush=True)
    return int(bool(report.get('stopped_reason')))

if __name__=='__main__':raise SystemExit(main())
