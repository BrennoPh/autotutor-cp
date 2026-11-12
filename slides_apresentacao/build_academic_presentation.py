import os
from PIL import Image, ImageDraw, ImageFont
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

ASSETS_DIR = 'slides_apresentacao/assets'
OUT_DIR = 'slides_apresentacao/academic_png'
os.makedirs(OUT_DIR, exist_ok=True)

# Paleta de Altíssimo Contraste para Projeção em Quadro Branco no Escuro
# Fundo: Deep Navy/Carbon (0A0F1D)
# Texto Principal: Branco Puro (FFFFFF)
# Destaque 1 (Títulos/Métricas): Amarelo Laser / Alta Luminância (FACC15)
# Destaque 2 (Invariantes/Badges): Ciano Elétrico (38BDF8)
# Destaque 3 (Validação/Sucesso): Verde Esmeralda Alta Visibilidade (34D399)
# Texto Secundário: Prata Claro (E2E8F0) - Jamais cinza escuro apagado!
BG_COLOR = (10, 15, 29)
CARD_BG = (21, 31, 50)
BORDER_COLOR = (71, 85, 105)
BORDER_CYAN = (56, 189, 248)
BORDER_YELLOW = (250, 204, 21)
TEXT_WHITE = (255, 255, 255)
TEXT_SILVER = (226, 232, 240)
TEXT_YELLOW = (250, 204, 21)
TEXT_CYAN = (56, 189, 248)
TEXT_EMERALD = (52, 211, 153)
TEXT_ROSE = (251, 113, 133)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title = get_font(36, bold=True)
font_sub = get_font(20, bold=False)
font_badge = get_font(16, bold=True)
font_card_h = get_font(22, bold=True)
font_card_b = get_font(17, bold=False)
font_code = get_font(16, bold=True)
font_footer = get_font(15, bold=False)

