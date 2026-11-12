"""Official cloud endpoints and bounded Qwen text-model catalog discovery."""
import re
import requests

DEFAULT_CLOUD_MODELS={'DeepSeek':'deepseek-flash','Qwen':'qwen-plus'}
QWEN_REGIONS={
    'Singapura':('dashscope-intl.aliyuncs.com','ap-southeast-1'),
    'Estados Unidos · Virgínia':('dashscope-us.aliyuncs.com','us-east-1'),
    'China · Pequim':('dashscope.aliyuncs.com','cn-beijing'),
    'China · Hong Kong':('cn-hongkong.dashscope.aliyuncs.com','cn-hongkong')}


class CloudProviderError(RuntimeError):
    def __init__(self,message,status_code=None):
        super().__init__(message);self.message=message;self.status_code=status_code


def cloud_url(provider,region='Singapura',workspace=''):
    if provider=='OpenAI':return 'https://api.openai.com/v1'
    if provider=='DeepSeek':return 'https://api.deepseek.com'
    if provider!='Qwen':raise CloudProviderError('Provedor incompatível com este transporte.')
    if region not in QWEN_REGIONS:raise CloudProviderError('Selecione uma região válida para a API Qwen.')
    shared,location=QWEN_REGIONS[region]
    workspace=workspace.strip()
    if workspace and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,63}',workspace):
        raise CloudProviderError('Informe somente o ID do workspace Qwen, sem endereço, pontos ou barras.')
    host=f'{workspace}.{location}.maas.aliyuncs.com' if workspace else shared
    return 'https://'+host+'/compatible-mode/v1'


def qwen_models(api_key,region='Singapura',workspace=''):
    url=cloud_url('Qwen',region,workspace).removesuffix('/compatible-mode/v1')+'/api/v1/models'
    models=set()
    with requests.Session() as session:
        for page in range(1,11):
            response=session.get(url,headers={'Authorization':'Bearer '+api_key},
                params={'providers':'qwen','capabilities':'TG','page_no':page,'page_size':100},
                timeout=(5,30),allow_redirects=False)
            if response.status_code!=200:
                try:detail=str(response.json().get('message',''))[:500]
                except (ValueError,AttributeError):detail=''
                raise CloudProviderError(detail or 'Não foi possível consultar o catálogo Qwen.',response.status_code)
            try:data=response.json()
            except ValueError as exc:raise CloudProviderError('O catálogo Qwen não retornou JSON válido.') from exc
            output=data.get('output') if isinstance(data,dict) else None
            if not isinstance(output,dict) or not isinstance(output.get('models'),list):
                raise CloudProviderError('O catálogo Qwen respondeu em formato inesperado.')
            for item in output['models']:
                if isinstance(item,dict) and isinstance(item.get('model'),str) and 1<=len(item['model'])<=200:models.add(item['model'])
            total=output.get('total',0)
            if not output['models'] or (isinstance(total,int) and page*100>=total):break
        else:raise CloudProviderError('O catálogo excedeu 1000 modelos. Informe o ID do modelo manualmente.')
    return sorted(models)
