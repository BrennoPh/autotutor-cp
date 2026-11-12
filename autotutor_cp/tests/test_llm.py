from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest
from core.llm_client import LLMClient
from core.codigen_tutor import CodigenTutor


def fake_client(response=None, error=None):
    client = MagicMock()
    client.__enter__.return_value = client
    if error:
        client.models.generate_content.side_effect = error
    else:
        client.models.generate_content.return_value = SimpleNamespace(text=response)
    return client


@pytest.mark.parametrize('code,expected', [(400,'parâmetros'), (401,'chave'), (403,'chave'), (404,'modelo'), (429,'cota'), (503,'indisponível')])
def test_actionable_provider_errors_and_secret_redaction(code, expected):
    from google.genai.errors import ClientError
    key = 'AIza-test-VERY-PRIVATE-1234'
    error = ClientError(code, {'error':{'code':code,'message':f'Provider failure. key={key}'}})
    llm = LLMClient('Gemini', key, 'gemini-flash-latest')
    with patch.object(llm, '_gemini_client', return_value=fake_client(error=error)):
        assert llm.complete('system','prompt') is None
    assert expected in llm.last_error
    assert key not in str(llm.events)
    assert llm.events[-1]['code'] == code


def test_trimmed_credentials_and_json_response():
    llm = LLMClient('Gemini', '  example-key  ', ' models/gemini-flash-latest ')
    client = fake_client('```json\n{"ok":true}\n```')
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.complete('s','p', True) == {'ok':True}
    assert llm.api_key == 'example-key'
    assert llm.model == 'gemini-flash-latest'
    assert llm.last_source == 'api'
    assert not llm.last_error
    assert client.models.generate_content.call_args.kwargs['config']['response_mime_type'] == 'application/json'


@pytest.mark.parametrize('text,reason', [('', 'vazia'), ('this is not json', 'JSON')])
def test_invalid_response_is_visible(text, reason):
    llm = LLMClient('Gemini','key','model')
    with patch.object(llm, '_gemini_client', return_value=fake_client(text)):
        assert llm.complete('s','p',True) is None
    assert reason in llm.last_error


def test_model_listing_filters_generation_support():
    llm = LLMClient('Gemini','key','model')
    client = fake_client()
    client.models.list.return_value = [SimpleNamespace(name='models/gemini-flash-latest', supported_actions=['generateContent']),
                                       SimpleNamespace(name='models/embedding', supported_actions=['embedContent'])]
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.list_models() == ['gemini-flash-latest']


def test_configured_is_distinct_from_verified_and_pedagogy_rejection():
    local = LLMClient()
    assert local.complete('s','p') is None and not local.events
    llm = LLMClient('Gemini','key','model')
    assert llm.enabled and not llm.events
    with patch.object(llm, '_gemini_client', return_value=fake_client('Conexão confirmada.')):
        assert llm.test_connection()
    with patch.object(llm, '_gemini_client', return_value=fake_client('```cpp\nint main(){}\n```')):
        result = CodigenTutor(llm).explain_code('int main(){}')
    assert 'main()' not in result
    assert 'pedagógicas' in llm.last_error
    assert llm.events[-1]['source'] == 'local'


def test_small_commented_examples_are_not_mistaken_for_solution_leaks():
    llm = LLMClient('Gemini','key','model')
    response = 'Exemplo de atualização:\n```cpp\nfrequencia[valor]++; // Conta uma ocorrência.\n```'
    with patch.object(llm, '_gemini_client', return_value=fake_client(response)):
        result = CodigenTutor(llm).generate_material('Exemplo Comentado','Estruturas de Dados','Iniciante','Jogos')
    assert result.startswith(response)
    assert "Para continuar estudando" in result
    assert llm.last_source == 'api'
    assert not llm.last_error