academic_slides = [
    {
        "num": 1,
        "time": "00:00 - 00:35 (35s)",
        "badge": "FORMULAÇÃO DO PROBLEMA CIENTÍFICO",
        "title": "AutoTutor CP: Tutoria Inteligente e Verificação Formal em Algoritmos",
        "subtitle": "O abismo cognitivo entre a prova teórica e a correção assintótica no julgamento automático",
        "type": "custom_cards",
        "script": """\"Boa tarde aos membros da banca avaliadora. Na disciplina de Fundamentos da Inteligência Artificial, investigamos o problema da formação analítica em Ciência da Computação.

Existe uma lacuna estrutural no aprendizado de algoritmos avançados: juízes online operam com vereditos booleanos opacos como Wrong Answer, sem explicitar a quebra do invariante lógico. Em contrapartida, LLMs genéricas entregam o código pronto, suprimindo o esforço cognitivo do discente e induzindo à atrofia do raciocínio analítico.

O AutoTutor CP investiga e formaliza a integração entre execução determinística em sandbox C++, recuperação semântica por invariantes e mediação dialógica socrática.\""""
    },
    {
        "num": 2,
        "time": "00:35 - 01:10 (35s)",
        "badge": "FUNDAMENTAÇÃO TEÓRICA",
        "title": "A Tríade de Pesquisa: Fundamentação na Literatura Internacional",
        "subtitle": "Três pilares formais recentes em conferências de ponta (ICLR, IOI, IEEE VL/HCC)",
        "type": "custom_cards",
        "script": """\"Nossa arquitetura fundamenta-se estritamente na literatura científica recente:

Primeiro, o AutoCode (publicado no ICLR 2026), que estabelece a validação por oráculo duplo: instâncias de problemas e baterias de testes de estresse são compiladas e verificadas cruzadamente antes da apresentação ao estudante, assegurando corretude matemática formal.

Segundo, o OI-Assistant (IOI 2025), que propõe a recuperação estruturada por propriedades matemáticas profundas e classes assintóticas.

E terceiro, o CODIGEN (IEEE 2025), que formaliza a escada gradual de pistas socráticas sem alucinação de sintaxe.\""""
    },
    {
        "num": 3,
        "time": "01:10 - 01:55 (45s)",
        "badge": "ANÁLISE CRÍTICA DE IA",
        "title": "Limitações Estruturais: Por Que o RAG Convencional Falha em Algoritmos?",
        "subtitle": "A falácia da similaridade léxica, insensibilidade assintótica e vazamento precoce de soluções",
        "type": "custom_cards",
        "script": """\"Uma contribuição central deste trabalho é demonstrar por que o RAG clássico falha em domínios algorítmicos:

Primeiro: a falácia da proximidade léxica. Dois problemas que utilizam a mesma narrativa metafórica — por exemplo, uma malha rodoviária rural — são agrupados no espaço denso genérico por causa das palavras superficiais. No entanto, um deles exige caminho mínimo O(E log V) via Dijkstra, enquanto o outro exige corte mínimo e fluxo máximo em O(V^2 E) via algoritmo de Dinic. O RAG tradicional recupera o paradigma incorreto.

Segundo: a insensibilidade assintótica. Limites de N <= 20 demandam busca com bitmask O(2^N * N), enquanto N <= 10^5 exige busca binária ou programação dinâmica com Convex Hull Trick. O RAG clássico é cego a ordens de grandeza.

Terceiro: o vazamento de gabaritos. O RAG convencional injeta a solução no prompt, gerando respostas prontas que anulam o ganho pedagógico.\""""
    },
    {
        "num": 4,
        "time": "01:55 - 02:40 (45s)",
        "badge": "METODOLOGIA PROPOSTA",
        "title": "Metodologia: RAG Multiespaço por Invariantes e Reranking Semântico",
        "subtitle": "Decomposição em 3 espaços vetoriais ortogonais e validação matemática de corretude",
        "type": "custom_cards",
        "script": """\"Para mitigar essas limitações, implementamos a arquitetura multiespaço inspirada no OI-Assistant, decompondo a representação em três espaços vetoriais ortogonais:

Espaço 1: Enunciados Formais, que isola a especificação matemática do ruído narrativo.
Espaço 2: Conceitos Algorítmicos e Invariantes, indexando propriedades de monotonicidade, subestrutura ótima e dualidade.
Espaço 3: Resumos Estruturais e Limites, que modela restrições temporais de 1.0 a 2.0 segundos e memória de 256 megabytes.

Calculamos uma métrica de similaridade linearmente ponderada, seguida de reranking semântico via LLM, garantindo que o exercício análogo compartilhe a mesma assinatura assintótica.\""""
    },
    {
        "num": 5,
        "time": "02:40 - 03:20 (40s)",
        "badge": "MODELAGEM LONGITUDINAL",
        "title": "AI Memory Longitudinal e Engenharia de Prompt Formal",
        "subtitle": "Persistência de perfil cognitivo em SQLite e contenção estrita de prompt injection",
        "type": "custom_cards",
        "script": """\"O sistema elimina a volatilidade de sessões efêmeras através do pipeline de AI Memory: um ciclo contínuo de Captura de falhas, Consolidação de padrões de dificuldade, Recuperação contextual e Handoff entre agentes, persistido com transações ACID em SQLite.

Na Engenharia de Prompt, empregamos delimitação XML estrita (<role>, <context>, <constraints>) e guardrails matemáticos de Zero-Leakage.

Mesmo sob ataques deliberados de injeção de prompt simulados em nossa suíte com a persona adversarial Diana, o tutor intercepta a tentativa e mantém rigorosamente a postura dialógica socrática.\""""
    },
    {
        "num": 6,
        "time": "03:20 - 04:05 (45s)",
        "badge": "EVIDÊNCIAS EXPERIMENTAIS (SISTEMA REAL)",
        "title": "Evidências Empíricas: O Workspace de Execução e o Quadro Branco",
        "subtitle": "Sandbox C++17 com limites POSIX, detecção determinística de TLE/WA e visualização de grafos",
        "type": "system_screenshots_1",
        "script": """\"Apresentamos aqui as evidências empíricas da plataforma em operação real:

À esquerda, o Workspace de Resolução: integra o editor Monaco em C++17 sob sandbox isolado pelo isolated_judge.py com Bubblewrap e limites POSIX de 256MB. O console demonstra a captura determinística de Time Limit Exceeded em um laço quadrático, acionando o AI Tutor no dock lateral com dicas socráticas orientadas por invariantes.

À direita, o Quadro Branco Algorítmico: o aluno projeta o grafo topológico acoplado à execução C++. Conforme o algoritmo de busca percorre os vértices, os estados mudam de cor e a Call Stack de recursão é renderizada ao vivo, tornando observável a dinâmica de memória e o backtracking.\""""
    },
    {
        "num": 7,
        "time": "04:05 - 04:40 (35s)",
        "badge": "DIAGNÓSTICO E ADAPTAÇÃO",
        "title": "Diagnóstico Cognitivo e Escalonamento Espaçado (Ebbinghaus)",
        "subtitle": "Micro-quiz objetivo de código e agendamento adaptativo de repetição espaçada",
        "type": "system_screenshots_2",
        "script": """\"Para fundamentar a adaptação pedagógica sem autoavaliações ilusórias, o sistema implementa:

À esquerda, o Onboarding Diagnóstico: micro-quiz calibrado com trechos formais de código avaliando Programação Dinâmica, Grafos, Busca Binária e Soma de Prefixos. O algoritmo mapeia com precisão as lacunas conceituais do discente.

À direita, o Calendário Adaptativo: o motor projeta um cronograma baseado na curva de esquecimento de Ebbinghaus, intercalando leitura analítica no Study Reader e desafios práticos na Arena, respeitando a carga horária do estudante.\""""
    },
    {
        "num": 8,
        "time": "04:40 - 05:00 (20s)",
        "badge": "VALIDAÇÃO FORMAL E CONCLUSÕES",
        "title": "Validação Empírica, Limitações e Arguição da Banca",
        "subtitle": "365 testes Pytest (100% pass), simulação com 1.000.000 de discentes sintéticos e trabalho futuro",
        "type": "custom_cards",
        "script": """\"Para homologar a integridade matemática da solução, submetemos a arquitetura a uma suíte de 365 testes unitários e de integração no Pytest com 100% de aprovação, e simulamos 1 milhão de discentes sintéticos cobrindo 3 milhões de jornadas completas sem quebra de invariantes.

Como limitação, identificamos a latência do reranking em modelos de grande porte, contornável via destilação local.

Agradecemos a atenção da banca examinadora e estamos abertos para a discussão técnica e metodológica.\""""
    }
]

# --------------------------------------------------------------------------
# Renderização dos Slides 1 a 5 e 8 (Diagramas Científicos de Alto Contraste)
# --------------------------------------------------------------------------

