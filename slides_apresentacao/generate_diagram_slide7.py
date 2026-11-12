import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = 'slides_apresentacao/assets'
W, H = 1600, 900
img = Image.new('RGB', (W, H), (15, 23, 42))
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    font_card_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    font_card_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_closing = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
except:
    font_title = font_sub = font_card_title = font_card_body = font_badge = font_closing = ImageFont.load_default()

draw.text((80, 50), "AutoTutor CP: Conclusão & Impacto Formativo", fill=(248, 250, 252), font=font_title)
draw.text((80, 100), "A união pioneira entre rigor de juiz de maratona e tutoria socrática baseada em IA", fill=(148, 163, 184), font=font_sub)

pillars = [
    {
        "x": 80, "w": 335,
        "title": "1. Validação por Oráculo",
        "badge": "SEM PROBLEMAS INVÁLIDOS",
        "badge_color": (56, 189, 248),
        "text": "Problemas inéditos gerados com oráculo duplo C++ compilado antes da entrega. Zero alucinação em casos de teste."
    },
    {
        "x": 450, "w": 335,
        "title": "2. Invariantes Matemáticos",
        "badge": "RAG ESTRUTURAL",
        "badge_color": (52, 211, 153),
        "text": "Recuperação de exercícios similares por propriedades profundas de complexidade e monotonicidade, não por palavras soltas."
    },
    {
        "x": 820, "w": 335,
        "title": "3. Tutoria Dialógica",
        "badge": "SEM SPOILER DE CÓDIGO",
        "badge_color": (251, 191, 36),
        "text": "Escada de pistas graduais guiando o aluno para a causa raiz do erro (TLE, WA), cultivando independência intelectual."
    },
    {
        "x": 1190, "w": 335,
        "title": "4. Cognição Espacial",
        "badge": "WHITEBOARD VIVO",
        "badge_color": (168, 85, 247),
        "text": "Canvas dinâmico de grafos acoplado à execução C++ com rastreamento da pilha de recursão em tempo real."
    }
]

card_y = 170
card_h = 360

for p in pillars:
    x, w = p["x"], p["w"]
    draw.rounded_rectangle([x, card_y, x + w, card_y + card_h], radius=16, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    
    draw.rounded_rectangle([x + 20, card_y + 20, x + w - 20, card_y + 55], radius=8, fill=(15, 23, 42), outline=p["badge_color"], width=1)
    draw.text((x + 30, card_y + 28), p["badge"], fill=p["badge_color"], font=font_badge)

    draw.text((x + 20, card_y + 80), p["title"], fill=(248, 250, 252), font=font_card_title)
    
    draw.line([x + 20, card_y + 120, x + w - 20, card_y + 120], fill=(51, 65, 85), width=1)
    
    # Texto
    draw.text((x + 20, card_y + 140), p["text"], fill=(203, 213, 225), font=font_card_body)

# Banner inferior de Encerramento e Abertura para Perguntas
box_y = 570
box_h = 240
draw.rounded_rectangle([80, box_y, 1525, box_y + box_h], radius=16, fill=(30, 41, 59), outline=(56, 189, 248), width=2)

draw.text((120, box_y + 35), "“Não ensinamos a máquina a programar pelo aluno. Ensinamos o aluno a pensar com a máquina.”", fill=(56, 189, 248), font=font_closing)

info_text = (
    "Autor: Brenno Phelipe Silva dos Santos  •  Disciplina: Fundamentos da Inteligência Artificial (FIA)\n"
    "Stack: Next.js 14, FastAPI, Sandbox POSIX, Gemini / OpenAI / Ollama Offline  •  365 Testes Pytest Aprovados\n"
    "Disponibilidade: Repositório com código aberto, suíte de testes de invariantes e suporte 100% offline."
)
draw.text((120, box_y + 90), info_text, fill=(148, 163, 184), font=font_card_body)

draw.rounded_rectangle([120, box_y + 165, 450, box_y + 215], radius=10, fill=(15, 23, 42), outline=(52, 211, 153), width=1)
draw.text((140, box_y + 178), "💬 Perguntas & Considerações da Banca", fill=(52, 211, 153), font=font_card_title)

out_path = os.path.join(ASSETS_DIR, 'diagrama_slide7_conclusao.png')
img.save(out_path, quality=95)
print(f"Gerado: {out_path}")
