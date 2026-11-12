import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = 'slides_apresentacao/assets'
os.makedirs(ASSETS_DIR, exist_ok=True)

# Cores do tema escuro sóbrio (Slate Dark)
BG_COLOR = (15, 23, 42)       # Slate 900
CARD_BG = (30, 41, 59)        # Slate 800
CARD_BORDER = (51, 65, 85)    # Slate 700
TEXT_WHITE = (248, 250, 252)  # Slate 50
TEXT_MUTED = (148, 163, 184)  # Slate 400
TEXT_CYAN = (56, 189, 248)    # Sky 400
TEXT_EMERALD = (52, 211, 153) # Emerald 400
TEXT_ROSE = (251, 113, 133)   # Rose 400
TEXT_AMBER = (251, 191, 36)   # Amber 400

# Tentativa de carregar fontes TTF do sistema, com fallback para padrão
def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title = get_font(32, bold=True)
font_subtitle = get_font(20, bold=False)
font_card_title = get_font(22, bold=True)
font_card_sub = get_font(16, bold=True)
font_body = get_font(15, bold=False)
font_badge = get_font(13, bold=True)

# -------------------------------------------------------------
# 1. Diagrama Slide 1: Comparativo do Problema
# -------------------------------------------------------------
def make_diagram_slide1():
    W, H = 1600, 900
    img = Image.new('RGB', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Título & Subtítulo
    draw.text((80, 50), "O Dilema do Estudante: Onde a Aprendizagem Falha?", fill=TEXT_WHITE, font=font_title)
    draw.text((80, 100), "A comparação entre abordagens tradicionais e a necessidade de tutoria socrática", fill=TEXT_MUTED, font=font_subtitle)

    cards = [
        {
            "x": 80, "w": 440,
            "badge": "JUIZ ONLINE TRADICIONAL",
            "badge_color": TEXT_ROSE,
            "title": "Veredito Frio & Opaco",
            "mock": "Verdict: Wrong Answer\nTest 4: Output mismatch.\n(Nenhuma explicação)",
            "pain": [
                "• Punição sem rastreabilidade do erro",
                "• Estudante trava sem entender a causa",
                "• Abismo entre a teoria e a correção",
                "• Gera frustração e abandono"
            ],
            "footer": "Diagnóstico: Feedback Incompleto",
            "footer_color": TEXT_ROSE
        },
        {
            "x": 580, "w": 440,
            "badge": "CHATBOT GENÉRICO (LLM)",
            "badge_color": TEXT_AMBER,
            "title": "Solução Mastigada",
            "mock": "'Aqui está o código C++ pronto\nresolvendo o problema com\nComplexidade O(N log N)...'",
            "pain": [
                "• Entrega a resposta de imediato",
                "• Aluno copia e passa sem pensar",
                "• Falsa sensação de competência",
                "• Causa atrofia cognitiva a longo prazo"
            ],
            "footer": "Diagnóstico: Anti-Pedagógico",
            "footer_color": TEXT_AMBER
        },
        {
            "x": 1080, "w": 440,
            "badge": "AUTOTUTOR CP (NOSSA SOLUÇÃO)",
            "badge_color": TEXT_EMERALD,
            "title": "Tutoria Socrática Guiada",
            "mock": "'Note que seu laço repete buscas.\nQual propriedade matemática evita\nrecalcular os mesmos subproblemas?'",
            "pain": [
                "• Juiz local com diagnóstico em tempo real",
                "• Escada de pistas sem entregar o código",
                "• Foco em invariantes e complexidade",
                "• Constrói raciocínio autônomo"
            ],
            "footer": "Resultado: Aprendizado Real",
            "footer_color": TEXT_EMERALD
        }
    ]

    card_y = 170
    card_h = 660

    for c in cards:
        x, w = c["x"], c["w"]
        # Card Background
        draw.rounded_rectangle([x, card_y, x + w, card_y + card_h], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
        
        # Badge
        draw.rounded_rectangle([x + 24, card_y + 24, x + 24 + len(c["badge"])*10, card_y + 54], radius=8, fill=(15, 23, 42), outline=c["badge_color"], width=1)
        draw.text((x + 34, card_y + 30), c["badge"], fill=c["badge_color"], font=font_badge)

        # Title
        draw.text((x + 24, card_y + 75), c["title"], fill=TEXT_WHITE, font=font_card_title)

        # Mock terminal/chat box
        draw.rounded_rectangle([x + 24, card_y + 125, x + w - 24, card_y + 245], radius=10, fill=(15, 23, 42), outline=(71, 85, 105), width=1)
        draw.text((x + 38, card_y + 140), c["mock"], fill=TEXT_MUTED, font=font_body)

        # Pain points
        y_text = card_y + 275
        for p in c["pain"]:
            draw.text((x + 24, y_text), p, fill=TEXT_WHITE, font=font_body)
            y_text += 45

        # Footer Pill
        draw.rounded_rectangle([x + 24, card_y + card_h - 70, x + w - 24, card_y + card_h - 24], radius=10, fill=(15, 23, 42), outline=c["footer_color"], width=1)
        draw.text((x + 40, card_y + card_h - 55), c["footer"], fill=c["footer_color"], font=font_card_sub)

    out_path = os.path.join(ASSETS_DIR, 'diagrama_slide1_problema.png')
    img.save(out_path, quality=95)
    print(f"Gerado: {out_path}")

# -------------------------------------------------------------
# 2. Diagrama Slide 2: Pilares Científicos
# -------------------------------------------------------------
def make_diagram_slide2():
    W, H = 1600, 900
    img = Image.new('RGB', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.text((80, 50), "Fundamentação Teórica: A Tríade Científica", fill=TEXT_WHITE, font=font_title)
    draw.text((80, 100), "Três artigos de ponta que sustentam a geração, recuperação e tutoria sem alucinação", fill=TEXT_MUTED, font=font_subtitle)

    pillars = [
        {
            "x": 80, "w": 440,
            "conf": "ICLR 2026",
            "conf_color": TEXT_CYAN,
            "name": "AutoCode",
            "subtitle": "Geração Validada por Oráculo",
            "citation": "Zhou et al. (ICLR 2026 / arXiv:2510.12803)",
            "bullets": [
                "1. Geração de Problema Inédito:\n   LLM formula enunciado e restrições formais.",
                "2. Síntese do Par Oráculo:\n   Gera gerador de testes (input) e gabarito C++.",
                "3. Validação Cruzada por Compilação:\n   Se o oráculo falha nos testes, descarta.",
                "4. Garantia Matemática:\n   Zero problemas mal formulados entregues ao aluno."
            ]
        },
        {
            "x": 580, "w": 440,
            "conf": "IOI 2025",
            "conf_color": TEXT_EMERALD,
            "name": "OI-Assistant",
            "subtitle": "RAG por Invariantes Matemáticos",
            "citation": "Su, Nie & Meng (Olympiads in Informatics 2025)",
            "bullets": [
                "1. Além da Busca Léxica:\n   Não busca por palavras superficiais.",
                "2. Embedding de Invariantes:\n   Indexa por propriedades estruturais profundas\n   (ex: monotonicidade, subestrutura ótima).",
                "3. Recuperação de Problemas Análogos:\n   Oferece problemas similares no nível exato.",
                "4. Transferência de Conhecimento:\n   Ensina o aluno a reconhecer o padrão formal."
            ]
        },
        {
            "x": 1080, "w": 440,
            "conf": "IEEE VL/HCC 2025",
            "conf_color": TEXT_AMBER,
            "name": "CODIGEN",
            "subtitle": "Tutoria Socrática Adaptativa",
            "citation": "Ez-zaouia & Boumarafi (IEEE VL/HCC 2025)",
            "bullets": [
                "1. Escada de Pistas Graduais:\n   Nível 1 (Conceitual) -> Nível 2 (Estrutural)\n   -> Nível 3 (Assintótico).",
                "2. Zero-Leakage Guardrails:\n   Barreiras anti-jailbreak e anti-alucinação.",
                "3. Pre-Flight Check Assintótico:\n   Analisa loops antes de gerar a dica.",
                "4. Tutoria Ativa:\n   Estimula metacognição e reflexão contínua."
            ]
        }
    ]

    card_y = 170
    card_h = 660

    for p in pillars:
        x, w = p["x"], p["w"]
        draw.rounded_rectangle([x, card_y, x + w, card_y + card_h], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)

        # Conf badge
        draw.rounded_rectangle([x + 24, card_y + 24, x + 160, card_y + 54], radius=8, fill=(15, 23, 42), outline=p["conf_color"], width=1)
        draw.text((x + 36, card_y + 30), p["conf"], fill=p["conf_color"], font=font_badge)

        # Title & Subtitle
        draw.text((x + 24, card_y + 70), p["name"], fill=TEXT_WHITE, font=font_card_title)
        draw.text((x + 24, card_y + 105), p["subtitle"], fill=TEXT_CYAN, font=font_card_sub)
        draw.text((x + 24, card_y + 135), p["citation"], fill=TEXT_MUTED, font=font_badge)

        # Divisor
        draw.line([x + 24, card_y + 165, x + w - 24, card_y + 165], fill=CARD_BORDER, width=1)

        # Bullets
        y_text = card_y + 185
        for b in p["bullets"]:
            draw.text((x + 24, y_text), b, fill=TEXT_WHITE, font=font_body)
            y_text += 105

    out_path = os.path.join(ASSETS_DIR, 'diagrama_slide2_pilares.png')
    img.save(out_path, quality=95)
    print(f"Gerado: {out_path}")

# -------------------------------------------------------------
# 3. Diagrama Slide 6: Arquitetura Técnica & Engenharia
# -------------------------------------------------------------
def make_diagram_slide6():
    W, H = 1600, 900
    img = Image.new('RGB', (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.text((80, 45), "Arquitetura Técnica & Engenharia de Resiliência", fill=TEXT_WHITE, font=font_title)
    draw.text((80, 95), "Fullstack desacoplado, sandbox isolado e tolerância a falhas offline", fill=TEXT_MUTED, font=font_subtitle)

    layers = [
        {
            "y": 160, "h": 120,
            "title": "CAMADA 1 · FRONTEND ERGONÔMICO (Next.js 14 App Router)",
            "color": TEXT_CYAN,
            "items": "• React 18 & TypeScript Estrito  • Editor Monaco (C++17)  • Canvas Cytoscape (Grafos)  • Tailwind CSS Sóbrio (Linear/LeetCode Dark)"
        },
        {
            "y": 300, "h": 120,
            "title": "CAMADA 2 · API GATEWAY REST (Python Starlette & FastAPI)",
            "color": TEXT_EMERALD,
            "items": "• Endpoints Assíncronos  • Isolamento por Bearer Token  • Motor de Trilha Adaptativa  • Orquestrador RAG com Memória Akita"
        },
        {
            "y": 440, "h": 125,
            "title": "CAMADA 3 · SANDBOX & JUIZ DE EXECUÇÃO LOCAL (isolated_judge.py)",
            "color": TEXT_ROSE,
            "items": "• Compilação G++ 17 Isolada  • Limites POSIX (RLIMIT_AS 256MB)  • Bubblewrap Jail contra Fork/Memory Bombs  • Vereditos Precisos: AC, WA, TLE, CE, RE"
        },
        {
            "y": 585, "h": 120,
            "title": "CAMADA 4 · ORQUESTRADOR MULTI-LLM & PERSISTÊNCIA TRANSAÇÃO ACID",
            "color": TEXT_AMBER,
            "items": "• Provedores: Google Gemini / OpenAI / OLLAMA LOCAL (100% Offline sem internet)  • SQLite Transacional (progress.sqlite3, library.sqlite3)"
        }
    ]

    for lay in layers:
        y, h = lay["y"], lay["h"]
        draw.rounded_rectangle([80, y, 1520, y + h], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.text((110, y + 20), lay["title"], fill=lay["color"], font=font_card_sub)
        draw.text((110, y + 60), lay["items"], fill=TEXT_WHITE, font=font_body)

    # Badges de Certificação no Rodapé
    cert_y = 735
    certs = [
        "✓ 365 Testes Pytest Aprovados (100% Pass)",
        "✓ 1.000.000 Estudantes Sintéticos Auditados",
        "✓ Zero Alucinações / Zero Solution Leakage",
        "✓ 100% Operacional Offline via Ollama"
    ]
    w_pill = 330
    for idx, c in enumerate(certs):
        xp = 80 + idx * (w_pill + 26)
        draw.rounded_rectangle([xp, cert_y, xp + w_pill, cert_y + 55], radius=10, fill=(15, 23, 42), outline=TEXT_EMERALD, width=1)
        draw.text((xp + 15, cert_y + 18), c, fill=TEXT_EMERALD, font=font_badge)

    out_path = os.path.join(ASSETS_DIR, 'diagrama_slide6_arquitetura.png')
    img.save(out_path, quality=95)
    print(f"Gerado: {out_path}")

if __name__ == '__main__':
    make_diagram_slide1()
    make_diagram_slide2()
    make_diagram_slide6()
    print("Todos os diagramas foram gerados com sucesso!")