def draw_header(draw, s, W=1920):
    # Badge do Topo
    draw.rounded_rectangle([60, 30, 60 + len(s["badge"])*12 + 40, 72], radius=8, fill=CARD_BG, outline=BORDER_CYAN, width=2)
    draw.text((80, 40), s["badge"], fill=TEXT_CYAN, font=font_badge)

    # Cronômetro
    time_w = len(s["time"]) * 11 + 35
    draw.rounded_rectangle([W - 60 - time_w, 30, W - 60, 72], radius=8, fill=CARD_BG, outline=BORDER_YELLOW, width=2)
    draw.text((W - 45 - time_w, 40), f"⏱ {s['time']}", fill=TEXT_YELLOW, font=font_badge)

    # Título & Subtítulo
    draw.text((60, 95), s["title"], fill=TEXT_WHITE, font=font_title)
    draw.text((60, 150), s["subtitle"], fill=TEXT_SILVER, font=font_sub)

def draw_footer(draw, s, W=1920, H=1080):
    draw.line([60, H - 70, W - 60, H - 70], fill=BORDER_COLOR, width=1)
    draw.text((60, H - 52), "AutoTutor CP — Arquitetura de Tutoria Inteligente e Verificação Formal em Algoritmos (FIA 2026)", fill=TEXT_SILVER, font=font_footer)
    draw.text((W - 130, H - 52), f"Slide {s['num']} / 8", fill=TEXT_YELLOW, font=font_footer)