def test_preview_model_retries_without_system_instruction_and_remembers_capability():
    from google.genai.errors import ClientError
    capabilities = {}
    llm = LLMClient('Gemini', 'key', 'antigravity-preview-05-2026', capabilities=capabilities)
    client = fake_client()
    client.models.generate_content.side_effect = [
        ClientError(400, {'error':{'message':'Developer instruction is not enabled for models/antigravity-preview-05-2026'}}),
        SimpleNamespace(text='Conexão confirmada.')]
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.test_connection()
    assert client.models.generate_content.call_count == 2
    original, retry = [call.kwargs for call in client.models.generate_content.call_args_list]
    assert 'system_instruction' in original['config']
    assert 'system_instruction' not in retry['config']
    assert 'Responda em português.' in retry['contents']
    assert 'Conexão confirmada.' in retry['contents']
    assert llm.last_source == 'api' and not llm.last_error
    assert len(llm.events) == 1 and 'compatível' in llm.events[0]['message']
    # A new Streamlit run reuses only feature flags; it does not repeat the known 400.
    next_llm = LLMClient('Gemini', 'key', llm.model, capabilities=capabilities)
    next_client = fake_client('Uma pista em prosa.')
    with patch.object(next_llm, '_gemini_client', return_value=next_client):
        assert next_llm.complete('Não revele a resposta.', 'Explique este código.')
    assert next_client.models.generate_content.call_count == 1
    call = next_client.models.generate_content.call_args.kwargs
    assert 'system_instruction' not in call['config']
    assert 'Não revele a resposta.' in call['contents']


def test_preview_json_negotiation_preserves_parsing_and_educational_instructions():
    from google.genai.errors import ClientError
    llm = LLMClient('Gemini', 'key', 'preview')
    client = fake_client()
    client.models.generate_content.side_effect = [
        ClientError(400, {'error':{'message':'Developer instruction is not enabled for models/preview'}}),
        ClientError(400, {'error':{'message':'response_mime_type application/json is not supported'}}),
        SimpleNamespace(text='{"title":"Exercício"}')]
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.complete('Preserve a gramática de entrada.', 'Gere JSON.', True) == {'title':'Exercício'}
    assert client.models.generate_content.call_count == 3
    call = client.models.generate_content.call_args.kwargs
    assert not call['config']
    assert 'Preserve a gramática de entrada.' in call['contents']
    assert 'objeto JSON válido' in call['contents']
    assert llm.last_source == 'api'


def test_compatibility_does_not_hide_quota_error_after_parameter_recovery():
    from google.genai.errors import ClientError
    llm = LLMClient('Gemini', 'key', 'preview')
    client = fake_client()
    client.models.generate_content.side_effect = [
        ClientError(400, {'error':{'message':'Developer instruction is not enabled for models/preview'}}),
        ClientError(429, {'error':{'message':'Quota exceeded'}})]
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.complete('Tutor instructions', 'A question') is None
    assert client.models.generate_content.call_count == 2
    assert 'cota' in llm.last_error
    assert llm.events[-1]['code'] == 429


def test_unrelated_parameter_errors_are_not_retried():
    from google.genai.errors import ClientError
    llm = LLMClient('Gemini', 'key', 'preview')
    client = fake_client(error=ClientError(400, {'error':{'message':'Invalid contents'}}))
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.complete('Tutor instructions', 'A question') is None
    assert client.models.generate_content.call_count == 1


def test_interactions_only_model_routes_and_caches_endpoint_without_storage():
    from google.genai.errors import ClientError
    capabilities = {}
    llm = LLMClient('Gemini','key','preview', capabilities=capabilities)
    client = fake_client(error=ClientError(400, {'error':{'message':'This model only supports Interactions API.'}}))
    client.interactions.create.return_value = SimpleNamespace(output_text='Conexão confirmada.')
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.test_connection()
    assert client.models.generate_content.call_count == 1
    assert client.interactions.create.call_count == 1
    call = client.interactions.create.call_args.kwargs
    assert call['store'] is False and 0 < call['timeout'] <= 15
    assert 'Responda em português.' in call['input']
    assert llm.last_source == 'api' and not llm.last_error
    client.models.generate_content.reset_mock()
    next_llm = LLMClient('Gemini','key','preview', capabilities=capabilities)
    client.interactions.create.return_value = SimpleNamespace(outputs=[SimpleNamespace(type='text',text='{"ok":true}')])
    with patch.object(next_llm, '_gemini_client', return_value=client):
        assert next_llm.complete('Instrução', 'Pedido', True) == {'ok':True}
    assert not client.models.generate_content.called


