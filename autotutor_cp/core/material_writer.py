"""Size-aware offline study material assembled from authored, reviewed lessons."""
import re
import unicodedata
from html import escape


TOPIC_DIAGRAMS = {
    'graph': (
        '#### Estrutura Visual do Grafo de Exemplo\n'
        '```mermaid\n'
        'graph LR\n'
        '  A((A)) --- B((B))\n'
        '  A --- C((C))\n'
        '  B --- D((D))\n'
        '  C --- E((E))\n'
        '  E --- F((F))\n'
        '```\n\n'
        '#### Árvore de Expansão BFS (Camadas de Distância)\n'
        '```mermaid\n'
        'graph TD\n'
        '  A["A (d=0)"] --> B["B (d=1)"]\n'
        '  A --> C["C (d=1)"]\n'
        '  B --> D["D (d=2)"]\n'
        '  C --> E["E (d=2)"]\n'
        '  E --> F["F (d=3)"]\n'
        '```\n\n'
        '#### Classificação das 4 Arestas na DFS e Detecção de Ciclo\n'
        '```mermaid\n'
        'graph TD\n'
        '  U["U (ancestral cinza)"] -->|Tree Edge: descobre novo no| V["V (filho cinza)"]\n'
        '  V -->|Tree Edge: descobre novo no| W["W (neto cinza)"]\n'
        '  W -.->|Back Edge: CICLO! aponta para ancestral cinza| U\n'
        '  U ==>|Forward Edge: descende na arvore| W\n'
        '  X["X (ramo vizinho preto)"] -.->|Cross Edge: entre ramos| W\n'
        '```'
    ),
    'tree': (
        '#### Estrutura Visual da Árvore\n'
        '```mermaid\n'
        'graph TD\n'
        '  R["1 (Raiz)"] --> A["2"]\n'
        '  R --> B["3"]\n'
        '  A --> C["4"]\n'
        '  A --> D["5"]\n'
        '  B --> E["6"]\n'
        '```'
    ),
    'dp': (
        '#### Fluxo de Dependência de Estados (DP)\n'
        '```mermaid\n'
        'graph LR\n'
        '  DP0["dp[0] (Base)"] --> DP1["dp[1]"]\n'
        '  DP1 --> DP2["dp[2]"]\n'
        '  DP0 --> DP2\n'
        '  DP2 --> DPN["dp[i] = transição"]\n'
        '```'
    ),
    'prefix': (
        '#### Intervalo com Soma de Prefixos\n'
        '```mermaid\n'
        'graph LR\n'
        '  P0["P[0] = 0"] --> PL["P[L-1]"]\n'
        '  PL --> PR["P[R]"]\n'
        '  PR -.->|Soma(L, R) = P[R] - P[L-1]| RES["Resultado em O(1)"]\n'
        '```'
    ),
    'binary': (
        '#### Espaço de Busca Binária Monótona\n'
        '```mermaid\n'
        'graph LR\n'
        '  L["L (Início)"] --> M["MID (Ponto Médio)"]\n'
        '  M --> R["R (Fim)"]\n'
        '  M -->|Viável? Sim| Rnew["R = MID - 1"]\n'
        '  M -->|Viável? Não| Lnew["L = MID + 1"]\n'
        '```'
    ),
    'structures': (
        '#### Estrutura: Pilha (LIFO) vs Fila (FIFO)\n'
        '```mermaid\n'
        'graph TD\n'
        '  subgraph Pilha [Pilha LIFO]\n'
        '    P3["Topo: 3"] --> P2["2"] --> P1["Base: 1"]\n'
        '  end\n'
        '  subgraph Fila [Fila FIFO]\n'
        '    F1["Frente: 1"] --> F2["2"] --> F3["Fundo: 3"]\n'
        '  end\n'
        '```'
    )
}


def local_material(lesson,guide,kind,level,theme,request,length,depth,examples,exercises,prereq_decision=None):
    from core.prerequisites import detect_prerequisites, build_prerequisite_primer_markdown
    def words(value):
        value=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()
        return set(re.findall(r'[a-z0-9]{3,}',value))-{'que','para','como','uma','com','sobre','quero','aprender','explique','entender'}
    terms=words(request)
    sections=list(lesson['sections'])
    if depth!='Visão geral':sections+=list(guide['sections'])
    elif length=='Longo':sections+=list(guide['sections'][:2])
    sections=sorted(enumerate(sections),key=lambda pair:(-len(terms & words(pair[1]['title']+' '+pair[1]['body'])),pair[0]))
    count={'Curto':1,'Médio':3,'Longo':len(sections)}[length]
    if depth=='Aprofundada' and length=='Médio':count=4
    if kind=='Exemplo Comentado' and examples:count=min(count,{'Curto':1,'Médio':2,'Longo':4}[length])
    if kind=='Exercício Prático' and exercises:count=min(count,{'Curto':1,'Médio':2,'Longo':4}[length])
    chosen=[s for _,s in sections[:count]]
    parts=[f'## {lesson["title"]} · {kind}',f'**Nível:** {level} · **Tamanho:** {length} · **Profundidade:** {depth}.']
    if theme:parts.append('**Tema de prática:** '+escape(theme))
    if request:
        parts.append('**Seu objetivo:** '+escape(request))
        parts.append('**Material local:** a seleção abaixo usa o acervo deste assunto como ponto de partida. Uma resposta personalizada ao seu pedido específico requer um motor de IA conectado.')
    parts.append(lesson['summary'])
    if prereq_decision == 'explain':
        prereqs = detect_prerequisites(request, lesson.get('title', ''))
        if prereqs:
            parts.append(build_prerequisite_primer_markdown(prereqs[0]))
    for section in chosen:parts.extend(['### '+section['title'],section['body']])
    if examples:
        example=lesson['example'];parts.extend(['### Exemplo passo a passo',example['story']])
        if length!='Curto' and lesson.get('id') in TOPIC_DIAGRAMS:
            parts.append(TOPIC_DIAGRAMS[lesson['id']])
        if length!='Curto':parts.extend(f'{i}. {line}' for i,line in enumerate(example['trace'],1))
        if depth!='Visão geral' and length!='Curto':parts.append('```cpp\n'+example['code']+'\n```')
    if length=='Longo' and depth!='Visão geral':
        parts.extend(['### Cuidados importantes']+['- '+p for p in lesson['pitfalls']])
    if exercises:
        parts.append('### Exercícios para conferir sua compreensão')
        if kind=='Exercício Prático':parts.append(lesson['challenge'])
        for exercise in guide['exercises'][:1 if length=='Curto' else 2]:parts.append('- '+exercise['prompt'])
        if length=='Longo':
            parts.append({'Iniciante':'Trace uma entrada pequena e explique cada mudança de estado.',
                          'Intermediário':'Justifique o invariante e compare com uma estratégia ingênua.',
                          'Avançado':'Demonstre a correção, crie um caso adversarial e discuta os limites da técnica.'}[level])
    return '\n\n'.join(parts)
