"""Track provider access separately from the validity of generated content.

The status is the last observed result, not a persistent network connection.
No timer, background request, credential or model change is performed here.
"""


def update_connection(previous, events):
    state = dict(previous or {})
    for event in events:
        source = event.get('source')
        kind = event.get('failure_kind')
        if source == 'api' or kind == 'response':
            state.update(ok=True, status='verified' if source == 'api' else 'response_rejected',
                         message='Resposta da API recebida com sucesso.' if source == 'api' else
                         'A API respondeu, mas o conteúdo foi rejeitado. Confira o diagnóstico da operação.',
                         code=None, last_success_at=event.get('time'))
        elif source == 'local' and kind in ('provider', 'transport', 'configuration'):
            code = event.get('code')
            temporary = kind == 'transport' or code in (408, 500, 502, 503, 504)
            status = ('temporary_error' if temporary else
                      'credentials_error' if code in (401, 403) else
                      'quota_error' if code == 429 else
                      'balance_error' if code == 402 else 'request_error')
            state.update(ok=False, status=status, message=event['message'],
                         code=code, last_failure_at=event.get('time'))
        # Pedagogical/schema validation and audit notices do not prove loss of access.
    return state or None


def connection_label(provider, configured, state):
    if not configured:
        return f'{provider} · aguardando chave e modelo', ''
    if not state:
        return f'{provider} · selecionado, conexão não testada', 'configured'
    status = state.get('status')
    if status == 'temporary_error':
        return f'{provider} · instabilidade temporária', 'configured'
    if status == 'response_rejected':
        return f'{provider} · respondeu; conteúdo rejeitado', 'configured'
    if status == 'quota_error':
        return f'{provider} · limite de uso ou cota atingida', 'configured'
    if status == 'balance_error':
        return f'{provider} · saldo insuficiente', 'configured'
    if status == 'credentials_error':
        return f'{provider} · verificar chave ou permissão', 'configured'
    if state.get('ok'):
        return f'{provider} · conexão verificada', 'connected'
    return f'{provider} · conexão requer atenção', 'configured'