def test_real_google_sdk_serializes_interactions_request_with_mock_http_transport():
    """Exercise the installed SDK, not only a mocked method call."""
    import json
    import httpx
    from google import genai
    requests=[]
    def handle(request):
        body=json.loads(request.content)
        requests.append((request.url.path,body))
        if 'generateContent' in request.url.path:
            return httpx.Response(400,json={'error':{'code':400,'message':'This model only supports Interactions API.','status':'INVALID_ARGUMENT'}})
        assert request.url.path.endswith('/interactions')
        return httpx.Response(200,json={'id':'interaction-test','status':'completed','model':'preview',
                                       'steps':[{'type':'model_output','content':[{'type':'text','text':'Conexão confirmada.'}]}]})
    http_client=httpx.Client(transport=httpx.MockTransport(handle))
    client=genai.Client(api_key='example-key',http_options={'httpx_client':http_client,'timeout':1000})
    llm=LLMClient('Gemini','example-key','preview')
    with patch.object(llm,'_gemini_client',return_value=client):
        assert llm.test_connection(), llm.last_error
    assert len(requests)==2
    assert requests[-1][1]['store'] is False
    assert 'Responda em português.' in requests[-1][1]['input']


def test_material_preferences_and_specific_goal_reach_the_model():
    llm=LLMClient('Gemini','key','model');client=fake_client('Uma explicação focada no seu pedido.')
    with patch.object(llm,'_gemini_client',return_value=client):
        result=CodigenTutor(llm).generate_material('Explicação','DP','Iniciante','Jogos',
            learning_request='Por que a ordem dos laços muda a contagem?',length='Curto',depth='Passo a passo',
            include_examples=False,include_exercises=False)
    prompt=client.models.generate_content.call_args.kwargs['contents']
    assert 'Por que a ordem dos laços muda a contagem?' in prompt
    assert '150 a 250 palavras' in prompt and 'Passo a passo' in prompt
    assert 'Não inclua exemplos, código ou rastreamentos' in prompt
    assert 'Não inclua exercícios' in prompt
    assert result.startswith('Uma explicação focada')


def test_local_material_respects_length_depth_and_optional_sections():
    tutor=CodigenTutor()
    short=tutor.generate_material('Explicação','DP','Iniciante','Jogos',length='Curto',depth='Visão geral',include_examples=False,include_exercises=False)
    long=tutor.generate_material('Explicação','DP','Iniciante','Jogos',length='Longo',depth='Aprofundada')
    assert len(long)>len(short)*2
    assert 'Exemplo passo a passo' not in short and '```' not in short
    assert 'Exercícios para conferir' not in short
    assert 'Exemplo passo a passo' in long and 'Exercícios para conferir' in long
    request=tutor.generate_material('Explicação','DP','Iniciante','Jogos',learning_request='Uma dúvida muito específica',length='Curto')
    assert 'Uma dúvida muito específica' in request
    assert 'requer um motor de IA conectado' in request



def test_small_local_model_receives_external_text_instead_of_authored_lesson(tmp_path,monkeypatch):
    from core.knowledge import KnowledgeBase
    path=tmp_path/'kb.sqlite3';monkeypatch.setenv('AUTOTUTOR_KNOWLEDGE_DB',str(path))
    KnowledgeBase(path).import_documents([dict(title='Prefix sums',url='https://example.org/prefix',source='External source',license='Test',content='Prefix sums use P[R]-P[L-1] and P[0]=0. '*20)])
    llm=LLMClient('Ollama')
    with patch('core.ollama_client.OllamaClient.chat',return_value={'message':{'content':'P[3] menos P[1]: 7 menos 2 resulta em 5.'}}) as chat:
        result=CodigenTutor(llm).generate_material('Explicação','Prefix Sum','Iniciante','',learning_request='Prefix sums',length='Curto')
    prompt=chat.call_args.args[2]
    assert 'BASE DE ESTUDO REVISADA' not in prompt
    assert 'P[R]-P[L-1]' in prompt and 'P[0]=0' in prompt
    assert result.startswith('P[3] menos P[1]')
    assert llm.last_source=='api'


