from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock,patch
import json,math,subprocess
import pytest
from core.research.provider import ResearchConfig,Generation,BudgetLedger,BudgetExceeded,ResearchError,GeminiResearchProvider
from core.research.competencies import graph,specification,knowledge_state,probable_gaps
from core.research.retrieval import reciprocal_rank_fusion,diversify,ranking_metrics,ResearchRetriever
from core.research.pipeline import ResearchPipeline,validate_problem,save_run
from core.isolated_judge import IsolatedMiniJudge,isolation_available
from scripts.run_research_pilot import OfflineFixture

def config(**kwargs):return ResearchConfig(api_key='TEST_SECRET_NOT_A_REAL_KEY',min_interval=0,**kwargs)

def test_zero_cost_policy_and_secret_repr_and_official_endpoint():
    c=config();assert c.api_key not in repr(c) and c.api_key not in str(c.public())
    for kwargs in ({'max_cost_usd':.01},{'allow_paid':True},{'free_tier_only':False},{'base_url':'https://example.org'}):
        with pytest.raises(ValueError):config(**kwargs)

def test_atomic_reservations_survive_failures_and_restart(tmp_path):
    c=config(max_calls=1);path=tmp_path/'b.db';ledger=BudgetLedger(path)
    first=ledger.reserve(c,100);ledger.finish(first,'transport_error',{})
    with pytest.raises(BudgetExceeded):BudgetLedger(path).reserve(c,1)
    assert ledger.report()['reserved_usd']==0 and ledger.report()['calls']==1

@pytest.mark.parametrize('status',[400,401,403,429])
def test_provider_never_retries_quota_or_auth_or_request_errors(tmp_path,status):
    c=config(max_attempts=2);ledger=BudgetLedger(tmp_path/'b.db');transport=Mock()
    transport.post.return_value=SimpleNamespace(status_code=status,json=lambda:{'error':{'message':c.api_key+' refused'}})
    client=GeminiResearchProvider(c,ledger,transport)
    with pytest.raises(ResearchError) as error:client.generate('synthetic','synthetic')
    assert c.api_key not in str(error.value) and c.api_key not in str(ledger.report())
    with pytest.raises(BudgetExceeded):client.generate('synthetic','synthetic')
    assert transport.post.call_count==1