def build_slide_1(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    cards = [
        {
            "x": 60, "w": 560,
            "badge": "ESTADO DA PRÁTICA 1",
            "badge_color": TEXT_ROSE,
            "title": "Juízes Online Tradicionais",
            "mock": "Verdict: Wrong Answer (Test 4)\nTempo: 0.12s | Memória: 12.4MB\n[Nenhum log explicativo emitido]",
            "bullets": [
                "• Verificação booleana puramente opaca.",
                "• Não identifica a quebra da invariante lógica.",
                "• Distância crítica entre a teoria e a correção.",
                "• Frustração discente e descontinuidade do estudo."
            ],
            "conclusion": "Problema: Diagnóstico Inexistente",
            "concl_color": TEXT_ROSE
        },
        {
            "x": 680, "w": 560,
            "badge": "ESTADO DA PRÁTICA 2",
            "badge_color": TEXT_YELLOW,
            "title": "Modelos Fundacionais Genéricos",
            "mock": "\"Aqui está o código completo em C++\nutilizando Dijkstra com priority_queue\ne vetor de distâncias...\"",
            "bullets": [
                "• Fornece a resolução algorítmica integral.",
                "• Elimina a necessidade de abstração do aluno.",
                "• Induz a uma ilusão precoce de competência.",
                "• Provoca atrofia no raciocínio assintótico."
            ],
            "conclusion": "Problema: Atrofia Cognitiva por Cópia",
            "concl_color": TEXT_YELLOW
        },
        {
            "x": 1300, "w": 560,
            "badge": "PROPOSTA CIENTÍFICA",
            "badge_color": TEXT_EMERALD,
            "title": "AutoTutor CP (Arquitetura Proposta)",
            "mock": "\"Observe o laço na linha 14: a busca linear\né repetida a cada consulta. Qual propriedade\nde prefixo permite consulta em O(1)?\"",
            "bullets": [
                "• Execução confinada com limites POSIX rígidos.",
                "• Recuperação semântica baseada em invariantes.",
                "• Escada de pistas socráticas sem spoiler de código.",
                "• Consolidação de memória longitudinal discente."
            ],
            "conclusion": "Contribuição: Mediação Dialógica Ativa",
            "concl_color": TEXT_EMERALD
        }
    ]

    card_y = 205
    card_h = 780

    for c in cards:
        x, w = c["x"], c["w"]
        draw.rounded_rectangle([x, card_y, x + w, card_y + card_h], radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
        
        # Badge
        draw.rounded_rectangle([x + 24, card_y + 24, x + len(c["badge"])*11 + 45, card_y + 60], radius=8, fill=BG_COLOR, outline=c["badge_color"], width=1)
        draw.text((x + 36, card_y + 32), c["badge"], fill=c["badge_color"], font=font_badge)

        draw.text((x + 24, card_y + 80), c["title"], fill=TEXT_WHITE, font=font_card_h)

        # Mock terminal/code box
        draw.rounded_rectangle([x + 24, card_y + 130, x + w - 24, card_y + 250], radius=10, fill=BG_COLOR, outline=BORDER_COLOR, width=1)
        draw.text((x + 38, card_y + 145), c["mock"], fill=TEXT_SILVER, font=font_code)

        y_text = card_y + 280
        for b in c["bullets"]:
            draw.text((x + 24, y_text), b, fill=TEXT_WHITE, font=font_card_b)
            y_text += 60

        draw.rounded_rectangle([x + 24, card_y + card_h - 75, x + w - 24, card_y + card_h - 25], radius=10, fill=BG_COLOR, outline=c["concl_color"], width=2)
        draw.text((x + 40, card_y + card_h - 60), c["conclusion"], fill=c["concl_color"], font=font_card_h)

    draw_footer(draw, s)
    return img

def build_slide_2(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    pillars = [
        {
            "x": 60, "w": 560,
            "conf": "ICLR 2026",
            "conf_color": TEXT_CYAN,
            "title": "AutoCode",
            "sub": "Validação Formal por Oráculo Duplo",
            "cit": "Zhou et al. (ICLR 2026 / arXiv:2510.12803)",
            "bullets": [
                "1. Síntese do Par Problema-Oráculo:\n   Geração do enunciado formal, solução canônica\n   e gerador sintético de casos de estresse.",
                "2. Compilação Cruzada Prévia:\n   Se o oráculo não atinge veredito AC nos testes,\n   a instância é descartada pelo pipeline.",
                "3. Teorema de Confiabilidade:\n   Garantia matemática de ausência de problemas\n   inválidos ou testes mal calibrados."
            ]
        },
        {
            "x": 680, "w": 560,
            "conf": "IOI 2025",
            "conf_color": TEXT_YELLOW,
            "title": "OI-Assistant",
            "sub": "RAG Estruturado por Invariantes",
            "cit": "Su, Nie & Meng (Olympiads in Informatics, 2025)",
            "bullets": [
                "1. Ruptura com Embeddings Superficiais:\n   Desacopla a historinha do problema da sua\n   assinatura assintótica e invariantes.",
                "2. Três Espaços Vetoriais Ortogonais:\n   Enunciados Formais, Conceitos Matemáticos e\n   Resumos Estruturais com TF-IDF especializado.",
                "3. Transferência de Domínio:\n   Identificação do núcleo algorítmico idêntico\n   sob diferentes cenários de aplicação."
            ]
        },
        {
            "x": 1300, "w": 560,
            "conf": "IEEE VL/HCC 2025",
            "conf_color": TEXT_EMERALD,
            "title": "CODIGEN",
            "sub": "Scaffolding Socrático Adaptativo",
            "cit": "Ez-zaouia & Boumarafi (IEEE VL/HCC 2025)",
            "bullets": [
                "1. Escada Gradual de Pistas (Scaffolding):\n   Pista 1: Conceitual (propriedade matemática)\n   Pista 2: Estrutural (estrutura de dados)\n   Pista 3: Assintótica (análise do laço crítico).",
                "2. Guardrails de Zero-Leakage:\n   Barreiras formais de contenção contra vazamento\n   acidental do código-fonte de resolução.",
                "3. Autoria Visual de Algoritmos:\n   Ancoragem espacial de memória e execução."
            ]
        }
    ]

    card_y = 205
    card_h = 780

    for p in pillars:
        x, w = p["x"], p["w"]
        draw.rounded_rectangle([x, card_y, x + w, card_y + card_h], radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
        
        draw.rounded_rectangle([x + 24, card_y + 24, x + len(p["conf"])*14 + 30, card_y + 60], radius=8, fill=BG_COLOR, outline=p["conf_color"], width=2)
        draw.text((x + 36, card_y + 32), p["conf"], fill=p["conf_color"], font=font_badge)

        draw.text((x + 24, card_y + 80), p["title"], fill=TEXT_WHITE, font=font_card_h)
        draw.text((x + 24, card_y + 115), p["sub"], fill=TEXT_YELLOW, font=font_card_b)
        draw.text((x + 24, card_y + 145), p["cit"], fill=TEXT_CYAN, font=font_footer)

        draw.line([x + 24, card_y + 175, x + w - 24, card_y + 175], fill=BORDER_COLOR, width=1)

        y_text = card_y + 200
        for b in p["bullets"]:
            draw.text((x + 24, y_text), b, fill=TEXT_WHITE, font=font_card_b)
            y_text += 160

    draw_footer(draw, s)
    return img

def build_slide_3(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    cards = [
        {
            "x": 60, "w": 560,
            "badge": "LIMITAÇÃO 1 · SEMÂNTICA",
            "badge_color": TEXT_ROSE,
            "title": "A Falácia da Similaridade Léxica",
            "desc": "Problemas de programação competitiva utilizam narrativas metafóricas ('fazendas com vacas e estradas').",
            "case": "CASO CONCRETO:\n• Problema A: Caminho Mínimo simples em grafo (Dijkstra - O(E log V)).\n• Problema B: Corte Mínimo e Capacidade de Fluxo (Dinic - O(V^2 E)).\n• Resultado RAG Comum: Proximidade vetorial aproxima as palavras 'fazenda' e 'estrada', recuperando o algoritmo totalmente errado.",
            "impact": "Falha Crítica: Divergência de Paradigma Algorítmico"
        },
        {
            "x": 680, "w": 560,
            "badge": "LIMITAÇÃO 2 · ASSINTÓTICA",
            "badge_color": TEXT_YELLOW,
            "title": "Insensibilidade à Ordem de Grandeza",
            "desc": "O RAG tradicional baseia-se em embeddings que tratam restrições numéricas de N como tokens semânticos ordinários.",
            "case": "DISCRIMINAÇÃO ASSINTÓTICA:\n• Se N <= 20: Espaço de busca exponencial 2^N. Solução correta é Bitmask Brute-force.\n• Se N <= 10^5: Solução requer O(N log N) via Programação Dinâmica com Convex Hull.\n• Resultado RAG Comum: Cego para o limiar de complexidade assintótica.",
            "impact": "Falha Crítica: Solução Inviável por TLE / MLE"
        },
        {
            "x": 1300, "w": 560,
            "badge": "LIMITAÇÃO 3 · PEDAGÓGICA",
            "badge_color": TEXT_CYAN,
            "title": "Vazamento Precoce e Alucinação",
            "desc": "Arquiteturas RAG ingênuas injetam o gabarito completo no contexto da LLM para síntese de resposta.",
            "case": "EFEITO COLATERAL:\n• A LLM cospe o código C++ pronto para o aluno.\n• O aluno atinge veredito AC sem construir o modelo mental do invariante.\n• Alucinação de bibliotecas inexistentes em C++17 puro (ex: módulos externos).",
            "impact": "Falha Crítica: Supressão do Processo Cognitivo"
        }
    ]

    card_y = 205
    card_h = 780

    for c in cards:
        x, w = c["x"], c["w"]
        draw.rounded_rectangle([x, card_y, x + w, card_y + card_h], radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
        
        draw.rounded_rectangle([x + 24, card_y + 24, x + len(c["badge"])*11 + 30, card_y + 60], radius=8, fill=BG_COLOR, outline=c["badge_color"], width=2)
        draw.text((x + 36, card_y + 32), c["badge"], fill=c["badge_color"], font=font_badge)

        draw.text((x + 24, card_y + 80), c["title"], fill=TEXT_WHITE, font=font_card_h)
        draw.text((x + 24, card_y + 120), c["desc"], fill=TEXT_SILVER, font=font_card_b)

        draw.rounded_rectangle([x + 24, card_y + 190, x + w - 24, card_y + 640], radius=12, fill=BG_COLOR, outline=BORDER_COLOR, width=1)
        draw.text((x + 40, card_y + 210), c["case"], fill=TEXT_WHITE, font=font_card_b)

        draw.rounded_rectangle([x + 24, card_y + card_h - 90, x + w - 24, card_y + card_h - 25], radius=10, fill=BG_COLOR, outline=c["badge_color"], width=2)
        draw.text((x + 35, card_y + card_h - 65), c["impact"], fill=c["badge_color"], font=font_card_h)

    draw_footer(draw, s)
    return img

def build_slide_4(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    # Diagrama de 3 Espaços Ortogonais
    layers = [
        {
            "y": 210, "h": 160,
            "badge": "ESPAÇO VETORIAL 1 (ENUNCIADOS FORMAIS)",
            "color": TEXT_CYAN,
            "math": "V_1 = Embed(Enunciado_Formal)  [Extrai o domínio matemático e restrições formais, descartando a narrativa]",
            "desc": "Modela o objetivo formal do problema sem contaminação léxica de historinhas metafóricas."
        },
        {
            "y": 395, "h": 160,
            "badge": "ESPAÇO VETORIAL 2 (INVARIANTES E PROPRIEDADES MATEMÁTICAS)",
            "color": TEXT_YELLOW,
            "math": "V_2 = Embed(Invariantes)  [Propriedades: Monotonicidade, Subestrutura Ótima, Matroides, Dualidade]",
            "desc": "Indexa a essência matemática que determina a prova de corretude da abordagem ótima."
        },
        {
            "y": 580, "h": 160,
            "badge": "ESPAÇO VETORIAL 3 (RESUMOS ESTRUTURAIS E LIMITES ASSINTÓTICOS)",
            "color": TEXT_EMERALD,
            "math": "V_3 = Embed(Complexidade)  [Restrições: N <= 10^5, Tempo: 2.0s, Memória: 256MB -> Complexidade Alvo: O(N log N)]",
            "desc": "Garante que o análogo recuperado respeite rigorosamente o mesmo espaço de estados e limiar de tempo."
        }
    ]

    for lay in layers:
        y, h = lay["y"], lay["h"]
        draw.rounded_rectangle([60, y, 1860, y + h], radius=14, fill=CARD_BG, outline=lay["color"], width=2)
        draw.text((90, y + 20), lay["badge"], fill=lay["color"], font=font_card_h)
        draw.text((90, y + 65), lay["math"], fill=TEXT_WHITE, font=font_code)
        draw.text((90, y + 105), lay["desc"], fill=TEXT_SILVER, font=font_card_b)

    # Caixa Inferior de Fusão Ponderada e Reranking
    box_y = 765
    box_h = 220
    draw.rounded_rectangle([60, box_y, 1860, box_y + box_h], radius=14, fill=CARD_BG, outline=BORDER_YELLOW, width=2)
    draw.text((90, box_y + 20), "FUSÃO MULTIVARIADA DE SCORES & RERANKING SEMÂNTICO VIA LLM", fill=TEXT_YELLOW, font=font_card_h)
    
    formula = "Score_Final(P, Q) = 0.25 * TFIDF_enunciado + 0.45 * TFIDF_essencia_matematica + 0.30 * TFIDF_estrategia"
    draw.text((90, box_y + 65), formula, fill=TEXT_CYAN, font=font_code)
    
    rerank_text = (
        "• Os Top-K candidatos da fusão vetorial são submetidos a um passo determinístico de Reranking Semântico por LLM.\n"
        "• O reranker audita se o invariante matemático de Q (código/erro do discente) converge com o problema recuperado P antes de compor o prompt."
    )
    draw.text((90, box_y + 115), rerank_text, fill=TEXT_WHITE, font=font_card_b)

    draw_footer(draw, s)
    return img

def build_slide_5(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    # 2 Colunas: Lado Esquerdo AI Memory / Lado Direito Engenharia de Prompt e Guardrails
    col_w = 875
    col_h = 780
    col_y = 205

    # Coluna 1: AI Memory
    draw.rounded_rectangle([60, col_y, 60 + col_w, col_y + col_h], radius=16, fill=CARD_BG, outline=BORDER_CYAN, width=2)
    draw.text((90, col_y + 25), "AI MEMORY: MODELAGEM COGNITIVA LONGITUDINAL", fill=TEXT_CYAN, font=font_card_h)
    draw.text((90, col_y + 65), "Pipeline contínuo que extingue o esquecimento entre sessões de estudo", fill=TEXT_SILVER, font=font_card_b)

    stages = [
        ("1. CAPTURAR", "Intercepta vereditos de compilação (AC, WA, TLE, RE) e código submetido.", TEXT_CYAN),
        ("2. CONSOLIDAR", "Agrupa recorrências de erros em tópicos canônicos (ex: loops aninhados em Grafos).", TEXT_YELLOW),
        ("3. RECUPERAR", "Recall longitudinal do perfil do estudante antes da geração da resposta do tutor.", TEXT_EMERALD),
        ("4. HANDOFF", "Transição segura de contexto entre múltiplos chats e agentes sem perda de estado.", TEXT_WHITE)
    ]
    sy = col_y + 120
    for st, sd, sc in stages:
        draw.rounded_rectangle([90, sy, 60 + col_w - 30, sy + 105], radius=10, fill=BG_COLOR, outline=BORDER_COLOR, width=1)
        draw.text((115, sy + 18), st, fill=sc, font=font_card_h)
        draw.text((115, sy + 55), sd, fill=TEXT_SILVER, font=font_card_b)
        sy += 125

    draw.rounded_rectangle([90, col_y + col_h - 130, 60 + col_w - 30, col_y + col_h - 30], radius=10, fill=BG_COLOR, outline=BORDER_CYAN, width=2)
    draw.text((115, col_y + col_h - 110), "PERSISTÊNCIA RIGOROSA COM SQLite E MARKDOWN", fill=TEXT_CYAN, font=font_card_h)
    draw.text((115, col_y + col_h - 75), "Transações ACID em progress.sqlite3 + arquivos memoria.md versionados.", fill=TEXT_WHITE, font=font_card_b)

    # Coluna 2: Prompt Engineering & Guardrails
    draw.rounded_rectangle([985, col_y, 985 + col_w, col_y + col_h], radius=16, fill=CARD_BG, outline=BORDER_YELLOW, width=2)
    draw.text((1015, col_y + 25), "ENGENHARIA DE PROMPT FORMAL E GUARDRAILS", fill=TEXT_YELLOW, font=font_card_h)
    draw.text((1015, col_y + 65), "Estruturação por delimitadores XML e contenção de injeção de prompt", fill=TEXT_SILVER, font=font_card_b)

    prompt_pts = [
        ("DELIMITADORES XML ESTRITOS", "<role>, <context>, <constraints>, <pedagogical_guidelines>\nIsolamento estrito entre instruções do sistema e código submetido pelo discente.", TEXT_YELLOW),
        ("DEFESA ANTI-JAILBREAK (ZERO-LEAKAGE)", "Regra formal: Proibição de emissão de blocos de sintaxe C++ que resolvam\no exercício. Recusa ativa a ataques de 'ignore all previous instructions'.", TEXT_ROSE),
        ("CALIBRAGEM DO MÉTODO SOCRÁTICO", "Escada de Pistas Graduais: Nível 1 (Conceitual) -> Nível 2 (Estrutural)\n-> Nível 3 (Assintótico). O tutor faz perguntas e não entrega o código pronto.", TEXT_EMERALD),
        ("VALIDAÇÃO EMPÍRICA MULTI-PERSONA", "Auditoria adversarial com persona Diana (Pentester): 100% das tentativas de\ninjeção de prompt contidas sem quebra de postura socrática.", TEXT_CYAN)
    ]
    py = col_y + 120
    for pt, pd, pc in prompt_pts:
        draw.rounded_rectangle([1015, py, 985 + col_w - 30, py + 115], radius=10, fill=BG_COLOR, outline=BORDER_COLOR, width=1)
        draw.text((1040, py + 15), pt, fill=pc, font=font_card_h)
        draw.text((1040, py + 52), pd, fill=TEXT_WHITE, font=font_card_b)
        py += 135

    draw.rounded_rectangle([1015, col_y + col_h - 130, 985 + col_w - 30, col_y + col_h - 30], radius=10, fill=BG_COLOR, outline=BORDER_YELLOW, width=2)
    draw.text((1040, col_y + col_h - 110), "ZONA DE DESENVOLVIMENTO PROXIMAL (ZPD)", fill=TEXT_YELLOW, font=font_card_h)
    draw.text((1040, col_y + col_h - 75), "O prompt injeta o nível cognitivo do aluno para dosar a complexidade da pista.", fill=TEXT_WHITE, font=font_card_b)

    draw_footer(draw, s)
    return img

def build_slide_6(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    # 2 Screenshots Reais do Sistema: Workspace à esquerda / Whiteboard à direita
    shot1_path = os.path.join(ASSETS_DIR, 'arena_problem.png')
    shot2_path = os.path.join(ASSETS_DIR, 'whiteboard_full.png')

    target_w = 875
    target_h = 620
    sy = 210

    if os.path.exists(shot1_path):
        im1 = Image.open(shot1_path).resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.paste(im1, (60, sy))
        draw.rectangle([58, sy - 2, 60 + target_w + 2, sy + target_h + 2], outline=BORDER_CYAN, width=3)

    if os.path.exists(shot2_path):
        im2 = Image.open(shot2_path).resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.paste(im2, (985, sy))
        draw.rectangle([983, sy - 2, 985 + target_w + 2, sy + target_h + 2], outline=BORDER_YELLOW, width=3)

    # Legendas Técnicas Explicativas abaixo de cada foto
    desc_y = sy + target_h + 20
    desc_h = 135

    # Legenda 1
    draw.rounded_rectangle([60, desc_y, 60 + target_w, desc_y + desc_h], radius=10, fill=CARD_BG, outline=BORDER_CYAN, width=2)
    draw.text((80, desc_y + 15), "1. WORKSPACE & JUIZ ISOLADO (/workspace)", fill=TEXT_CYAN, font=font_card_h)
    text_l1 = (
        "• Editor Monaco C++17 integrado com limites POSIX rígidos (RLIMIT_AS 256MB, timeout 2.0s).\n"
        "• Captura determinística de TLE para laço O(N^2) e mediação socrática contextual no dock direito."
    )
    draw.text((80, desc_y + 50), text_l1, fill=TEXT_WHITE, font=font_card_b)

    # Legenda 2
    draw.rounded_rectangle([985, desc_y, 985 + target_w, desc_y + desc_h], radius=10, fill=CARD_BG, outline=BORDER_YELLOW, width=2)
    draw.text((1005, desc_y + 15), "2. QUADRO BRANCO EXECUTÁVEL (/whiteboard)", fill=TEXT_YELLOW, font=font_card_h)
    text_l2 = (
        "• Canvas Cytoscape com vértices coloridos por estado de busca (Descoberto, Em Processo, Concluído).\n"
        "• Acoplamento do runtime C++ com renderização em tempo real da Call Stack e variáveis locais."
    )
    draw.text((1005, desc_y + 50), text_l2, fill=TEXT_WHITE, font=font_card_b)

    draw_footer(draw, s)
    return img

def build_slide_7(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    shot1_path = os.path.join(ASSETS_DIR, 'onboarding.png')
    shot2_path = os.path.join(ASSETS_DIR, 'calendar.png')

    target_w = 875
    target_h = 620
    sy = 210

    if os.path.exists(shot1_path):
        im1 = Image.open(shot1_path).resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.paste(im1, (60, sy))
        draw.rectangle([58, sy - 2, 60 + target_w + 2, sy + target_h + 2], outline=BORDER_CYAN, width=3)

    if os.path.exists(shot2_path):
        im2 = Image.open(shot2_path).resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.paste(im2, (985, sy))
        draw.rectangle([983, sy - 2, 985 + target_w + 2, sy + target_h + 2], outline=TEXT_EMERALD, width=3)

    desc_y = sy + target_h + 20
    desc_h = 135

    # Legenda 1
    draw.rounded_rectangle([60, desc_y, 60 + target_w, desc_y + desc_h], radius=10, fill=CARD_BG, outline=BORDER_CYAN, width=2)
    draw.text((80, desc_y + 15), "1. MICRO-QUIZ DIAGNÓSTICO (/onboarding)", fill=TEXT_CYAN, font=font_card_h)
    text_l1 = (
        "• Avaliação objetiva com trechos de código C++: DP, Grafos, Busca Binária e Prefix Sum.\n"
        "• Mapeamento formal de pontos fortes vs lacunas conceituais persistidas no perfil SQLite."
    )
    draw.text((80, desc_y + 50), text_l1, fill=TEXT_WHITE, font=font_card_b)

    # Legenda 2
    draw.rounded_rectangle([985, desc_y, 985 + target_w, desc_y + desc_h], radius=10, fill=CARD_BG, outline=TEXT_EMERALD, width=2)
    draw.text((1005, desc_y + 15), "2. CALENDÁRIO ADAPTATIVO ESPAÇADO (/calendar)", fill=TEXT_EMERALD, font=font_card_h)
    text_l2 = (
        "• Escalonamento diário automático baseado na curva de retenção de memória de Ebbinghaus.\n"
        "• Alternância equilibrada entre estudo teórico no Study Reader e desafios práticos na Arena."
    )
    draw.text((1005, desc_y + 50), text_l2, fill=TEXT_WHITE, font=font_card_b)

    draw_footer(draw, s)
    return img

def build_slide_8(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

    # 3 Cards: Validação Experimental, Limitações Reconhecidas, Conclusões Formais
    cards = [
        {
            "x": 60, "w": 560,
            "badge": "HOMOLOGAÇÃO EXPERIMENTAL",
            "badge_color": TEXT_EMERALD,
            "title": "Evidências de Engenharia",
            "bullets": [
                "• Suíte Completa Pytest: 365 testes unitários e de integração com 100% de aprovação.",
                "• Simulação em Hiper-Escala: 1.000.000 de estudantes sintéticos auditados em lote assíncrono.",
                "• Cobertura Combinatória: 3.000.000 de jornadas auditadas com zero quebra de invariantes.",
                "• Suporte Multi-Provedor: Gemini, OpenAI e execução 100% offline via Ollama local."
            ],
            "footer": "Certificação: 100% Aprovado em Produção",
            "footer_color": TEXT_EMERALD
        },
        {
            "x": 680, "w": 560,
            "badge": "LIMITAÇÕES RECONHECIDAS",
            "badge_color": TEXT_YELLOW,
            "title": "Limitações & Ameaças à Validade",
            "bullets": [
                "• Latência de Inferência: Reranking semântico via LLM adiciona overhead de 800ms a 1.2s.",
                "• Dependência de Calibração: Oráculos sintetizados exigem suite de estresse suficientemente densa.",
                "• Validação Ecológica: Necessidade de ensaios clínicos controlados com turmas reais de algoritmos.",
                "• Trabalho Futuro: Destilação do reranker para modelo local ultraleve (SLM)."
            ],
            "footer": "Rigor: Limitações Documentadas",
            "footer_color": TEXT_YELLOW
        },
        {
            "x": 1300, "w": 560,
            "badge": "CONCLUSÕES FORMAIS",
            "badge_color": TEXT_CYAN,
            "title": "Síntese das Contribuições",
            "bullets": [
                "• Formalização da Tríade: Validação (AutoCode) + RAG de Invariantes (OI-Assistant) + Tutoria (CODIGEN).",
                "• Eliminação de Alucinações: Zero vazamento de código e contenção de injeções de prompt.",
                "• Impacto Pedagógico: Preservação do esforço intelectual e autonomia do estudante.",
                "• Código Aberto e Reprodutibilidade: Repositório com suíte de testes e memória longitudinal."
            ],
            "footer": "💬 Aberto à Arguição da Banca",
            "footer_color": TEXT_CYAN
        }
    ]

    card_y = 205
    card_h = 780

    for c in cards:
        x, w = c["x"], c["w"]
        draw.rounded_rectangle([x, card_y, x + w, card_y + card_h], radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
        
        draw.rounded_rectangle([x + 24, card_y + 24, x + len(c["badge"])*11 + 30, card_y + 60], radius=8, fill=BG_COLOR, outline=c["badge_color"], width=2)
        draw.text((x + 36, card_y + 32), c["badge"], fill=c["badge_color"], font=font_badge)

        draw.text((x + 24, card_y + 80), c["title"], fill=TEXT_WHITE, font=font_card_h)
        draw.line([x + 24, card_y + 120, x + w - 24, card_y + 120], fill=BORDER_COLOR, width=1)

        y_text = card_y + 145
        for b in c["bullets"]:
            draw.text((x + 24, y_text), b, fill=TEXT_WHITE, font=font_card_b)
            y_text += 120

        draw.rounded_rectangle([x + 24, card_y + card_h - 75, x + w - 24, card_y + card_h - 25], radius=10, fill=BG_COLOR, outline=c["footer_color"], width=2)
        draw.text((x + 40, card_y + card_h - 60), c["footer"], fill=c["footer_color"], font=font_card_h)

    draw_footer(draw, s)
    return img

# Geração de todos os slides
builders = {
    1: build_slide_1,
    2: build_slide_2,
    3: build_slide_3,
    4: build_slide_4,
    5: build_slide_5,
    6: build_slide_6,
    7: build_slide_7,
    8: build_slide_8
}

rendered_images = []
for s in academic_slides:
    num = s["num"]
    fn = builders[num]
    im = fn(s)
    out_png = os.path.join(OUT_DIR, f"academic_slide_{num:02d}.png")
    im.save(out_png, quality=95)
    rendered_images.append(im)
    print(f"Slide acadêmico {num} gerado em: {out_png}")

# Salva PDF Oficial de Alto Contraste
pdf_out1 = "slides_apresentacao/Apresentacao_AutoTutor_CP_Academica.pdf"
pdf_out2 = "Apresentacao_AutoTutor_CP_Academica.pdf"

if rendered_images:
    first = rendered_images[0]
    rest = rendered_images[1:]
    first.save(pdf_out1, save_all=True, append_images=rest, resolution=150)
    first.save(pdf_out2, save_all=True, append_images=rest, resolution=150)
    print(f"PDF Acadêmico de Alto Contraste gerado com sucesso em:\n  1. {pdf_out1}\n  2. {pdf_out2}")

# Gerar PowerPoint PPTX Oficial de Alto Contraste com Notas do Orador
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

for idx, s in enumerate(academic_slides):
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(10, 15, 29) # 0A0F1D

    # Insere imagem renderizada com margens de precisão
    png_path = os.path.join(OUT_DIR, f"academic_slide_{s['num']:02d}.png")
    if os.path.exists(png_path):
        slide.shapes.add_picture(png_path, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))

    # Notas do Orador
    notes_slide = slide.notes_slide
    tf_notes = notes_slide.notes_text_frame
    tf_notes.text = f"=== SLIDE {s['num']} / 8 ({s['time']}) ===\n\n{s['script']}"

pptx_out1 = "slides_apresentacao/Apresentacao_AutoTutor_CP_Academica.pptx"
pptx_out2 = "Apresentacao_AutoTutor_CP_Academica.pptx"
prs.save(pptx_out1)
prs.save(pptx_out2)
print(f"PPTX Acadêmico gerado com sucesso em:\n  1. {pptx_out1}\n  2. {pptx_out2}")