def test_gemini_probe_reduces_thinking_without_changing_learning_requests():
    llm = LLMClient('Gemini', 'key', 'gemini-3.8-flash',
                    context_provider=lambda _: pytest.fail('Connection must not load profile history'))
    client = fake_client('Conexão confirmada.')
    with patch.object(llm, '_gemini_client', return_value=client) as factory:
        assert llm.test_connection()
    factory.assert_called_once_with(connection_test=True)
    config = client.models.generate_content.call_args.kwargs['config']
    assert config['thinking_config'] == {'thinking_level':'low'}
    assert config['max_output_tokens'] == 2048
    assert 0 < config['http_options']['timeout'] <= 15000
    assert config['http_options']['retry_options']['attempts'] == 1
    with patch.object(llm, '_gemini_client', return_value=client):
        assert llm.complete('Tutor', 'Explique DP', include_history=False)
    config = client.models.generate_content.call_args.kwargs['config']
    assert 'thinking_config' not in config and 'max_output_tokens' not in config
    assert 'http_options' not in config


@pytest.mark.parametrize('interactions', [False, True])
def test_gemini_probe_real_sdk_does_not_retry_server_errors(interactions):
    import httpx
    from google import genai
    real_client = genai.Client
    requests = []
    options = []
    def handle(request):
        requests.append(request)
        return httpx.Response(503, json={'error':{'code':503,'message':'Temporarily unavailable','status':'UNAVAILABLE'}})
    def build(**kwargs):
        options.append(kwargs['http_options'].copy())
        kwargs['http_options']['httpx_client'] = httpx.Client(transport=httpx.MockTransport(handle))
        return real_client(**kwargs)
    capabilities = {'gemini-3.8-flash':{'api':'interactions'}} if interactions else {}
    llm = LLMClient('Gemini', 'example-key', 'gemini-3.8-flash', capabilities=capabilities)
    with patch('google.genai.Client', side_effect=build):
        assert not llm.test_connection()
    assert len(requests) == 1
    assert options == [{'timeout':15000,'retry_options':{'attempts':1}}]
    assert llm.events[-1]['code'] == 503
    assert llm.last_source != 'api'


def test_gemini_probe_compatibility_negotiation_shares_remaining_time():
    from google.genai.errors import ClientError
    llm = LLMClient('Gemini','key','preview')
    client = fake_client(error=ClientError(400, {'error':{'message':'Developer instruction is not enabled'}}))
    with patch.object(llm, '_gemini_client', return_value=client), patch('core.llm_client.time.monotonic', side_effect=[10, 11, 26]):
        assert not llm.test_connection()
    assert client.models.generate_content.call_count == 1
    assert '15 s' in llm.last_error and 'chave inválida' in llm.last_error


@pytest.mark.parametrize('interactions', [False, True])
def test_gemini_probe_real_sdk_serializes_fast_generation_and_network_timeout(interactions):
    import json
    import httpx
    from google import genai
    real_client = genai.Client
    requests = []
    def handle(request):
        requests.append(request)
        body = json.loads(request.content)
        config = body['generation_config' if interactions else 'generationConfig']
        if interactions:
            assert config['thinking_level'] == 'low'
            assert config['max_output_tokens'] == 2048
            assert body['store'] is False
            response = {'id':'probe','status':'completed','model':'gemini-3.8-flash',
                        'steps':[{'type':'model_output','content':[{'type':'text','text':'Conexão confirmada.'}]}]}
        else:
            assert config['thinkingConfig'].get('thinkingLevel', config['thinkingConfig'].get('thinking_level')) == 'LOW'
            assert config['maxOutputTokens'] == 2048
            response = {'candidates':[{'content':{'role':'model','parts':[{'text':'Conexão confirmada.'}]},'finishReason':'STOP'}]}
        assert all(0 < value <= 15 for value in request.extensions['timeout'].values() if value is not None)
        return httpx.Response(200,json=response)
    def build(**kwargs):
        kwargs['http_options']['httpx_client'] = httpx.Client(transport=httpx.MockTransport(handle))
        return real_client(**kwargs)
    capabilities = {'gemini-3.8-flash':{'api':'interactions'}} if interactions else {}
    llm = LLMClient('Gemini','example-key','gemini-3.8-flash',capabilities=capabilities)
    with patch('google.genai.Client',side_effect=build):
        assert llm.test_connection(), llm.last_error
    assert len(requests) == 1 and llm.last_source == 'api'
