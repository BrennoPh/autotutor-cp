"""Explicit provider protocol, atomic daily reservations, usage and secret-free audit."""
from dataclasses import dataclass,field
from datetime import datetime,timezone
from pathlib import Path
from typing import Protocol
import hashlib,json,os,sqlite3,time,uuid
import requests

ROOT=Path(__file__).resolve().parents[2]
GEMINI_BASE='https://generativelanguage.googleapis.com/v1beta'

class ResearchError(RuntimeError):pass
class BudgetExceeded(ResearchError):pass

def settings(env_file=None):
    values={}
    path=Path(env_file or ROOT/'.env')
    if path.exists():
        for line in path.read_text().splitlines():
            line=line.strip()
            if line and not line.startswith('#') and '=' in line:
                k,v=line.split('=',1);values[k.strip()]=v.strip().strip('\"\'')
    values.update(os.environ)
    return values

@dataclass(frozen=True)
class ResearchConfig:
    provider:str='Gemini'
    model:str='gemini-3.1-flash-lite'
    api_key:str=field(default='',repr=False)
    base_url:str=GEMINI_BASE
    temperature:float=.3
    max_output_tokens:int=4096
    max_calls:int|None=None
    max_reserved_tokens:int|None=None
    max_cost_usd:float=0
    free_tier_only:bool=True
    allow_paid:bool=False
    min_interval:float=15
    max_input_bytes:int=18000
    max_attempts:int=1
    enabled:bool=True

    def __post_init__(self):
        if self.provider not in ('Gemini','Ollama'):raise ValueError('Provedor experimental inválido.')
        if self.provider=='Gemini' and self.base_url!=GEMINI_BASE:raise ValueError('A chave Gemini só pode ser enviada ao endpoint oficial.')
        if not 0<=self.temperature<=1 or not 32<=self.max_output_tokens<=4096:raise ValueError('Configuração de geração fora do limite do piloto.')
        if (self.max_calls is not None and self.max_calls<1) or not 1<=self.max_attempts<=2 or self.max_cost_usd!=0 or self.allow_paid or not self.free_tier_only:raise ValueError('Este piloto aceita apenas cota gratuita, sem autorização de gasto.')
        if not 0<=self.min_interval<=60 or not 1000<=self.max_input_bytes<=30000 or (self.max_reserved_tokens is not None and self.max_reserved_tokens<4096):raise ValueError('Limite de requisição inválido.')

    @classmethod
    def from_env(cls,env_file=None):
        e=settings(env_file)
        return cls(provider=e.get('LLM_PROVIDER','Gemini'),model=e.get('LLM_MODEL','gemini-3.1-flash-lite'),api_key=e.get('LLM_API_KEY',e.get('GEMINI_API_KEY','')),
            base_url=e.get('LLM_API_BASE_URL',GEMINI_BASE),temperature=float(e.get('LLM_TEMPERATURE','.3')),max_output_tokens=int(e.get('LLM_MAX_OUTPUT_TOKENS','4096')),
            max_calls=int(e.get('RESEARCH_MAX_CALLS','0')) or None,max_reserved_tokens=int(e.get('RESEARCH_MAX_RESERVED_TOKENS','0')) or None,
            max_cost_usd=float(e.get('RESEARCH_MAX_COST_USD','0')),free_tier_only=e.get('RESEARCH_FREE_TIER_ONLY','true').lower()=='true',allow_paid=e.get('RESEARCH_ALLOW_PAID','false').lower()=='true',min_interval=float(e.get('RESEARCH_MIN_INTERVAL_SECONDS','15')),
            max_input_bytes=int(e.get('RESEARCH_MAX_INPUT_BYTES','18000')),max_attempts=int(e.get('RESEARCH_MAX_ATTEMPTS','1')),enabled=e.get('ENABLE_EXTERNAL_API','true').lower()=='true')

    def public(self):
        return {k:v for k,v in self.__dict__.items() if k!='api_key'}

@dataclass
class Generation:
    text:str
    usage:dict
    model_version:str
    elapsed_seconds:float
    request_id:str

