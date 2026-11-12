import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = 'slides_apresentacao/assets'
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1920, 1080
img = Image.new('RGB', (W, H), (10, 15, 29)) # Deep Navy
draw = ImageDraw.Draw(img)

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

font_title = get_font(34, bold=True)
font_sub = get_font(18, bold=False)
font_badge = get_font(15, bold=True)
font_box_h = get_font(18, bold=True)
font_box_b = get_font(14, bold=False)
font_callout = get_font(16, bold=True)
font_quote = get_font(16, bold=False)

# Top Bar Badge
draw.rounded_rectangle([60, 30, 680, 72], radius=8, fill=(21, 31, 50), outline=(56, 189, 248), width=2)
draw.text((80, 40), "ESTUDO DE CASO REAL · CICLO DE 7 ETAPAS", fill=(56, 189, 248), font=font_badge)

# Title & Subtitle
draw.text((60, 95), "A Dança Síncrona na Prática: Caso Real de TLE no Workspace", fill=(255, 255, 255), font=font_title)
draw.text((60, 145), "Quando o estudante submete um código ineficiente em C++, a integração opera sem atrito e sem spoilers:", fill=(226, 232, 240), font=font_sub)

steps = [
    {
        "num": "1",
        "title": "Discente Submete Código C++",
        "desc": "Código C++17 submetido no Workspace para o problema 'Rotas entre Cidades'.",
        "detail": "Laço while com inserções redundantes na fila sem marcação imediata.",
        "color": (56, 189, 248) # Cyan
    },
    {
        "num": "2",
        "title": "Isolated Judge (Sandbox POSIX)",
        "desc": "Execução em sandbox Bubblewrap com RLIMIT_AS 256MB e timeout estrito de 2.0s.",
        "detail": "Veredito determinístico emitido: 'Time Limit Exceeded (TLE - 2.0s)'.",
        "color": (251, 113, 133) # Rose
    },
    {
        "num": "3",
        "title": "LearnerMemory (AI-Memory SQLite)",
        "desc": "Intercepta e persiste o evento em progress.sqlite3 (tabela FTS5).",
        "detail": "Atualiza data/memory/<id>/topicos/bfs.md: '3º TLE consecutivo em Grafos/BFS'.",
        "color": (250, 204, 21) # Yellow
    },
    {
        "num": "4",
        "title": "Motor OI-Assistant (rag_retriever.py)",
        "desc": "Extrator Estrutural analisa a topologia do problema (Grafo Não Ponderado).",
        "detail": "Score = 0.25·TFIDF_enun + 0.45·TFIDF_essência + 0.30·TFIDF_estrat. Invariante da BFS recuperada.",
        "color": (52, 211, 153) # Emerald
    },
    {
        "num": "5",
        "title": "KnowledgeBase (RAG Teórico)",
        "desc": "Consulta formal na literatura canônica (Szwarcfiter / Cormen).",
        "detail": "Recupera o lema sobre 'Exploração em largura por camadas e complexidade O(V + E)'.",
        "color": (56, 189, 248) # Cyan
    },
    {
        "num": "6",
        "title": "CodigenTutor (Prompt Socrático XML)",
        "desc": "Fusão: Contexto do Aluno (Memória) + Teoria Formal + Invariante Estrutural.",
        "detail": "Aplica Guardrail Zero-Leakage (Tier 2): Proibição terminante de fornecer código pronto.",
        "color": (250, 204, 21) # Yellow
    }
]

# Renderização dos 6 primeiros passos em 2 linhas de 3 cards
card_w = 560
card_h = 165
xs = [60, 680, 1300]
ys = [195, 395]

for idx, st in enumerate(steps):
    r = idx // 3
    c = idx % 3
    x = xs[c]
    y = ys[r]
    
    draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=14, fill=(21, 31, 50), outline=st["color"], width=2)
    
    # Badge número
    draw.rounded_rectangle([x + 18, y + 16, x + 58, y + 52], radius=8, fill=(10, 15, 29), outline=st["color"], width=1)
    draw.text((x + 30, y + 22), st["num"], fill=st["color"], font=font_box_h)
    
    draw.text((x + 72, y + 22), st["title"], fill=(255, 255, 255), font=font_box_h)
    draw.text((x + 20, y + 68), st["desc"], fill=(226, 232, 240), font=font_box_b)
    draw.text((x + 20, y + 108), st["detail"], fill=st["color"], font=font_callout)

# Passo 7: Intervenção Socrática na Tela do Aluno (Banner Inferior de Destaque)
box_y = 610
box_h = 390
draw.rounded_rectangle([60, box_y, 1860, box_y + box_h], radius=16, fill=(21, 31, 50), outline=(52, 211, 153), width=3)

# Header Passo 7
draw.rounded_rectangle([85, box_y + 20, 750, box_y + 65], radius=8, fill=(10, 15, 29), outline=(52, 211, 153), width=2)
draw.text((100, box_y + 28), "7. INTERVENÇÃO SOCRÁTICA NA TELA DO ALUNO (ZERO-LEAKAGE)", fill=(52, 211, 153), font=font_box_h)

quote_text = (
    "“Percebi que seu laço while executa muito mais iterações do que a quantidade de salas do labirinto (V).\n\n"
    "O que acontece se uma mesma sala for inserida na fila mais de uma vez antes de ser processada?\n\n"
    "Em que momento exato você deve marcar que ela já foi descoberta?”"
)
draw.text((95, box_y + 90), quote_text, fill=(255, 255, 255), font=font_title)

# Callout explicativo do ganho pedagógico
draw.rounded_rectangle([85, box_y + 295, 1835, box_y + 365], radius=10, fill=(10, 15, 29), outline=(56, 189, 248), width=1)
callout_text = "💡 GANHO PEDAGÓGICO: A IA não entrega o código pronto. Ela orienta a atenção do estudante para a causa raiz do TLE: a violação do invariante da BFS (marcar visitado tarde demais)."
draw.text((105, box_y + 315), callout_text, fill=(56, 189, 248), font=font_callout)

# Footer
draw.line([60, 1025, 1860, 1025], fill=(71, 85, 105), width=1)
draw.text((60, 1040), "AutoTutor CP — Arquitetura de Tutoria Inteligente e Verificação Formal em Algoritmos (FIA 2026)", fill=(226, 232, 240), font=font_sub)
draw.text((1760, 1040), "Caso Real TLE", fill=(250, 204, 21), font=font_sub)

out_file = os.path.join(ASSETS_DIR, 'diagrama_danca_sincrona_tle.png')
img.save(out_file, quality=95)
print(f"Diagrama gerado com sucesso em: {out_file}")
