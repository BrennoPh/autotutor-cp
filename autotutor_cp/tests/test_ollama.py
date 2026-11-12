from unittest.mock import patch,MagicMock
import pytest
import requests
from core.ollama_client import OllamaClient,OllamaError
from core.llm_client import LLMClient


def test_local_model_needs_no_key_and_preserves_history_audit_and_json():
    audit=[];client=LLMClient('Ollama',context_provider=lambda q:'{"level":"Iniciante"}',audit_callback=audit.append)
    assert client.enabled and client.model=='llama3.2:1b'
    with patch('core.ollama_client.OllamaClient.request',return_value={'message':{'content':'{"math_essence":"prefixos"}'},'done_reason':'stop'}) as request:
        assert client.complete('Tutor','Explique prefixos',True)=={'math_essence':'prefixos'}
    payload=request.call_args.args[1]
    assert payload['format']=='json' and payload['stream'] is False
    assert payload['messages'][0]['role']=='system'
    assert 'HISTÓRICO DO PERFIL' in payload['messages'][1]['content']
    assert payload['options']['num_ctx']==4096
    assert payload['keep_alive']==0
    assert payload['options']['num_thread']==2
    assert payload['options']['num_batch']==128
    assert audit[0]['provider']=='Ollama' and audit[0]['context_chars']>0
    assert client.last_source=='api' and not client.last_error


def test_connection_does_not_send_personal_history():
    client=LLMClient('Ollama',context_provider=lambda q:'PRIVATE_HISTORY')
    with patch('core.ollama_client.OllamaClient.request',return_value={'message':{'content':'Conexão confirmada.'}}) as request:
        assert client.test_connection()
    assert 'PRIVATE_HISTORY' not in str(request.call_args)


@pytest.mark.parametrize('url',['https://example.com','http://192.168.1.10:11434','http://user:pass@localhost:11434','http://localhost:11434/path'])
def test_local_transport_rejects_remote_or_credential_urls(monkeypatch,url):
    monkeypatch.setenv('AUTOTUTOR_OLLAMA_URL',url)
    with pytest.raises(OllamaError):OllamaClient()


def test_missing_server_and_model_report_real_failure():
    client=LLMClient('Ollama')
    with patch('core.ollama_client.OllamaClient.request',side_effect=OllamaError('Ollama não está em execução.')):
        assert client.complete('Tutor','Olá') is None
    assert 'não está em execução' in client.last_error and client.last_source=='local'
    with patch('core.ollama_client.OllamaClient.request',side_effect=OllamaError('model not found',404)):
        assert not client.test_connection()
    assert 'ollama pull' in client.last_error and client.events[-1]['code']==404


def test_invalid_json_empty_and_truncated_output_are_distinguished():
    client=LLMClient('Ollama')
    for text in ('','not json'):
        with patch('core.ollama_client.OllamaClient.request',return_value={'message':{'content':text}}):assert client.complete('Tutor','Pedido',True) is None
        assert client.last_source=='local'
    with patch('core.ollama_client.OllamaClient.request',return_value={'message':{'content':'Texto parcial'},'done_reason':'length'}):
        assert client.complete('Tutor','Pedido')=='Texto parcial'
    assert any(e['source']=='notice' and 'incompleto' in e['message'] for e in client.events)


def test_listing_models_only_lists_installed_local_models():
    client=LLMClient('Ollama')
    with patch('core.ollama_client.OllamaClient.request',return_value={'models':[{'name':'llama3.2:1b'},{'name':'example:cloud'},{'name':'llama3.2:1b'},{}]}):
        assert client.list_models()==['llama3.2:1b']
    with pytest.raises(OllamaError):OllamaClient().chat('example:cloud','Tutor','Test')


def test_transport_bypasses_proxy_and_disallows_redirects():
    session=MagicMock();session.__enter__.return_value=session
    session.post.return_value.status_code=200;session.post.return_value.json.return_value={'message':{'content':'Olá'}}
    with patch('core.ollama_client.requests.Session',return_value=session):
        OllamaClient().chat('llama3.2:1b','Tutor','Pedido')
    assert session.trust_env is False
    assert session.post.call_args.kwargs['allow_redirects'] is False


def test_transport_network_errors_have_actionable_local_messages():
    session=MagicMock();session.__enter__.return_value=session
    session.post.side_effect=requests.ConnectionError()
    with patch('core.ollama_client.requests.Session',return_value=session):
        with pytest.raises(OllamaError,match='não está em execução'):OllamaClient().chat('llama3.2:1b','Tutor','Pedido')


def test_transport_supplies_json_schema_for_model_decisions():
    schema={'type':'object','properties':{'level':{'type':'string','enum':['Não avaliado']}}}
    with patch('core.ollama_client.OllamaClient.request',return_value={'message':{'content':'{"level":"Não avaliado"}'}}) as request:
        assert LLMClient('Ollama',require_model=True).complete('Tutor','Analise os dados',schema)=={'level':'Não avaliado'}
    payload=request.call_args.args[1]
    assert payload['format']==schema
    assert payload['options']['temperature']==0
