"""Presentation preferences for generated study material, shared by UI and tutor."""
LENGTHS={'Curto':(150,250),'Médio':(350,550),'Longo':(1000,1600)}
DEPTHS={
    'Visão geral':'Explique a intuição e os pontos essenciais em linguagem simples, sem provas formais ou detalhes de implementação desnecessários.',
    'Passo a passo':'Desenvolva cada ideia em ordem, explique os termos novos e mostre o raciocínio das etapas, sem saltos.',
    'Aprofundada':'Inclua definição precisa, invariantes ou justificativa de correção quando aplicáveis, complexidade, limites e erros sutis.'}
DEFAULT_PREFERENCES={'learning_request':'','material_length':'Longo','material_depth':'Aprofundada',
                     'material_target_chars':5000,'material_examples':True,'material_exercises':True}
