import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = 'slides_apresentacao/assets'
onb_path = os.path.join(ASSETS_DIR, 'onboarding.png')
cal_path = os.path.join(ASSETS_DIR, 'calendar.png')

W, H = 1600, 900
comp = Image.new('RGB', (W, H), (15, 23, 42))
draw = ImageDraw.Draw(comp)

if os.path.exists(onb_path) and os.path.exists(cal_path):
    im_onb = Image.open(onb_path)
    im_cal = Image.open(cal_path)

    # Redimensiona cada um para caber lado a lado com bordas arredondadas e títulos
    # Largura de cada: 740, Altura: 700
    target_w = 750
    target_h = 700

    # Crop do centro para manter foco nos elementos principais
    im_onb_resized = im_onb.resize((target_w, target_h), Image.Resampling.LANCZOS)
    im_cal_resized = im_cal.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Cola lado a lado
    comp.paste(im_onb_resized, (40, 140))
    comp.paste(im_cal_resized, (810, 140))

    # Desenha molduras
    draw.rectangle([38, 138, 40 + target_w + 1, 140 + target_h + 1], outline=(56, 189, 248), width=2)
    draw.rectangle([808, 138, 810 + target_w + 1, 140 + target_h + 1], outline=(52, 211, 153), width=2)

    # Títulos dos painéis
    # Fontes
    font_p = ImageFont.load_default()
    try:
        font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except:
        font_h = font_sub = font_badge = font_p

    draw.text((40, 45), "Diagnóstico Adaptativo & Calendário Diário de Estudos", fill=(248, 250, 252), font=font_h)
    draw.text((40, 85), "O fluxo contínuo: da detecção de lacunas conceituais ao agendamento de repetição espaçada", fill=(148, 163, 184), font=font_sub)

    # Badges sobre cada tela
    draw.rectangle([50, 150, 420, 190], fill=(15, 23, 42), outline=(56, 189, 248), width=1)
    draw.text((60, 160), "1. Micro-Quiz & Detecção de Lacunas", fill=(56, 189, 248), font=font_badge)

    draw.rectangle([820, 150, 1220, 190], fill=(15, 23, 42), outline=(52, 211, 153), width=1)
    draw.text((830, 160), "2. Trilha & Calendário Espaçado", fill=(52, 211, 153), font=font_badge)

    out_path = os.path.join(ASSETS_DIR, 'composite_slide5_onboarding_calendar.png')
    comp.save(out_path, quality=95)
    print(f"Gerado: {out_path}")
