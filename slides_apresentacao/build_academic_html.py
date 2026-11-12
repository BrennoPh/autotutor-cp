import os
import base64

OUT_DIR = 'slides_apresentacao/academic_png'

def get_base64(num):
    path = os.path.join(OUT_DIR, f"academic_slide_{num:02d}.png")
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""

slides_meta = [
    {
        "num": 1,
        "time": "00:00 - 00:35 (35s)",
        "title": "Formulação do Problema Científico",
        "script": "Boa tarde aos membros da banca avaliadora. Na disciplina de Fundamentos da Inteligência Artificial, investigamos o problema da formação analítica em Ciência da Computação.\n\nExiste uma lacuna estrutural no aprendizado de algoritmos avançados: juízes online operam com vereditos booleanos opacos como Wrong Answer, sem explicitar a quebra do invariante lógico. Em contrapartida, LLMs genéricas entregam o código pronto, suprimindo o esforço cognitivo do discente e induzindo à atrofia do raciocínio analítico.\n\nO AutoTutor CP investiga e formaliza a integração entre execução determinística em sandbox C++, recuperação semântica por invariantes e mediação dialógica socrática."
    },
    {
        "num": 2,
        "time": "00:35 - 01:10 (35s)",
        "title": "Fundamentação Teórica",
        "script": "Nossa arquitetura fundamenta-se estritamente na literatura científica recente:\n\nPrimeiro, o AutoCode (publicado no ICLR 2026), que estabelece a validação por oráculo duplo: instâncias de problemas e baterias de testes de estresse são compiladas e verificadas cruzadamente antes da apresentação ao estudante, assegurando corretude matemática formal.\n\nSegundo, o OI-Assistant (IOI 2025), que propõe a recuperação estruturada por propriedades matemáticas profundas e classes assintóticas.\n\nE terceiro, o CODIGEN (IEEE 2025), que formaliza a escada gradual de pistas socráticas sem alucinação de sintaxe."
    },
    {
        "num": 3,
        "time": "01:10 - 01:55 (45s)",
        "title": "Limitações Estruturais do RAG Convencional",
        "script": "Uma contribuição central deste trabalho é demonstrar por que o RAG clássico falha em domínios algorítmicos:\n\nPrimeiro: a falácia da proximidade léxica. Dois problemas que utilizam a mesma narrativa metafórica — por exemplo, uma malha rodoviária rural — são agrupados no espaço denso genérico por causa das palavras superficiais. No entanto, um deles exige caminho mínimo O(E log V) via Dijkstra, enquanto o outro exige corte mínimo e fluxo máximo em O(V^2 E) via algoritmo de Dinic. O RAG tradicional recupera o paradigma incorreto.\n\nSegundo: a insensibilidade assintótica. Limites de N <= 20 demandam busca com bitmask O(2^N * N), enquanto N <= 10^5 exige busca binária ou programação dinâmica com Convex Hull Trick. O RAG clássico é cego a ordens de grandeza.\n\nTerceiro: o vazamento de gabaritos. O RAG convencional injeta a solução no prompt, gerando respostas prontas que anulam o ganho pedagógico."
    },
    {
        "num": 4,
        "time": "01:55 - 02:40 (45s)",
        "title": "Metodologia: RAG Multiespaço e Invariantes",
        "script": "Para mitigar essas limitações, implementamos a arquitetura multiespaço inspirada no OI-Assistant, decompondo a representação em três espaços vetoriais ortogonais:\n\nEspaço 1: Enunciados Formais, que isola a especificação matemática do ruído narrativo.\nEspaço 2: Conceitos Algorítmicos e Invariantes, indexando propriedades de monotonicidade, subestrutura ótima e dualidade.\nEspaço 3: Resumos Estruturais e Limites, que modela restrições temporais de 1.0 a 2.0 segundos e memória de 256 megabytes.\n\nCalculamos uma métrica de similaridade linearmente ponderada, seguida de reranking semântico via LLM, garantindo que o exercício análogo compartilhe a mesma assinatura assintótica."
    },
    {
        "num": 5,
        "time": "02:40 - 03:20 (40s)",
        "title": "AI Memory Longitudinal e Engenharia de Prompt",
        "script": "O sistema elimina a volatilidade de sessões efêmeras através do pipeline de AI Memory: um ciclo contínuo de Captura de falhas, Consolidação de padrões de dificuldade, Recuperação contextual e Handoff entre agentes, persistido com transações ACID em SQLite.\n\nNa Engenharia de Prompt, empregamos delimitação XML estrita (<role>, <context>, <constraints>) e guardrails matemáticos de Zero-Leakage.\n\nMesmo sob ataques deliberados de injeção de prompt simulados em nossa suíte com a persona adversarial Diana, o tutor intercepta a tentativa e mantém rigorosamente a postura dialógica socrática."
    },
    {
        "num": 6,
        "time": "03:20 - 04:05 (45s)",
        "title": "Evidências Empíricas: Workspace e Whiteboard",
        "script": "Apresentamos aqui as evidências empíricas da plataforma em operação real:\n\nÀ esquerda, o Workspace de Resolução: integra o editor Monaco em C++17 sob sandbox isolado pelo isolated_judge.py com Bubblewrap e limites POSIX de 256MB. O console demonstra a captura determinística de Time Limit Exceeded em um laço quadrático, acionando o AI Tutor no dock lateral com dicas socráticas orientadas por invariantes.\n\nÀ direita, o Quadro Branco Algorítmico: o aluno projeta o grafo topológico acoplado à execução C++. Conforme o algoritmo de busca percorre os vértices, os estados mudam de cor e a Call Stack de recursão é renderizada ao vivo, tornando observável a dinâmica de memória e o backtracking."
    },
    {
        "num": 7,
        "time": "04:05 - 04:40 (35s)",
        "title": "Diagnóstico Cognitivo e Escalonamento Espaçado",
        "script": "Para fundamentar a adaptação pedagógica sem autoavaliações ilusórias, o sistema implementa:\n\nÀ esquerda, o Onboarding Diagnóstico: micro-quiz calibrado com trechos formais de código avaliando Programação Dinâmica, Grafos, Busca Binária e Soma de Prefixos. O algoritmo mapeia com precisão as lacunas conceituais do discente.\n\nÀ direita, o Calendário Adaptativo: o motor projeta um cronograma baseado na curva de esquecimento de Ebbinghaus, intercalando leitura analítica no Study Reader e desafios práticos na Arena, respeitando a carga horária do estudante."
    },
    {
        "num": 8,
        "time": "04:40 - 05:00 (20s)",
        "title": "Validação Empírica, Limitações e Arguição",
        "script": "Para homologar a integridade matemática da solução, submetemos a arquitetura a uma suíte de 365 testes unitários e de integração no Pytest com 100% de aprovação, e simulamos 1 milhão de discentes sintéticos cobrindo 3 milhões de jornadas completas sem quebra de invariantes.\n\nComo limitação, identificamos a latência do reranking em modelos de grande porte, contornável via destilação local.\n\nAgradecemos a atenção da banca examinadora e estamos abertos para a discussão técnica e metodológica."
    }
]

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
    /* Barra de Navegação */
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
    /* Gaveta de Roteiro Acadêmico */
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

for s in slides_meta:
    b64 = get_base64(s["num"])
    html_str += f"""
    <div class="slide {'active' if s['num'] == 1 else ''}" id="slide-{s['num']}">
      <img src="{b64}" alt="Slide {s['num']} - {s['title']}">
      <div class="notes-drawer" id="notes-{s['num']}">
        <div class="notes-header">
          <span class="notes-title">🎙 Roteiro Acadêmico Formal • Slide {s['num']} / 8 ({s['time']})</span>
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
      <span class="counter" id="slideCount">Slide 1 de 8</span>
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
    const total = 8;
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
      else if (e.key >= '1' && e.key <= '8') show(parseInt(e.key));
    });
  </script>
</body>
</html>
"""

with open("slides_apresentacao/Apresentacao_AutoTutor_CP_Academica.html", "w", encoding="utf-8") as f:
    f.write(html_str)

with open("Apresentacao_AutoTutor_CP_Academica.html", "w", encoding="utf-8") as f:
    f.write(html_str)

print("Apresentação HTML Acadêmica gerada com sucesso!")
