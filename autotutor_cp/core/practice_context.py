"""Carry the explicit study objective across reading, search, and practice screens."""

def study_context(item):
    payload=item.get('payload',{})
    request=payload.get('learning_request') or payload.get('retrieval_query') or item.get('title') or payload.get('concept','')
    return dict(request=str(request)[:2000],concept=payload.get('concept',''),level=payload.get('level','Iniciante'),theme=payload.get('theme',''),source_id=item.get('id'),source_title=item.get('title',''))


def queue_practice(state,context,go):
    state['pending_practice']=dict(context)
    state['pending_learning_request']=context['request']
    state['pending_concept']=context.get('concept','')
    go('Laboratório IA')
