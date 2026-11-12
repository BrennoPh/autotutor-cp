import pytest
from core.research.lessons import expected_answer,validate_lesson
from core.research.provider import ResearchError

@pytest.mark.parametrize('target,answer',[('Soma de prefixos',[2,2]),('BFS',[0,1,1,2]),('DP',[5]),('Fundamentos e simulação',[4])])
def test_independent_lesson_examples(target,answer):
    assert expected_answer(target)==answer

def test_invalid_example_or_topic_is_rejected_before_publication():
    value={'title':'Prefixos','topic':'Prefix Sum','sections':[{'heading':'Parte','body':'Texto'}]*4,'example_id':'prefix-01','answer':[2,2],'example_reasoning':'Subtrair prefixos nas fronteiras.','source_labels':['1']}
    assert validate_lesson(value,'Soma de prefixos',['1'])['numerical_example_valid']
    for key,bad in [('topic','DP'),('answer',[8]),('source_labels',['invented'])]:
        with pytest.raises(ResearchError):validate_lesson({**value,key:bad},'Soma de prefixos',['1'])