def test_provider_usage_schema_and_no_hidden_retries(tmp_path):
    c=config();ledger=BudgetLedger(tmp_path/'b.db');transport=Mock()
    transport.post.return_value=SimpleNamespace(status_code=200,json=lambda:{'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'{"ok":true}'}]}}],'modelVersion':c.model,'usageMetadata':{'totalTokenCount':12}})
    result=GeminiResearchProvider(c,ledger,transport).generate('s','p',{'type':'object'})
    assert result.usage['totalTokenCount']==12 and json.loads(result.text)['ok']
    request=transport.post.call_args.kwargs
    assert request['headers']['x-goog-api-key']==c.api_key and request['allow_redirects'] is False
    assert request['json']['generationConfig']['maxOutputTokens']==4096
    assert request['json']['generationConfig']['responseJsonSchema']=={'type':'object'}

def test_input_cap_prevents_request_without_reserving_budget(tmp_path):
    c=config(max_input_bytes=1000);ledger=BudgetLedger(tmp_path/'b.db');transport=Mock()
    with pytest.raises(BudgetExceeded):GeminiResearchProvider(c,ledger,transport).generate('s','a'*2000)
    assert not transport.post.called and ledger.report()['calls']==0

def test_competency_graph_and_bkt_do_not_diagnose_one_failure():
    assert 'segment_tree' in {x['id'] for x in graph()['nodes']}
    assert specification('Segment Tree')['contract_id']=='extended_range_sum'
    event={'competency':'segment_tree','item_id':'p1','correct':False}
    one=knowledge_state([event]);many=knowledge_state([event]*20)
    assert one['states']==many['states']
    assert one['states']['segment_tree']['status']=='evidência insuficiente'
    assert not probable_gaps([event])['support_candidates']
    events=[dict(event,item_id='p'+str(i)) for i in range(3)]
    assert probable_gaps(events)['support_candidates']==['segment_tree']
    with pytest.raises(ValueError):knowledge_state([dict(event,correct='false')])

def test_rrf_diversity_and_metrics_require_judgments():
    a={'id':'a','chunk_id':1,'excerpt':'prefix sum immutable array','retrieval_score':1}
    b={'id':'b','chunk_id':2,'excerpt':'prefix sum immutable array','retrieval_score':.99}
    c={'id':'c','chunk_id':3,'excerpt':'binary predicate search monotonic','retrieval_score':.9}
    assert reciprocal_rank_fusion([[a,b],[b,c]])[0]['id']=='b'
    assert [x['id'] for x in diversify([a,b,c],2)]==['a','c']
    assert ranking_metrics(['a'],{'a':1})['status']=='not_evaluated'
    metrics=ranking_metrics(['x','a','b'],{'a':2,'b':1,'x':0},2,reviewed=True,complete=True)
    assert metrics['precision_at_k']==.5 and metrics['recall_at_k']==.5 and metrics['reciprocal_rank']==.5
    assert 0<metrics['ndcg_at_k']<1

def test_structural_validation_without_executing_invalid_code():
    spec=specification('Segment Tree')
    with patch('core.research.pipeline.isolation_available',side_effect=AssertionError('Must not reach execution')):
        result,problem=validate_problem({'title':'incomplete'},spec)
    assert not result['structural_valid'] and problem is None

@pytest.mark.skipif(not isolation_available(),reason='Linux bubblewrap unavailable; execution stays disabled')
def test_sandbox_hides_credentials_and_host_files_and_network(tmp_path):
    secret=tmp_path/'secret.txt';secret.write_text('NOT_PUBLIC')
    source='''#include <fstream>
#include <iostream>
#include <cstdlib>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
int main(){std::ifstream f("HOSTFILE");int fd=socket(AF_INET,SOCK_STREAM,0);sockaddr_in a{};a.sin_family=AF_INET;a.sin_port=htons(80);inet_pton(AF_INET,"1.1.1.1",&a.sin_addr);int online=connect(fd,(sockaddr*)&a,sizeof(a))==0;std::cout<<bool(f)<<" "<<(getenv("LLM_API_KEY")!=nullptr)<<" "<<online;close(fd);}'''.replace('HOSTFILE',str(secret))
    judge=IsolatedMiniJudge(tmp_path/'judge');result=judge.judge(source,[{'input':'','expected_output':'0 0 0'}])
    assert result['verdict']=='AC',result

def test_sandbox_failure_blocks_host_execution(tmp_path):
    with patch('core.isolated_judge.isolation_available',return_value=False),patch('core.isolated_judge.subprocess.Popen') as process:
        result=IsolatedMiniJudge(tmp_path/'judge').judge('int main(){}',[{'input':'','expected_output':''}])
    assert result['verdict']=='CE' and not process.called

@pytest.mark.skipif(not isolation_available(),reason='Linux bubblewrap unavailable')
def test_generation_validates_against_independent_oracle_and_saves_bundle(tmp_path):
    pipeline=ResearchPipeline(OfflineFixture('Segment Tree'),judge=IsolatedMiniJudge(tmp_path/'judge'))
    record,problem=pipeline.run('Segment Tree','direct')
    assert record['validated'] and problem['double_validated'] and record['attempts'][0]['validation']['independent_tests_passed']
    folder=save_run(record,problem,tmp_path/'runs');assert (folder/'problem.json.gz').exists()
    response=json.loads(record['attempts'][0]['response']);response['examples'][0]['output']='999999\n'
    report,problem=validate_problem(response,specification('Segment Tree'),IsolatedMiniJudge(tmp_path/'bad'))
    assert report['compiled'] and not report['examples_valid'] and problem is None

def test_real_profile_is_rejected_before_any_model_call():
    provider=Mock();pipeline=ResearchPipeline(provider,retriever=Mock())
    pipeline.retriever.retrieve.return_value=('',[])
    with pytest.raises(ValueError):pipeline.run('Segment Tree','structured',synthetic_profile={'synthetic':False,'name':'private'})
    assert not provider.generate.called

def test_iterative_repair_is_bounded_and_receives_validation_feedback():
    provider=Mock()
    provider.generate.side_effect=[Generation('{}',{},'mock',0,'first'),Generation('{"fixed":true}',{},'mock',0,'second')]
    retriever=Mock(last_report={'method':'bm25'})
    retriever.retrieve.return_value=('',[])
    good={'id':'synthetic'}
    with patch('core.research.pipeline.validate_problem',side_effect=[({'error':'Missing statement'},None),({'independent_tests_passed':True},good)]):
        record,problem=ResearchPipeline(provider,retriever=retriever).run('Segment Tree','iterative',max_revisions=1)
    assert record['validated'] and len(record['attempts'])==2 and provider.generate.call_count==2
    assert 'Missing statement' in provider.generate.call_args.args[1]
    assert problem['research_run_id']==record['run_id']
    provider.reset_mock(side_effect=True)
    provider.generate.return_value=Generation('{}',{},'mock',0,'invalid')
    with patch('core.research.pipeline.validate_problem',return_value=({'error':'Still invalid'},None)):
        record,problem=ResearchPipeline(provider,retriever=retriever).run('Segment Tree','iterative',max_revisions=1)
    assert not record['validated'] and problem is None and provider.generate.call_count==2

def test_beginner_curriculum_has_supported_contracts_and_no_advanced_topics():
    from core.problem_bank import load_problems
    from pathlib import Path
    curriculum=json.loads((Path(__file__).resolve().parents[1]/'data/research/basic_curriculum.json').read_text())
    contracts={p['id'] for p in load_problems()}
    assert len(curriculum['modules'])==9
    assert all(m['contract_id'] in contracts for m in curriculum['modules'])
    assert not {'Segment Tree','Lazy propagation','Block-Cut Tree'} & {m['name'] for m in curriculum['modules']}
    assert all(specification(m['name'])['contract_id']==m['contract_id'] for m in curriculum['modules'])
    assert curriculum['first_api_benchmark']['financial_budget']==0


def test_no_artificial_daily_call_or_token_cap_by_default(tmp_path):
    c=config();ledger=BudgetLedger(tmp_path/'unlimited-free.db')
    assert c.max_calls is None and c.max_reserved_tokens is None
    for _ in range(8):ledger.reserve(c,30000)
    assert ledger.report()['calls']==8 and ledger.report()['reserved_usd']==0

def test_topic_and_required_competencies_checked_before_execution():
    provider=OfflineFixture('Soma de prefixos');value=json.loads(provider.generate('','').text)
    spec=specification('Soma de prefixos')
    for broken in ({**value,'topic':'DP'},{**value,'target_competencies':['dp_state']}):
        with patch('core.research.pipeline.isolation_available',side_effect=AssertionError('Wrong topic must never reach execution')):
            report,problem=validate_problem(broken,spec)
        assert problem is None and report['error']