class LLMProvider(Protocol):
    def generate(self,system:str,prompt:str,schema:dict|None=None)->Generation:...

class BudgetLedger:
    """Conservative reservations survive failures, restarts and concurrent processes."""
    def __init__(self,path=None):
        self.path=Path(path or ROOT/'.runtime/research/budget.sqlite3');self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS calls(id TEXT PRIMARY KEY,day TEXT,started REAL,reserved_tokens INTEGER,reserved_usd REAL,status TEXT,record TEXT)')
        self.path.chmod(0o600)

    def connect(self):return sqlite3.connect(self.path,timeout=10)

    def reserve(self,config,input_bytes):
        # Bytes plus protocol allowance deliberately overestimate input tokens.
        tokens=input_bytes+1024+config.max_output_tokens
        cost=0.0  # No paid use is authorized; token/call reservations remain enforced.
        if config.model!='gemini-3.1-flash-lite' and config.provider=='Gemini':raise BudgetExceeded('Reavalie preços e limites antes de mudar o modelo do piloto.')
        day=datetime.now(timezone.utc).date().isoformat();now=time.time();identifier=uuid.uuid4().hex
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            n,total,usd,last=db.execute('SELECT COUNT(*),COALESCE(SUM(reserved_tokens),0),COALESCE(SUM(reserved_usd),0),MAX(started) FROM calls WHERE day=?',(day,)).fetchone()
            stopped=db.execute("SELECT 1 FROM calls WHERE day=? AND status IN ('http_401','http_403','http_429','http_400') LIMIT 1",(day,)).fetchone()
            if stopped:raise BudgetExceeded('Piloto interrompido hoje após erro de credencial, configuração ou cota. Não há retentativa automática.')
            if (config.max_calls is not None and n>=config.max_calls) or (config.max_reserved_tokens is not None and total+tokens>config.max_reserved_tokens) or usd+cost>config.max_cost_usd:raise BudgetExceeded('Teto diário experimental atingido; nenhuma nova chamada foi enviada.')
            if last and now-last<config.min_interval:raise BudgetExceeded(f'Aguarde {config.min_interval-(now-last):.0f} segundos antes da próxima chamada.')
            db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?)',(identifier,day,now,tokens,cost,'reserved','{}'))
        return identifier

    def finish(self,identifier,status,record):
        with self.connect() as db:db.execute('UPDATE calls SET status=?,record=? WHERE id=?',(status,json.dumps(record,ensure_ascii=False),identifier))

    def report(self):
        day=datetime.now(timezone.utc).date().isoformat()
        with self.connect() as db:
            rows=db.execute('SELECT id,started,reserved_tokens,reserved_usd,status,record FROM calls WHERE day=? ORDER BY started',(day,)).fetchall()
        return {'day_utc':day,'calls':len(rows),'reserved_tokens':sum(r[2] for r in rows),'reserved_usd':sum(r[3] for r in rows),
                'operations':[dict(id=r[0],started_utc=datetime.fromtimestamp(r[1],timezone.utc).isoformat(),reserved_tokens=r[2],reserved_usd=r[3],status=r[4],**json.loads(r[5])) for r in rows],
                'financial_policy':'Somente cota gratuita declarada pelo dono da chave; gasto autorizado zero. A API não informa o plano de cobrança. Nenhuma rotina ativa faturamento ou fallback pago. Reservas de tokens não são devolvidas em falha.'}

def redact(value,secret=''):
    if isinstance(value,dict):return {k:redact(v,secret) for k,v in value.items() if k.lower() not in ('api_key','authorization','x-goog-api-key')}
    if isinstance(value,list):return [redact(x,secret) for x in value]
    if isinstance(value,str):return value.replace(secret,'[ocultada]') if secret else value
    return value

