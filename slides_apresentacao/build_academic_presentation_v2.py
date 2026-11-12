import os
from PIL import Image, ImageDraw, ImageFont
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

ASSETS_DIR = 'slides_apresentacao/assets'
OUT_DIR = 'slides_apresentacao/academic_png'
os.makedirs(OUT_DIR, exist_ok=True)

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

def draw_header(draw, s, W=1920):
    draw.rounded_rectangle([60, 30, 60 + len(s["badge"])*12 + 40, 72], radius=8, fill=CARD_BG, outline=BORDER_CYAN, width=2)
    draw.text((80, 40), s["badge"], fill=TEXT_CYAN, font=font_badge)

    time_w = len(s["time"]) * 11 + 35
    draw.rounded_rectangle([W - 60 - time_w, 30, W - 60, 72], radius=8, fill=CARD_BG, outline=BORDER_YELLOW, width=2)
    draw.text((W - 45 - time_w, 40), f"⏱ {s['time']}", fill=TEXT_YELLOW, font=font_badge)

    draw.text((60, 95), s["title"], fill=TEXT_WHITE, font=font_title)
    draw.text((60, 150), s["subtitle"], fill=TEXT_SILVER, font=font_sub)

def draw_footer(draw, s, W=1920, H=1080):
    draw.line([60, H - 70, W - 60, H - 70], fill=BORDER_COLOR, width=1)
    draw.text((60, H - 52), "AutoTutor CP — Arquitetura de Tutoria Inteligente e Verificação Formal em Algoritmos (FIA 2026)", fill=TEXT_SILVER, font=font_footer)
    draw.text((W - 130, H - 52), f"Slide {s['num']} / 9", fill=TEXT_YELLOW, font=font_footer)

# Importa as funções já existentes
from build_academic_presentation import build_slide_1, build_slide_2, build_slide_3, build_slide_6, build_slide_7, build_slide_8

def build_slide_4_formula(s):
    img = Image.new('RGB', (1920, 1080), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, s)

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

    box_y = 765
    box_h = 220
    draw.rounded_rectangle([60, box_y, 1860, box_y + box_h], radius=14, fill=CARD_BG, outline=BORDER_YELLOW, width=2)
    draw.text((90, box_y + 20), "FUSÃO MULTIVARIADA DE SCORES & RERANKING SEMÂNTICO VIA LLM", fill=TEXT_YELLOW, font=font_card_h)
    
    formula = "Score(q, d) = 0.25 · TFIDF_enunciado + 0.45 · TFIDF_essência_matemática + 0.30 · TFIDF_estratégia"
    draw.text((90, box_y + 65), formula, fill=TEXT_CYAN, font=get_font(20, bold=True))
    
    rerank_text = (
        "• Peso 0.45 na Essência Matemática: ali reside a invariante (ex: relações de recorrência dp[i] = max(...)).\n"
        "• Os Top-K candidatos são validados por um passo determinístico de Reranking Semântico por LLM antes do prompt."
    )
    draw.text((90, box_y + 115), rerank_text, fill=TEXT_WHITE, font=font_card_b)

    draw_footer(draw, s)
    return img

def build_slide_5_timeline(s):
    # Retorna diretamente a imagem gerada pelo script generate_danca_sincrona.py
    path = os.path.join(ASSETS_DIR, 'diagrama_danca_sincrona_tle.png')
    im = Image.open(path)
    draw = ImageDraw.Draw(im)
    # Atualiza o rodapé com numeração correta
    draw.line([60, 1080 - 70, 1920 - 60, 1080 - 70], fill=BORDER_COLOR, width=1)
    draw.text((60, 1080 - 52), "AutoTutor CP — Arquitetura de Tutoria Inteligente e Verificação Formal em Algoritmos (FIA 2026)", fill=TEXT_SILVER, font=font_footer)
    draw.text((1920 - 130, 1080 - 52), f"Slide {s['num']} / 9", fill=TEXT_YELLOW, font=font_footer)
    return im

from build_academic_presentation import build_slide_5 as build_slide_6_memory

