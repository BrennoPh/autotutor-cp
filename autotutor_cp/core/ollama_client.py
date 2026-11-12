"""Loopback-only Ollama transport. No API key, proxy, remote host or cloud model."""
import os
from urllib.parse import urlsplit
import requests

DEFAULT_LOCAL_MODEL='llama3.2:1b'


class OllamaError(RuntimeError):
    def __init__(self,message,status_code=None):
        super().__init__(message);self.status_code=status_code;self.message=message


class OllamaClient:
    def __init__(self):
        self.url=os.environ.get('AUTOTUTOR_OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')
        parts=urlsplit(self.url)
        if parts.scheme!='http' or parts.hostname not in ('127.0.0.1','localhost','::1') or parts.username or parts.password or parts.path or parts.query or parts.fragment:
            raise OllamaError('O motor local aceita somente um endereço HTTP de loopback, sem credenciais ou caminho.')

    def request(self,path,payload=None):
        try:
            with requests.Session() as session:
                # Local traffic must never inherit an HTTP proxy from the environment.
                session.trust_env=False
                if payload is None:response=session.get(self.url+path,timeout=(3,15),allow_redirects=False)
                else:response=session.post(self.url+path,json=payload,timeout=(3,300),allow_redirects=False)
                if response.status_code!=200:
                    try:detail=str(response.json().get('error',''))[:500]
                    except (ValueError,AttributeError):detail=''
                    raise OllamaError(detail or 'O Ollama recusou a solicitação.',response.status_code)
                try:data=response.json()
                except ValueError as exc:raise OllamaError('O Ollama respondeu sem JSON válido.') from exc
                if not isinstance(data,dict):raise OllamaError('Formato de resposta inesperado do Ollama.')
                if data.get('error'):raise OllamaError(str(data['error'])[:500])
                return data
        except requests.ConnectionError as exc:raise OllamaError('O Ollama não está em execução. Inicie scripts/start_local_ai.sh ou ollama serve.') from exc
        except requests.Timeout as exc:raise OllamaError('O modelo local excedeu 300 segundos. Escolha um texto mais curto ou feche aplicativos para liberar memória.') from exc

    @staticmethod
    def validate_model(model):
        if not model or 'cloud' in model.lower() or '/' in model or '://' in model:
            raise OllamaError('Selecione um modelo local instalado, como llama3.2:1b. Modelos de nuvem não são aceitos neste modo.')

    def chat(self,model,system,prompt,json_mode=False):
        self.validate_model(model)
        if len(system)+len(prompt)>12000:
            raise OllamaError('O pedido excede o limite de texto deste modelo leve. Reduza o código ou o texto enviado e tente novamente.')
        payload={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}],
                 'stream':False,'keep_alive':0,'options':{'temperature':0,'num_ctx':4096,'num_predict':2048,'num_thread':2,'num_batch':128}}
        if json_mode:payload['format']=json_mode if isinstance(json_mode,dict) else 'json'
        result=self.request('/api/chat',payload)
        if not isinstance(result.get('message'),dict):raise OllamaError('O Ollama retornou uma mensagem em formato inesperado.')
        return result

    def models(self):
        result=self.request('/api/tags')
        return sorted({m['name'] for m in result.get('models',[]) if isinstance(m,dict) and isinstance(m.get('name'),str) and 'cloud' not in m['name'].lower()})
