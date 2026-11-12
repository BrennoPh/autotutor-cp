from unittest.mock import patch
import json
from core.knowledge import KnowledgeBase
from core.codigen_tutor import CodigenTutor
from core.llm_client import LLMClient
from core.autocode_engine import AutoCodeEngine
from core.problem_bank import load_problems
from core.mini_judge import MiniJudge
from scripts.import_study_links import academy_records,youtube_records


def doc(url,title,kind='article'):
    return dict(url=url,title=title,source='External' if url.startswith('https') else 'Local',license='Test',kind=kind,content=(title+' explanation. '+url+' ')*20)


def test_context_excludes_authored_lessons_and_metadata_without_full_text(tmp_path):
    kb=KnowledgeBase(tmp_path/'kb.db');kb.import_documents([doc('autotutor://aulas/dp','Dynamic programming'),doc('https://example.org/video','Dynamic programming','video_reference'),doc('https://example.org/dp','Dynamic programming')])
    context,refs=kb.context('DP',external_only=True)
    assert len(refs)==1 and refs[0]['url']=='https://example.org/dp'
    assert 'autotutor' not in context and 'example.org/video' not in context


def test_explicit_request_overrides_dropdown_and_only_actual_sources_are_attached(tmp_path,monkeypatch):
    path=tmp_path/'kb.db';monkeypatch.setenv('AUTOTUTOR_KNOWLEDGE_DB',str(path))
    KnowledgeBase(path).import_documents([doc('https://example.org/seg','Segment Tree'),doc('https://example.org/dp','Dynamic programming')])
    tutor=CodigenTutor(LLMClient('Gemini','key','test',require_model=True))
    with patch.object(tutor.llm,'complete',return_value='## Segment Tree\nUma estrutura para intervalos.') as call:
        text=tutor.generate_material('Explicação','DP','Iniciante','',learning_request='SegTree')
    assert tutor.last_retrieval[0]['url']=='https://example.org/seg'
    assert all(r['url']!='https://example.org/dp' for r in tutor.last_retrieval)
    assert call.call_args.kwargs['include_history'] is False
    assert 'Fontes recuperadas' in text


def test_no_evidence_is_disclosed_instead_of_citing_local_lessons():
    tutor=CodigenTutor(LLMClient('Gemini','key','test',require_model=True))
    with patch.object(tutor.llm,'complete',return_value='Explicação do modelo.'):
        text=tutor.generate_material('Explicação','DP','Iniciante','',learning_request='zzunknownzz')
    assert 'nenhum trecho externo' in text and tutor.last_retrieval==[]


def test_previous_contract_is_removed_before_ai_choice():
    llm=LLMClient('Gemini','key','test',require_model=True);engine=AutoCodeEngine(llm)
    with patch.object(llm,'complete',return_value={'seed_id':'dp','focus':'DP'}) as complete,patch.object(engine,'adapt_seed',return_value={'id':'new'}):
        engine.generate_problem(concept='DP',recent_problems=[{'seed_id':'prefix'}])
    payload=json.loads(complete.call_args.args[1].splitlines()[-1])
    assert len(payload['candidates'])==len(load_problems())-1
    assert not any(p['id']=='prefix' for p in payload['candidates'])
    assert any(p['id'].startswith('external_') for p in payload['candidates'])


def test_classic_contract_is_adapted_with_independent_oracle(tmp_path):
    seed=next(p for p in load_problems() if p.get('local_task')=='missing')
    answer={k:seed.get(k,'// Independent oracle is provided by the judge') for k in ('title','statement','std_cpp','brute_cpp')}
    llm=LLMClient('Gemini','key','test',require_model=True)
    with patch.object(llm,'complete',return_value=answer):result=AutoCodeEngine(llm,MiniJudge(tmp_path)).adapt_seed(seed)
    assert result['double_validated'] and result['local_task']=='missing'
    assert 'Python' in result['validation']['oracle']
    assert result['validation']['contract_seed_id']==seed['id']


def test_importers_extract_only_literal_public_metadata():
    script='var x={a:{problem_title:"Segment Tree",problem_url:"https://example.org/p",topics:["segment_tree"]}};'
    records=academy_records(script,'https://youkn0wwho.academy/topic-list')
    assert len(records)==1 and records[0]['kind']=='problem_reference'
    assert records[0]['title']=='Segment Tree' and 'segment tree' in records[0]['tags']
    assert youtube_records({'videoRenderer':{'videoId':'abcdefghijk','title':{'runs':[{'text':'Aula de BFS'}]}}},'https://youtube.com/channel')[0]['kind']=='video_reference'