slides_9 = [
    {
        "num": 1,
        "time": "00:00 - 00:35 (35s)",
        "badge": "FORMULAÇÃO DO PROBLEMA CIENTÍFICO",
        "title": "AutoTutor CP: Tutoria Inteligente e Verificação Formal em Algoritmos",
        "subtitle": "O abismo cognitivo entre a prova teórica e a correção assintótica no julgamento automático",
        "script": """\"Boa tarde aos membros da banca examinadora. Na disciplina de Fundamentos da Inteligência Artificial, investigamos o problema da formação analítica em Ciência da Computação.

Existe uma lacuna estrutural no aprendizado de algoritmos avançados: juízes online operam com vereditos booleanos opacos como Wrong Answer, sem explicitar a quebra do invariante lógico. Em contrapartida, LLMs genéricas entregam o código pronto, suprimindo o esforço cognitivo do discente e induzindo à atrofia do raciocínio analítico.

O AutoTutor CP investiga e formaliza a integração entre execução determinística em sandbox C++, recuperação semântica por invariantes e mediação dialógica socrática.\""""
    },
    {
        "num": 2,
        "time": "00:35 - 01:05 (30s)",
        "badge": "FUNDAMENTAÇÃO TEÓRICA",
        "title": "A Tríade de Pesquisa: Fundamentação na Literatura Internacional",
        "subtitle": "Três publicações formais recentes em conferências de ponta (ICLR, IOI, IEEE VL/HCC)",
        "script": """\"Nossa arquitetura fundamenta-se estritamente na literatura científica recente:

Do AutoCode (ICLR 2026), adotamos a validação por oráculo duplo: enunciados e testes de estresse são compilados antes do consumo do discente.
Do OI-Assistant (IOI 2025), extraímos a recuperação semântica por invariantes matemáticos.
E do CODIGEN (IEEE 2025), formalizamos a escada gradual de pistas socráticas sem alucinação.\""""
    },
    {
        "num": 3,
        "time": "01:05 - 01:40 (35s)",
        "badge": "ANÁLISE CRÍTICA DE IA",
        "title": "Limitações Estruturais: Por Que o RAG Convencional Falha em Algoritmos?",
        "subtitle": "A falácia da similaridade léxica, insensibilidade assintótica e vazamento precoce de soluções",
        "script": """\"Demonstramos analiticamente por que o RAG clássico falha em domínios algorítmicos:

Primeiro: a falácia léxica. Dois problemas que compartilham a mesma narrativa metafórica — como vacas e fazendas — são aproximados no espaço denso genérico pelas palavras. Porém, um exige Dijkstra O(E log V) e o outro Fluxo Máximo O(V^2 E). O RAG tradicional recupera o algoritmo incorreto.

Segundo: a insensibilidade assintótica. Limites de N <= 20 demandam busca exponencial, enquanto N <= 10^5 exige programação dinâmica. O RAG comum é cego a ordens de grandeza.\""""
    },
    {
        "num": 4,
        "time": "01:40 - 02:15 (35s)",
        "badge": "METODOLOGIA PROPOSTA",
        "title": "Metodologia: RAG Multiespaço e Fórmula de Scores TF-IDF",
        "subtitle": "Decomposição em 3 espaços vetoriais ortogonais e validação matemática de corretude",
        "script": """\"Para mitigar essas limitações, implementamos a arquitetura do OI-Assistant com três espaços vetoriais ortogonais:

Espaço 1: Enunciados Formais.
Espaço 2: Invariantes e Propriedades Matemáticas.
Espaço 3: Resumos Estruturais e Limites Assintóticos.

A métrica de similaridade linear ponderada é definida formalmente por:
Score(q, d) = 0.25 · TFIDF_enunciado + 0.45 · TFIDF_essência_matemática + 0.30 · TFIDF_estratégia.

O peso de 0.45 na essência matemática prioriza a relação de recorrência sobre o texto da historinha, seguido de reranking semântico via LLM.\""""
    },
    {
        "num": 5,
        "time": "02:15 - 03:00 (45s)",
        "badge": "ESTUDO DE CASO REAL",
        "title": "A Dança Síncrona na Prática: Caso Real de TLE no Workspace",
        "subtitle": "Ciclo integrado de 7 etapas: da submissão do discente à intervenção socrática contextual",
        "script": """\"Vejam a integração síncrona operando em 7 etapas diante de um caso real de TLE:

1. O discente submete um código ineficiente em C++ no Workspace.
2. O Isolated Judge em Bubblewrap POSIX retorna Time Limit Exceeded (2.0s).
3. A LearnerMemory intercepta e grava o evento em SQLite FTS5, atualizando o arquivo topicos/bfs.md.
4. O motor OI-Assistant extrai a essência do problema e calcula o TF-IDF nos 3 espaços, recuperando o invariante da BFS.
5. O KnowledgeBase busca na literatura de base o lema sobre exploração por camadas em O(V + E).
6. O CodigenTutor aplica o guardrail Zero-Leakage e formula a pista socrática.
7. Na tela do aluno, a IA intervém cirurgicamente: 'Percebi que seu laço while executa muito mais iterações do que a quantidade de salas (V). O que acontece se uma mesma sala for inserida na fila mais de uma vez antes de ser processada? Em que momento exato você deve marcar que ela já foi descoberta?'\""""
    },
    {
        "num": 6,
        "time": "03:00 - 03:35 (35s)",
        "badge": "MODELAGEM LONGITUDINAL",
        "title": "AI Memory Longitudinal e Engenharia de Prompt Formal",
        "subtitle": "Persistência de perfil cognitivo em SQLite e contenção estrita de prompt injection",
        "script": """\"O pipeline de AI Memory opera um ciclo contínuo de Captura, Consolidação, Recuperação e Handoff com transações ACID em SQLite.

Na Engenharia de Prompt, empregamos delimitação XML estrita (<role>, <context>, <constraints>) e guardrails matemáticos de Zero-Leakage.

Mesmo sob ataques deliberados de injeção de prompt simulados com a persona Diana, o tutor conteve 100% das tentativas, preservando a mediação dialógica dosada pela Zona de Desenvolvimento Proximal.\""""
    },
    {
        "num": 7,
        "time": "03:35 - 04:10 (35s)",
        "badge": "EVIDÊNCIAS EXPERIMENTAIS (SISTEMA REAL)",
        "title": "Evidências Empíricas: O Workspace de Execução e o Quadro Branco",
        "subtitle": "Sandbox C++17 com limites POSIX, detecção determinística de TLE/WA e visualização de grafos",
        "script": """\"Apresentamos aqui as evidências empíricas da plataforma em operação real:

À esquerda, o Workspace com editor Monaco C++17 sob limites POSIX de 256MB e captura determinística de Time Limit Exceeded, com o AI Tutor atuando no dock lateral.

À direita, o Quadro Branco Algorítmico, onde o grafo topológico acopla-se ao runtime C++, renderizando a Call Stack de recursão ao vivo para observação do backtracking.\""""
    },
    {
        "num": 8,
        "time": "04:10 - 04:40 (30s)",
        "badge": "DIAGNÓSTICO E ADAPTAÇÃO",
        "title": "Diagnóstico Cognitivo e Escalonamento Espaçado (Ebbinghaus)",
        "subtitle": "Micro-quiz objetivo de código e agendamento adaptativo de repetição espaçada",
        "script": """\"Para fundamentar a adaptação pedagógica:

À esquerda, o Onboarding com micro-quiz calibrado de código C++ mapeando lacunas conceituais em Programação Dinâmica e Grafos.

À direita, o Calendário Adaptativo projetando a rotina diária baseada na curva de esquecimento de Ebbinghaus, intercalando leitura teórica e prática na Arena.\""""
    },
    {
        "num": 9,
        "time": "04:40 - 05:00 (20s)",
        "badge": "VALIDAÇÃO FORMAL E CONCLUSÕES",
        "title": "Validação Empírica, Limitações e Arguição da Banca",
        "subtitle": "365 testes Pytest (100% pass), simulação com 1.000.000 de discentes sintéticos e trabalho futuro",
        "script": """\"Homologamos a arquitetura com 365 testes no Pytest com 100% de aprovação e simulamos 1 milhão de discentes sintéticos cobrindo 3 milhões de jornadas completas sem quebra de invariantes.

Como limitação, documentamos o custo computacional do reranking, apontando como trabalho futuro a destilação de modelos especializados.

Agradecemos à banca examinadora e estamos abertos para a discussão técnica e metodológica.\""""
    }
]

