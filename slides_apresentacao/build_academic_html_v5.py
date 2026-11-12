import os
import base64

OUT_DIR = 'slides_apresentacao/academic_png'

slides_data = [
    {
        "num": 1,
        "time": "00:00 - 00:15 (15s)",
        "badge": "UNIVERSIDADE FEDERAL DE SERGIPE",
        "title": "AutoTutor CP: Tutoria Inteligente e Verificação Formal em Algoritmos",
        "subtitle": "Departamento de Computação · Disciplina: FUNDAMENTOS DA INTELIGÊNCIA ARTIFICIAL",
        "script": """\"Boa tarde aos membros da banca examinadora e ao professor Yuri Tavares dos Passos. Meu nome é Brenno Phelipe Silva dos Santos, discente do Departamento de Computação da Universidade Federal de Sergipe. Apresento hoje o projeto AutoTutor CP, desenvolvido no âmbito da disciplina de Fundamentos da Inteligência Artificial.\""""
    },
    {
        "num": 2,
        "time": "00:15 - 00:45 (30s)",
        "badge": "FORMULAÇÃO DO PROBLEMA CIENTÍFICO",
        "title": "O Abismo Cognitivo no Julgamento Automático",
        "subtitle": "A lacuna estrutural entre a teoria analítica e o veredito determinístico assintótico",
        "script": """\"Investigamos o problema da formação analítica em Ciência da Computação. Existe uma lacuna estrutural no aprendizado de algoritmos: juízes online operam com vereditos booleanos opacos como Wrong Answer, sem explicitar a quebra do invariante lógico. Em contrapartida, LLMs genéricas entregam o código pronto, gerando atrofia do raciocínio analítico.

O AutoTutor CP formaliza a integração entre execução determinística em sandbox C++, recuperação semântica por invariantes e mediação dialógica socrática.\""""
    },
    {
        "num": 3,
        "time": "00:45 - 01:15 (30s)",
        "badge": "FUNDAMENTAÇÃO TEÓRICA",
        "title": "A Tríade de Pesquisa: Fundamentação na Literatura Internacional",
        "subtitle": "Três publicações formais recentes em conferências de ponta (ICLR, IOI, IEEE VL/HCC)",
        "script": """\"Nossa arquitetura fundamenta-se estritamente na literatura científica recente:

Do AutoCode (ICLR 2026), adotamos a validação por oráculo duplo: enunciados e testes de estresse são compilados antes do consumo do discente, garantindo corretude formal.
Do OI-Assistant (IOI 2025), extraímos a recuperação semântica estruturada por propriedades matemáticas profundas.
E do CODIGEN (IEEE 2025), formalizamos a escada gradual de pistas socráticas sem alucinação.\""""
    },
    {
        "num": 4,
        "time": "01:15 - 01:45 (30s)",
        "badge": "ANÁLISE CRÍTICA DE IA",
        "title": "Limitações Estruturais: Por Que o RAG Convencional Falha em Algoritmos?",
        "subtitle": "A falácia da similaridade léxica, insensibilidade assintótica e vazamento precoce de soluções",
        "script": """\"Demonstramos analiticamente por que o RAG clássico falha em domínios algorítmicos:

Primeiro: a falácia da proximidade léxica. Dois problemas que utilizam a mesma historinha metafórica são aproximados no espaço denso genérico pelas palavras superficiais. No entanto, um exige Dijkstra O(E log V) e o outro Fluxo Máximo O(V^2 E). O RAG tradicional recupera o paradigma incorreto.

Segundo: a insensibilidade assintótica. Limites de N <= 20 demandam busca com bitmask O(2^N * N), enquanto N <= 10^5 exige programação dinâmica. O RAG comum é cego a ordens de grandeza.

Terceiro: o vazamento de gabaritos, que anula a construção cognitiva.\""""
    },
    {
        "num": 5,
        "time": "01:45 - 02:20 (35s)",
        "badge": "METODOLOGIA PROPOSTA",
        "title": "Metodologia: RAG Multiespaço e Fórmula de Scores TF-IDF",
        "subtitle": "Decomposição em 3 espaços vetoriais ortogonais e validação matemática de corretude",
        "script": """\"Para mitigar essas limitações, implementamos a arquitetura do OI-Assistant decompondo o espaço em três vetores ortogonais:

Espaço 1: Enunciados Formais, isolando a especificação do ruído narrativo.
Espaço 2: Conceitos Algorítmicos e Invariantes, indexando propriedades matemáticas.
Espaço 3: Resumos Estruturais e Limites, modelando restrições de tempo e memória.

A métrica de similaridade linear ponderada calcula:
Score(q, d) = 0.25 · TFIDF_enunciado + 0.45 · TFIDF_essência_matemática + 0.30 · TFIDF_estratégia.

O peso preponderante de 0.45 na essência matemática prioriza a relação de recorrência em vez da narrativa, seguido de reranking semântico via LLM.\""""
    },
    {
        "num": 6,
        "time": "02:20 - 02:50 (30s)",
        "badge": "MODELAGEM LONGITUDINAL",
        "title": "AI Memory Longitudinal e Engenharia de Prompt Formal",
        "subtitle": "Persistência de perfil cognitivo em SQLite e contenção estrita de prompt injection",
        "script": """\"O pipeline de AI Memory opera um ciclo contínuo de Captura de falhas, Consolidação de padrões de dificuldade, Recuperação contextual e Handoff entre agentes, persistido com transações ACID em SQLite.

Na Engenharia de Prompt, empregamos delimitação XML estrita (<role>, <context>, <constraints>) e guardrails matemáticos de Zero-Leakage.

Mesmo sob ataques deliberados de injeção de prompt simulados em nossa suíte com a persona adversarial Diana, o tutor conteve 100% das tentativas e manteve rigorosamente a postura dialógica socrática.\""""
    },
    {
        "num": 7,
        "time": "02:50 - 03:25 (35s)",
        "badge": "EVIDÊNCIAS EXPERIMENTAIS (SISTEMA REAL)",
        "title": "Evidências Empíricas: O Workspace de Execução e o Quadro Branco",
        "subtitle": "Sandbox C++17 com limites POSIX, detecção determinística de TLE/WA e visualização de grafos",
        "script": """\"Apresentamos aqui as evidências empíricas da plataforma em operação real:

À esquerda, o Workspace de Resolução com editor Monaco em C++17 sob sandbox isolado pelo isolated_judge.py com Bubblewrap e limites POSIX de 256MB. O console demonstra a captura determinística de Time Limit Exceeded aos 2.0 segundos, acionando o AI Tutor no dock lateral com dicas socráticas orientadas por invariantes.

À direita, o Quadro Branco Algorítmico: o discente projeta o grafo topológico acoplado à execução C++. Conforme o algoritmo de busca percorre os vértices, a Call Stack de recursão é renderizada ao vivo, tornando observável a dinâmica de memória e o backtracking.\""""
    },
    {
        "num": 8,
        "time": "03:25 - 03:55 (30s)",
        "badge": "DIAGNÓSTICO E ADAPTAÇÃO",
        "title": "Diagnóstico Cognitivo e Escalonamento Espaçado (Ebbinghaus)",
        "subtitle": "Micro-quiz objetivo de código e agendamento adaptativo de repetição espaçada",
        "script": """\"Para fundamentar a adaptação pedagógica sem autoavaliações ilusórias:

À esquerda, o Onboarding com micro-quiz calibrado de trechos reais de código C++ avaliando Programação Dinâmica, Grafos, Busca Binária e Soma de Prefixos, mapeando com precisão as lacunas conceituais do discente.

À direita, o Calendário Adaptativo projetando um cronograma baseado na curva de esquecimento de Ebbinghaus, intercalando leitura analítica no Study Reader e desafios práticos na Arena.\""""
    },
    {
        "num": 9,
        "time": "03:55 - 04:20 (25s)",
        "badge": "ESTUDO DE CASO REAL (ETAPAS 01 A 04)",
        "title": "A Dança Síncrona na Prática: Caso Real de TLE no Workspace",
        "subtitle": "Ciclo integrado de detecção determinística de TLE e indexação na memória cognitiva",
        "script": """\"Vejam a integração síncrona operando em 7 etapas diante de um caso real de TLE submetido no Workspace:

Etapa 1: O discente submete um código em C++17 com uma busca em largura que insere vértices redundantes na fila.
Etapa 2: O Isolated Judge confinado em Bubblewrap emite o veredito determinístico: Time Limit Exceeded aos 2.0 segundos.
Etapa 3: A LearnerMemory intercepta o veredito e persiste o evento em SQLite FTS5, gravando no perfil do discente a reincidência de TLE em Grafos/BFS.
Etapa 4: O motor OI-Assistant calcula os 3 espaços TF-IDF e recupera a invariante estrutural da BFS violada.\""""
    },
    {
        "num": 10,
        "time": "04:20 - 04:45 (25s)",
        "badge": "ESTUDO DE CASO REAL (ETAPAS 05 A 07)",
        "title": "A Dança Síncrona na Prática: Intervenção Socrática e Zero-Leakage",
        "subtitle": "Da teoria canônica à intervenção na tela do aluno preservando o esforço cognitivo",
        "script": """\"O ciclo completa-se com rigor pedagógico:

Etapa 5: O KnowledgeBase busca na literatura de base o lema de Szwarcfiter sobre exploração por camadas em O(V + E).
Etapa 6: O CodigenTutor aplica o guardrail de Zero-Leakage e formula a intervenção socrática.
Etapa 7: Na tela do estudante, o tutor intervém cirurgicamente sem entregar o código:
'Percebi que seu laço while executa muito mais iterações do que a quantidade de salas (V). O que acontece se uma mesma sala for inserida na fila mais de uma vez antes de ser processada? Em que momento exato você deve marcar que ela já foi descoberta?'

O discente é conduzido à causa raiz assintótica por reflexão própria.\""""
    },
    {
        "num": 11,
        "time": "04:45 - 04:50 (05s)",
        "badge": "VALIDAÇÃO FORMAL E CONCLUSÕES",
        "title": "Validação Empírica, Conclusões e Resultados Experimentais",
        "subtitle": "365 testes Pytest (100% pass), simulação com 1.000.000 de discentes sintéticos",
        "script": """\"Para homologar a integridade matemática da solução, submetemos a arquitetura a uma suíte de 365 testes unitários e de integração no Pytest com 100% de aprovação, e simulamos 1 milhão de discentes sintéticos cobrindo 3 milhões de jornadas completas sem quebra de invariantes.\""""
    },
    {
        "num": 12,
        "time": "04:50 - 04:55 (05s)",
        "badge": "LITERATURA CIENTÍFICA",
        "title": "Referências Bibliográficas e Fundamentos Teóricos",
        "subtitle": "AutoCode (ICLR 2026), OI-Assistant (IOI 2025), CODIGEN (IEEE 2025), Cormen & Szwarcfiter",
        "script": """\"As referências que fundamentam nosso trabalho englobam as publicações de ponta do AutoCode no ICLR 2026, OI-Assistant no IOI 2025, CODIGEN no IEEE VL/HCC 2025, além da literatura canônica de algoritmos de Cormen e Szwarcfiter.\""""
    },
    {
        "num": 13,
        "time": "04:55 - 05:00 (05s)",
        "badge": "ARGUIÇÃO DA BANCA",
        "title": "Muito Obrigado! — AutoTutor CP",
        "subtitle": "Brenno Phelipe Silva dos Santos · Prof. Dr. YURI TAVARES DOS PASSOS · UFS",
        "script": """\"Agradeço a atenção do professor Yuri Tavares dos Passos e de todos os presentes. Estou à disposição para as perguntas e a discussão técnica da banca examinadora. Muito obrigado.\""""
    }
]

