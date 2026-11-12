from types import SimpleNamespace
from unittest.mock import MagicMock,patch
import pytest
from core.llm_client import LLMClient,AIUnavailable
from core.cloud_providers import cloud_url,qwen_models,CloudProviderError


def sdk_response(text='{"ok":true}',finish='stop'):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text),finish_reason=finish)])


@pytest.mark.parametrize('provider,model,url',[('DeepSeek','deepseek-flash','https://api.deepseek.com'),('Qwen','qwen-plus','https://dashscope-intl.aliyuncs.com/compatible-mode/v1')])
def test_cloud_providers_route_history_json_and_audit_to_official_endpoint(provider,model,url):
    audit=[];secret='sk-private-test-only'
    llm=LLMClient(provider,secret,require_model=True,context_provider=lambda q:'{"quiz_correct":2}',audit_callback=audit.append)
    client=MagicMock();client.__enter__.return_value=client
    client.chat.completions.create.return_value=sdk_response()
    with patch('openai.OpenAI',return_value=client) as sdk:
        assert llm.complete('Tutor: retorne JSON.','Analise',True)=={'ok':True}
    assert sdk.call_args.kwargs['base_url']==url
    assert sdk.call_args.kwargs['api_key']==secret
    assert llm.model==model and llm.last_source=='api'
    request=client.chat.completions.create.call_args.kwargs
    assert request['response_format']=={'type':'json_object'}
    assert 'quiz_correct' in request['messages'][1]['content']
    if provider=='Qwen':assert request['extra_body']=={'enable_thinking':False}
    assert audit[0]['provider']==provider and audit[0]['context_chars']>0
    assert secret not in str(audit)


def test_cloud_keys_are_required_and_selection_makes_no_request():
    with patch('openai.OpenAI') as sdk:
        for provider in ('DeepSeek','Qwen'):
            llm=LLMClient(provider,require_model=True)
            assert not llm.enabled
            assert not llm.test_connection()
        sdk.assert_not_called()


def test_qwen_uses_selected_region_workspace_and_thinking_setting():
    assert cloud_url('Qwen','China · Pequim','work-123')=='https://work-123.cn-beijing.maas.aliyuncs.com/compatible-mode/v1'
    client=MagicMock();client.__enter__.return_value=client;client.chat.completions.create.return_value=sdk_response('Conectado')
    llm=LLMClient('Qwen','key','qwen3.7-plus',qwen_region='China · Hong Kong',qwen_workspace='work123',qwen_thinking=True,require_model=True)
    with patch('openai.OpenAI',return_value=client) as sdk:assert llm.test_connection()
    assert sdk.call_args.kwargs['base_url']=='https://work123.cn-hongkong.maas.aliyuncs.com/compatible-mode/v1'
    assert client.chat.completions.create.call_args.kwargs['extra_body']=={'enable_thinking':True}


@pytest.mark.parametrize('workspace',['https://attacker.example','evil.com','a/b','x@host','x?api_key=secret'])
def test_qwen_workspace_cannot_redirect_credentials(workspace):
    with pytest.raises(CloudProviderError):cloud_url('Qwen',workspace=workspace)


def test_deepseek_catalog_uses_its_endpoint_and_preserves_redacted_errors():
    from openai import AuthenticationError
    import httpx
    llm=LLMClient('DeepSeek','sk-PRIVATE',require_model=True)
    client=MagicMock();client.__enter__.return_value=client
    client.models.list.return_value=[SimpleNamespace(id='deepseek-flash'),SimpleNamespace(id='deepseek-v4-pro')]
    with patch('openai.OpenAI',return_value=client) as sdk:
        assert llm.list_models()==['deepseek-flash','deepseek-v4-pro']
    assert sdk.call_args.kwargs['base_url']=='https://api.deepseek.com'
    response=httpx.Response(401,request=httpx.Request('POST','https://api.deepseek.com/chat/completions'))
    client.chat.completions.create.side_effect=AuthenticationError('Invalid key sk-PRIVATE',response=response,body={})
    with patch('openai.OpenAI',return_value=client),pytest.raises(AIUnavailable):llm.complete('Tutor','Pedido')
    assert 'sk-PRIVATE' not in str(llm.events) and llm.events[-1]['code']==401


def test_qwen_native_catalog_parses_pages_without_forwarding_credentials():
    first=MagicMock(status_code=200);first.json.return_value={'output':{'models':[{'model':'qwen-plus'}],'total':101}}
    second=MagicMock(status_code=200);second.json.return_value={'output':{'models':[{'model':'qwen-max'}],'total':101}}
    session=MagicMock();session.__enter__.return_value=session;session.get.side_effect=[first,second]
    with patch('core.cloud_providers.requests.Session',return_value=session):
        assert qwen_models('private','Singapura')==['qwen-max','qwen-plus']
    calls=session.get.call_args_list
    assert len(calls)==2 and calls[0].kwargs['params']['page_no']==1 and calls[1].kwargs['params']['page_no']==2
    assert calls[0].args[0]=='https://dashscope-intl.aliyuncs.com/api/v1/models'
    assert all(c.kwargs['allow_redirects'] is False for c in calls)
    assert calls[0].kwargs['headers']['Authorization']=='Bearer private'


def test_qwen_bad_catalog_and_invalid_cloud_json_do_not_trigger_local_templates():
    response=MagicMock(status_code=200);response.json.return_value={'unexpected':[]}
    session=MagicMock();session.__enter__.return_value=session;session.get.return_value=response
    with patch('core.cloud_providers.requests.Session',return_value=session),pytest.raises(CloudProviderError):qwen_models('private')
    client=MagicMock();client.__enter__.return_value=client;client.chat.completions.create.return_value=sdk_response('broken JSON')
    with patch('openai.OpenAI',return_value=client),pytest.raises(AIUnavailable):LLMClient('DeepSeek','key',require_model=True).complete('JSON','Pedido',True)


def test_http_status_takes_precedence_over_sdk_error_type_and_402_means_balance():
    from openai import APIStatusError
    import httpx
    client=LLMClient('DeepSeek','sk-private',require_model=True)
    response=httpx.Response(402,request=httpx.Request('POST','https://api.deepseek.com/chat/completions'))
    error=APIStatusError('Insufficient Balance sk-private',response=response,body={'code':'invalid_request_error','message':'Insufficient Balance sk-private'})
    assert error.code=='invalid_request_error'
    transport=MagicMock();transport.__enter__.return_value=transport;transport.chat.completions.create.side_effect=error
    with patch('openai.OpenAI',return_value=transport):assert client.test_connection() is False
    assert client.events[-1]['code']==402
    assert 'Saldo insuficiente' in client.last_error
    assert 'sk-private' not in str(client.events)