builders_9 = {
    1: build_slide_1,
    2: build_slide_2,
    3: build_slide_3,
    4: build_slide_4_formula,
    5: build_slide_5_timeline,
    6: build_slide_6_memory,
    7: build_slide_6,
    8: build_slide_7,
    9: build_slide_8
}

rendered_9 = []
for s in slides_9:
    num = s["num"]
    fn = builders_9[num]
    im = fn(s)
    out_png = os.path.join(OUT_DIR, f"academic_slide_{num:02d}.png")
    im.save(out_png, quality=95)
    rendered_9.append(im)
    print(f"Slide acadêmico {num} gerado em: {out_png}")

# Salva PDF Oficial de Alto Contraste de 9 Slides
pdf_out1 = "slides_apresentacao/Apresentacao_AutoTutor_CP_Academica.pdf"
pdf_out2 = "Apresentacao_AutoTutor_CP_Academica.pdf"

if rendered_9:
    first = rendered_9[0]
    rest = rendered_9[1:]
    first.save(pdf_out1, save_all=True, append_images=rest, resolution=150)
    first.save(pdf_out2, save_all=True, append_images=rest, resolution=150)
    print(f"PDF Acadêmico de 9 Slides gerado em:\n  1. {pdf_out1}\n  2. {pdf_out2}")

# Gerar PowerPoint PPTX Oficial de 9 Slides
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

for idx, s in enumerate(slides_9):
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(10, 15, 29)

    png_path = os.path.join(OUT_DIR, f"academic_slide_{s['num']:02d}.png")
    if os.path.exists(png_path):
        slide.shapes.add_picture(png_path, Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))

    notes_slide = slide.notes_slide
    tf_notes = notes_slide.notes_text_frame
    tf_notes.text = f"=== SLIDE {s['num']} / 9 ({s['time']}) ===\n\n{s['script']}"

pptx_out1 = "slides_apresentacao/Apresentacao_AutoTutor_CP_Academica.pptx"
pptx_out2 = "Apresentacao_AutoTutor_CP_Academica.pptx"
prs.save(pptx_out1)
prs.save(pptx_out2)
print(f"PPTX Acadêmico de 9 Slides gerado em:\n  1. {pptx_out1}\n  2. {pptx_out2}")

