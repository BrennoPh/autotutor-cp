from unittest.mock import patch
from types import SimpleNamespace
import pytest
from core.ai_connection import update_connection,connection_label
from core.llm_client import LLMClient,AIUnavailable


def success():
    return update_connection(None,[dict(source='api',time='2026-11-04T01:40:17-03:00')])


def test_overload_keeps_previous_verification_without_claiming_current_success():
    old=success()
    current=update_connection(old,[dict(source='local',failure_kind='provider',code=503,message='Sobrecarga',time='later')])
    assert old['ok'] and not current['ok']
    assert current['last_success_at']==old['last_success_at']
    assert current['status']=='temporary_error'
    assert 'instabilidade temporária' in connection_label('Gemini',True,current)[0]
    recovered=update_connection(current,[dict(source='api',time='new-success')])
    assert recovered['ok'] and recovered['last_success_at']=='new-success'
    assert recovered['code'] is None and recovered['status']=='verified'


@pytest.mark.parametrize('code,status',[(401,'credentials_error'),(403,'credentials_error'),(402,'balance_error'),(429,'quota_error'),(400,'request_error'),(404,'request_error')])
def test_errors_have_distinct_status_and_do_not_hide_previous_failure(code,status):
    state=update_connection(success(),[dict(source='local',failure_kind='provider',code=code,message='Falhou')])
    assert state['status']==status and not state['ok']
    assert update_connection(state,[dict(source='local',failure_kind='validation',message='Conteúdo rejeitado')])==state
    assert state['last_success_at']


def test_local_validation_and_audit_notices_do_not_reset_access():
    old=success()
    assert update_connection(old,[dict(source='local',failure_kind='validation'),dict(source='notice')])==old
    assert update_connection(None,[dict(source='local',failure_kind='validation')]) is None


def test_real_rejected_response_is_not_mistaken_for_provider_outage():
    llm=LLMClient('Gemini','key','model',require_model=True)
    from unittest.mock import MagicMock
    transport=MagicMock();transport.__enter__.return_value=transport
    transport.models.generate_content.return_value=SimpleNamespace(text='invalid-json')
    with patch.object(llm,'_gemini_client',return_value=transport),pytest.raises(AIUnavailable):
        llm.complete('Retorne JSON','Pedido',True)
    state=update_connection(None,llm.events)
    assert state['ok'] and state['status']=='response_rejected'
    assert 'conteúdo rejeitado' in connection_label('Gemini',True,state)[0]
    with pytest.raises(AIUnavailable):llm.report_fallback('Estrutura inválida')
    assert update_connection(state,llm.events[-1:])==state


def test_transport_timeout_does_not_erase_previous_access():
    llm=LLMClient('Gemini','key','model')
    llm._exception(TimeoutError('timed out'))
    state=update_connection(success(),llm.events)
    assert not state['ok'] and state['status']=='temporary_error' and state['last_success_at']