def get_base64_canva(num):
    path = os.path.join(OUT_DIR, f"canva_slide-{num:02d}.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>AutoTutor CP — Apresentação UFS (13 Slides)</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: #070B14;
      color: #E2E8F0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }}
    header {{
      background: #0D1527;
      border-bottom: 1px solid #1E293B;
      padding: 10px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 56px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .brand-title {{
      font-weight: 700;
      font-size: 16px;
      color: #FFFFFF;
      letter-spacing: -0.3px;
    }}
    .badge {{
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(56, 189, 248, 0.15);
      color: #38BDF8;
      border: 1px solid rgba(56, 189, 248, 0.3);
      font-weight: 600;
      text-transform: uppercase;
    }}
    .controls {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .nav-btn {{
      background: #1E293B;
      border: 1px solid #334155;
      color: #F8FAFC;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      transition: all 0.15s ease;
    }}
    .nav-btn:hover {{
      background: #334155;
      border-color: #475569;
    }}
    .counter {{
      font-size: 14px;
      color: #94A3B8;
      font-weight: 500;
      min-width: 90px;
      text-align: center;
    }}
    .counter span {{
      color: #FACC15;
      font-weight: 700;
    }}
    .timer-pill {{
      background: rgba(250, 204, 21, 0.1);
      border: 1px solid rgba(250, 204, 21, 0.3);
      color: #FACC15;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
    }}
    main {{
      flex: 1;
      display: flex;
      overflow: hidden;
      position: relative;
    }}
    .slide-viewer {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      background: #070B14;
      position: relative;
    }}
    .slide-frame {{
      max-width: 100%;
      max-height: 100%;
      aspect-ratio: 16 / 9;
      box-shadow: 0 20px 40px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.08);
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      background: #0A0F1D;
    }}
    .slide-img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }}
    .notes-panel {{
      width: 440px;
      background: #0C1220;
      border-left: 1px solid #1E293B;
      display: flex;
      flex-direction: column;
      padding: 20px;
      overflow-y: auto;
      transition: margin-right 0.25s ease;
    }}
    .notes-panel.collapsed {{
      margin-right: -440px;
    }}
    .notes-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 1px solid #1E293B;
    }}
    .notes-title {{
      font-size: 14px;
      font-weight: 700;
      color: #F8FAFC;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .meta-card {{
      background: #151F32;
      border: 1px solid #1E293B;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 14px;
    }}
    .meta-label {{
      font-size: 11px;
      color: #64748B;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .meta-val {{
      font-size: 13px;
      color: #E2E8F0;
      line-height: 1.4;
    }}
    .script-box {{
      background: #111A2C;
      border: 1px solid #1E293B;
      border-left: 3px solid #38BDF8;
      border-radius: 8px;
      padding: 14px;
      font-size: 13.5px;
      line-height: 1.6;
      color: #F1F5F9;
      white-space: pre-wrap;
      flex: 1;
    }}
    .canva-link-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #0284C7;
      color: #FFFFFF;
      text-decoration: none;
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      transition: background 0.15s;
    }}
    .canva-link-btn:hover {{
      background: #0369A1;
    }}
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-title">AutoTutor CP — Apresentação UFS</div>
      <div class="badge" id="slide-badge">UNIVERSIDADE FEDERAL DE SERGIPE</div>
      <a href="https://www.canva.com/design/DAHaulNcItA/yoUBjlsVEz-kK4MvXQjdSg/edit" target="_blank" class="canva-link-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
        Abrir no Canva
      </a>
    </div>

    <div class="controls">
      <button class="nav-btn" onclick="prevSlide()">◀ Anterior</button>
      <div class="counter">Slide <span id="current-num">1</span> / 13</div>
      <button class="nav-btn" onclick="nextSlide()">Próximo ▶</button>
      <div class="timer-pill" id="slide-time">⏱ 00:00 - 00:15 (15s)</div>
      <button class="nav-btn" onclick="toggleNotes()">Notas [N]</button>
      <button class="nav-btn" onclick="toggleFullScreen()">Tela Cheia [F]</button>
    </div>
  </header>

  <main>
    <div class="slide-viewer" onclick="nextSlide()">
      <div class="slide-frame">
        <img id="slide-img" class="slide-img" src="" alt="Slide">
      </div>
    </div>

    <aside class="notes-panel" id="notes-panel">
      <div class="notes-header">
        <div class="notes-title">
          <span>🎙️</span> Roteiro Falado (Script da Apresentação)
        </div>
        <button class="nav-btn" style="padding: 2px 8px; font-size: 11px;" onclick="toggleNotes()">✕</button>
      </div>

      <div class="meta-card">
        <div class="meta-label">Título do Slide</div>
        <div class="meta-val" id="slide-title">AutoTutor CP</div>
        <div class="meta-label" style="margin-top: 8px;">Subtítulo Científico</div>
        <div class="meta-val" id="slide-subtitle" style="color: #94A3B8; font-size: 12px;"></div>
      </div>

      <div class="script-box" id="slide-script"></div>
    </aside>
  </main>

  <script>
    const slides = [
"""

for s in slides_data:
    b64 = get_base64_canva(s["num"])
    script_escaped = s["script"].replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    title_escaped = s["title"].replace('"', '\\"')
    sub_escaped = s["subtitle"].replace('"', '\\"')
    badge_escaped = s["badge"].replace('"', '\\"')
    time_escaped = s["time"].replace('"', '\\"')
    html_content += f"""      {{
        num: {s["num"]},
        time: "{time_escaped}",
        badge: "{badge_escaped}",
        title: "{title_escaped}",
        subtitle: "{sub_escaped}",
        script: "{script_escaped}",
        img: "{b64}"
      }},\n"""

html_content += """    ];

    let currentIndex = 0;

    function renderSlide(idx) {
      if (idx < 0) idx = 0;
      if (idx >= slides.length) idx = slides.length - 1;
      currentIndex = idx;

      const s = slides[currentIndex];
      document.getElementById('slide-img').src = s.img;
      document.getElementById('current-num').innerText = s.num;
      document.getElementById('slide-badge').innerText = s.badge;
      document.getElementById('slide-time').innerText = "⏱ " + s.time;
      document.getElementById('slide-title').innerText = s.title;
      document.getElementById('slide-subtitle').innerText = s.subtitle;
      document.getElementById('slide-script').innerText = s.script.replace(/^"|"$/g, '');
    }

    function nextSlide() {
      if (currentIndex < slides.length - 1) {
        renderSlide(currentIndex + 1);
      }
    }

    function prevSlide() {
      if (currentIndex > 0) {
        renderSlide(currentIndex - 1);
      }
    }

    function toggleNotes() {
      document.getElementById('notes-panel').classList.toggle('collapsed');
    }

    function toggleFullScreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {});
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      }
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        nextSlide();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        prevSlide();
      } else if (e.key === 'n' || e.key === 'N') {
        toggleNotes();
      } else if (e.key === 'f' || e.key === 'F') {
        toggleFullScreen();
      }
    });

    renderSlide(0);
  </script>
</body>
</html>
"""

out_html = 'Apresentacao_AutoTutor_CP_Academica.html'
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML gerado com sucesso em {out_html} ({len(html_content)} bytes)")