class GeminiResearchProvider:
    def __init__(self,config=None,ledger=None,transport=None):
        self.config=config or ResearchConfig.from_env();self.ledger=ledger or BudgetLedger();self.session=transport or requests.Session()
        if hasattr(self.session,'trust_env'):self.session.trust_env=False

    def generate(self,system,prompt,schema=None):
        c=self.config
        if not c.enabled or not c.api_key:raise ResearchError('API externa não configurada; nenhuma chamada enviada.')
        if c.provider!='Gemini':raise ResearchError('Selecione o adaptador correspondente ao provedor.')
        payload={'systemInstruction':{'parts':[{'text':system}]},'contents':[{'role':'user','parts':[{'text':prompt}]}],
            'generationConfig':{'temperature':c.temperature,'maxOutputTokens':c.max_output_tokens,'thinkingConfig':{'thinkingLevel':'minimal'}}}
        if schema:payload['generationConfig'].update(responseMimeType='application/json',responseJsonSchema=schema)
        encoded=json.dumps(payload,ensure_ascii=False).encode()
        if len(encoded)>c.max_input_bytes:raise BudgetExceeded('Pedido maior que o teto de entrada; nenhuma chamada enviada.')
        for attempt in range(c.max_attempts):
            identifier=self.ledger.reserve(c,len(encoded));start=time.monotonic()
            try:
                response=self.session.post(c.base_url+'/models/'+c.model+':generateContent',headers={'x-goog-api-key':c.api_key,'Content-Type':'application/json'},json=payload,timeout=(5,60),allow_redirects=False)
                elapsed=round(time.monotonic()-start,3)
                if response.status_code!=200:
                    try:detail=response.json().get('error',{}).get('message','Solicitação recusada.')
                    except (ValueError,AttributeError):detail='Solicitação recusada.'
                    detail=redact(str(detail),c.api_key)[:600]
                    self.ledger.finish(identifier,'http_'+str(response.status_code),{'error':detail,'seconds':elapsed,'model':c.model})
                    if response.status_code in (500,502,503,504) and attempt+1<c.max_attempts:
                        time.sleep(max(c.min_interval,2**attempt));continue
                    raise ResearchError(f'Gemini HTTP {response.status_code}: '+detail)
                data=response.json();candidate=(data.get('candidates') or [{}])[0]
                text='\n'.join(p.get('text','') for p in candidate.get('content',{}).get('parts',[]) if not p.get('thought'))
                usage={k:v for k,v in data.get('usageMetadata',{}).items() if isinstance(v,(int,float))}
                record={'model':c.model,'model_version':data.get('modelVersion',c.model),'usage':usage,'finish_reason':candidate.get('finishReason'),
                    'seconds':elapsed,'prompt_sha256':hashlib.sha256(encoded).hexdigest()}
                record=redact(record,c.api_key);self.ledger.finish(identifier,'received',record)
                if candidate.get('finishReason')!='STOP' or not text.strip():raise ResearchError('Resposta vazia, bloqueada ou truncada; não aceita como problema válido.')
                return Generation(redact(text,c.api_key),usage,data.get('modelVersion',c.model),elapsed,identifier)
            except requests.RequestException:
                self.ledger.finish(identifier,'transport_error',{'error':'Falha de transporte; não houve retentativa automática.','seconds':round(time.monotonic()-start,3),'model':c.model})
                raise ResearchError('Falha de transporte na API Gemini.') from None
        raise ResearchError('Limite de tentativas atingido.')

class LocalResearchProvider:
    def __init__(self,model='llama3.2:1b'):self.model=model
    def generate(self,system,prompt,schema=None):
        from core.ollama_client import OllamaClient
        start=time.monotonic();answer=OllamaClient().chat(self.model,system,prompt,schema or False)
        if answer.get('done_reason')=='length':raise ResearchError('Saída local truncada.')
        return Generation(answer['message']['content'],{k:answer[k] for k in ('prompt_eval_count','eval_count') if k in answer},self.model,round(time.monotonic()-start,3),uuid.uuid4().hex)

def configured_provider(config=None,ledger=None):
    c=config or ResearchConfig.from_env()
    return LocalResearchProvider(c.model) if c.provider=='Ollama' else GeminiResearchProvider(c,ledger)
