import os
import base64

OUT_DIR = 'slides_apresentacao/academic_png'

def get_base64(num):
    path = os.path.join(OUT_DIR, f"academic_slide_{num:02d}.png")
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""

from build_academic_presentation_v2 import slides_9

html_str = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>AutoTutor CP — Apresentação Acadêmica Formal (FIA 2026)</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #060913;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      user-select: none;
    }
    .slide-wrapper {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px 24px;
      position: relative;
    }
    .slide {
      display: none;
      width: 100%;
      height: 100%;
      align-items: center;
      justify-content: center;
    }
    .slide.active {
      display: flex;
      animation: fadeIn 0.15s ease-in-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    .slide img {
      max-width: 100%;
      max-height: 100%;
      width: auto;
      height: auto;
      object-fit: contain;
      border-radius: 6px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.8);
    }
    .nav-bar {
      height: 52px;
      background: #0a0f1d;
      border-top: 1px solid #1e293b;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 28px;
      z-index: 100;
    }
    .btn {
      background: #151f32;
      color: #ffffff;
      border: 1px solid #334155;
      padding: 7px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.1s ease;
    }
    .btn:hover {
      background: #1e293b;
      border-color: #38bdf8;
    }
    .btn-accent {
      background: #0284c7;
      border-color: #38bdf8;
      color: #ffffff;
    }
    .counter {
      font-size: 14px;
      font-weight: 700;
      color: #facc15;
    }
    .notes-drawer {
      position: absolute;
      bottom: 52px;
      left: 0;
      right: 0;
      max-height: 260px;
      background: rgba(10, 15, 29, 0.98);
      backdrop-filter: blur(14px);
      border-top: 2px solid #facc15;
      padding: 20px 32px;
      overflow-y: auto;
      transform: translateY(100%);
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 90;
      box-shadow: 0 -12px 28px rgba(0,0,0,0.7);
    }
    .notes-drawer.open {
      transform: translateY(0);
    }
    .notes-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .notes-title {
      font-size: 14px;
      font-weight: 800;
      color: #facc15;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .notes-body {
      font-size: 15px;
      line-height: 1.6;
      color: #e2e8f0;
      white-space: pre-line;
    }
  </style>
</head>
<body>
  <div class="slide-wrapper">
"""

for s in slides_9:
    b64 = get_base64(s["num"])
    html_str += f"""
    <div class="slide {'active' if s['num'] == 1 else ''}" id="slide-{s['num']}">
      <img src="{b64}" alt="Slide {s['num']} - {s['title']}">
      <div class="notes-drawer" id="notes-{s['num']}">
        <div class="notes-header">
          <span class="notes-title">🎙 Roteiro Acadêmico Formal • Slide {s['num']} / 9 ({s['time']})</span>
          <span style="font-size: 12px; color: #94a3b8;">Pressione [N] para fechar</span>
        </div>
        <div class="notes-body">"{s['script']}"</div>
      </div>
    </div>
"""

html_str += """
  </div>

  <div class="nav-bar">
    <div style="display: flex; gap: 10px; align-items: center;">
      <button class="btn" onclick="prevSlide()" title="Seta Esquerda">← Anterior</button>
      <button class="btn" onclick="nextSlide()" title="Seta Direita / Barra de Espaço">Próximo →</button>
      <span class="counter" id="slideCount">Slide 1 de 9</span>
    </div>

    <div style="display: flex; gap: 10px; align-items: center;">
      <button class="btn btn-accent" onclick="toggleNotes()" title="Atalho: Tecla N">
        🎙 Roteiro Acadêmico [N]
      </button>
      <button class="btn" onclick="toggleFull()" title="Atalho: Tecla F">
        ⛶ Tela Cheia [F]
      </button>
    </div>
  </div>

  <script>
    let cur = 1;
    const total = 9;
    let openNotes = false;

    function show(n) {
      if (n < 1) n = 1;
      if (n > total) n = total;
      cur = n;

      for (let i = 1; i <= total; i++) {
        const el = document.getElementById(`slide-${i}`);
        if (el) {
          if (i === cur) {
            el.classList.add('active');
            const drawer = document.getElementById(`notes-${i}`);
            if (drawer) {
              if (openNotes) drawer.classList.add('open');
              else drawer.classList.remove('open');
            }
          } else {
            el.classList.remove('active');
          }
        }
      }

      document.getElementById('slideCount').innerText = `Slide ${cur} de ${total}`;
    }

    function nextSlide() { if (cur < total) show(cur + 1); }
    function prevSlide() { if (cur > 1) show(cur - 1); }

    function toggleNotes() {
      openNotes = !openNotes;
      const d = document.getElementById(`notes-${cur}`);
      if (d) d.classList.toggle('open', openNotes);
    }

    function toggleFull() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        if (document.exitFullscreen) document.exitFullscreen().catch(() => {});
      }
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') nextSlide();
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') prevSlide();
      else if (e.key === 'n' || e.key === 'N') toggleNotes();
      else if (e.key === 'f' || e.key === 'F') toggleFull();
      else if (e.key >= '1' && e.key <= '9') show(parseInt(e.key));
    });
  </script>
</body>
</html>
"""

with open("slides_apresentacao/Apresentacao_AutoTutor_CP_Academica.html", "w", encoding="utf-8") as f:
    f.write(html_str)

with open("Apresentacao_AutoTutor_CP_Academica.html", "w", encoding="utf-8") as f:
    f.write(html_str)

print("Apresentação HTML Acadêmica v2 (9 slides) gerada com sucesso!")
