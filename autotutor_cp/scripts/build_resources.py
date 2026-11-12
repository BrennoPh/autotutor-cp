import json,hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.learning_engine import load_curriculum
from core.catalog import STUDY_SOURCES
rows={}
def add(title,url,topics,kind,publisher,summary,source_url=None,verification='Página consultada',language='Inglês'):
 key=hashlib.sha256(url.encode()).hexdigest()[:16]
 if key in rows:rows[key]['topics']=sorted(set(rows[key]['topics'])|set(topics));return
 rows[key]=dict(id='ref_'+key,title=title,url=url,topics=topics,kind=kind,publisher=publisher,summary=summary,source_url=source_url or url,verification=verification,language=language,checked='2026-10-24')
for t in load_curriculum():
 for v in t['videos']:add(v['title'],v['url'],[t['id']],'Vídeo',v['publisher'],'Aula complementar ao módulo. Ao assistir, anote o invariante apresentado e reconstrua um exemplo sem consultar o vídeo.',v['source_url'],'Link conferido no catálogo de aulas',v['language'])
usaco=[
('fundamentals','Complexidade de tempo','bronze/time-comp','Como estimar o crescimento do trabalho a partir das operações e restrições. Use para comparar uma varredura com dois laços aninhados.'),
('fundamentals','Tipos de dados','general/data-types','Referência de tipos numéricos e limites de representação. Relacione o maior valor intermediário ao tipo usado.'),
('fundamentals','Entrada e saída','general/input-output','Guia de leitura e impressão para concursos. Compare o formato exigido com cada operação de entrada de seu programa.'),
('fundamentals','Como depurar','general/debugging-checklist','Checklist organizado por falhas de compilação, resposta, execução e tempo. Use o veredito para formular uma hipótese verificável.'),
('fundamentals','Como praticar','general/practicing','Discussão sobre dificuldade adequada e leitura de editoriais. Inclui perspectivas de diferentes competidores; não é uma regra única de estudo.'),
('fundamentals','Busca completa','bronze/intro-complete','Enumeração de possibilidades como ponto de partida. Uma implementação simples também pode servir de comparação para uma abordagem otimizada.'),
('structures','Introdução às estruturas de dados','bronze/intro-ds','Arrays, vetores, pares e organização de dados. Escolha a estrutura a partir das operações necessárias.'),
('structures','Conjuntos e mapas','bronze/intro-sets','Presença de chaves e valores associados. Compare conjunto de valores distintos com mapa de frequências.'),
('greedy','Introdução à ordenação','bronze/intro-sorting','Como reorganizar coleções e usar critérios de ordenação. Avalie se a pergunta original depende da ordem de entrada.'),
('prefix','Introdução a somas de prefixos','silver/prefix-sums','Pré-processamento linear para somas de intervalos constantes. O módulo contém exemplos e prática adicional.'),
('binary','Busca binária e funções monotônicas','silver/binary-search','Busca de uma fronteira verdadeira ou falsa, com cuidados de índices e aritmética. Escreva o predicado antes do laço.'),
('greedy','Guloso com ordenação','silver/greedy-sorting','Agendamento, escolhas locais e exemplos em que estratégias gulosas falham. Procure a justificativa de cada critério.'),
('dp','Introdução à programação dinâmica','gold/intro-dp','Subproblemas, repetição de cálculos e ordens de transição. O módulo reúne referências escritas e em vídeo.'),
('graph','Introdução a grafos','bronze/intro-graphs','Representações por listas de adjacência e modelagem de conexões. Desenhe vértices e arestas antes de escolher a busca.'),
('graph','Travessias em grafos','silver/graph-traversal','DFS, BFS, componentes e coloração. Relacione ordem de visita ao objetivo de alcançabilidade ou distância.'),
('tree','Introdução a árvores','silver/intro-tree','Terminologia, travessia e agregação de subárvores. Diferencie descendentes e tamanho da subárvore.')]
for topic,title,path,summary in usaco:add(title,'https://usaco.guide/'+path,[topic],'Artigo','USACO Guide / CP Initiative',summary)
for topic,title,path,summary in [
('math','Exponenciação binária','algebra/binary-exp.html','Potências por quadrados sucessivos e aplicações modulares. Leitura para depois de entender escolhas independentes.'),
('math','Algoritmo de Euclides','algebra/euclid-algorithm.html','MDC por restos sucessivos e relação com MMC. Verifique a ordem das operações para evitar produtos desnecessariamente grandes.'),
('structures','Árvore de segmentos','data_structures/segment_tree.html','Consultas e atualizações por decomposição hierárquica de intervalos. Comece pela versão de soma ou mínimo antes das extensões.'),
('graph','Busca em largura','graph/breadth-first-search.html','Percurso em camadas para grafos sem pesos e aplicações. Compare sua fila com a ordem das distâncias.'),
('dp','Introdução à DP','dynamic_programming/intro-to-dp.html','Memorização e programação por estados em ordem de dependência. Compare recursão com implementação iterativa.')]:add(title,'https://cp-algorithms.com/'+path,[topic],'Artigo','CP-Algorithms',summary)
for title,url,topic,source in [
('DP: Fibonacci, iteração e recursão','https://www.youtube.com/watch?v=YBSt1jYwVfU','dp','https://usaco.guide/gold/intro-dp'),
('Busca binária em C++ e Python','https://www.youtube.com/watch?v=GU7DpgHINWQ','binary','https://usaco.guide/silver/binary-search')]:add(title,url,[topic],'Vídeo','Errichto','Videoaula recomendada no módulo correspondente do USACO Guide. Conteúdo em inglês; pratique o conceito depois de assistir.',source,'Link conferido no módulo de referência')
for title,vid,topics in [('Árvores de segmentos e lazy propagation','38n2Xv6gt1M',['structures']),('Matemática: prática','u3zkf9LsEnM',['math']),('Grafos e conjuntos disjuntos','gv9xUsJvVso',['graph','structures']),('Bitwise e técnicas em matrizes','-XoeqOOMxoU',['math','prefix'])]:add(title,'https://www.youtube.com/watch?v='+vid,topics,'Vídeo','AoCPC Community','Aula listada no catálogo de aprendizagem do AoCPC. Use como aprofundamento após o módulo introdutório.','https://aocpc-community.github.io/aocpc-guide/guide/aprender/','Link conferido no catálogo de aulas','Português')
for r in STUDY_SOURCES:
 verification='Recurso indicado pelo usuário; conteúdo não inspecionado' if r['name'] in ('YouKn0wWho Academy','TLE Eliminators CP Sheet') else 'Página da plataforma consultada'
 source='https://dcc.ufmg.br/canal-maratona-do-dcc-ufmg-ensina-algoritmos-e-estruturas-de-dados-de-forma-gratuita/' if r['name']=='Maratona UFMG' else r['url']
 if r['name']=='Maratona UFMG':verification='Canal confirmado pela página oficial do DCC/UFMG'
 add(r['name'],r['url'],[],'Canal' if r['name']=='Maratona UFMG' else 'Site',r['name'],r['description'],source,verification,'Português' if r['name'] in ('Maratona UFMG','Neps Academy') else 'Vários')
add('Curso Silver em vídeo','https://joincpi.org/silver-video-classes',['prefix','binary','greedy','graph','tree'],'Curso','CP Initiative','Curso autoguiado com aulas em vídeo e módulos correspondentes do USACO Guide. A página oficial informa acesso gratuito.')
(Path(__file__).resolve().parents[1]/'data/study_resources.json').write_text(json.dumps({'version':1,'checked':'2026-10-24','resources':list(rows.values())},ensure_ascii=False,indent=2))
print(len(rows),'referências únicas')
