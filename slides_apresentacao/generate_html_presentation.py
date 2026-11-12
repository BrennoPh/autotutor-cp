import os
import base64

SLIDES_DIR = 'slides_apresentacao/slides_png'

def get_base64_image(filename):
    path = os.path.join(SLIDES_DIR, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            return f"data:image/png;base64,{data}"
    return ""

slides = [
    {
        "num": 1,
        "time": "00:00 - 00:40 (40s)",
        "badge": "O GANCHO & O PROBLEMA",
        "title": "O Abismo na Programação Competitiva",
        "image": get_base64_image("slide_01.png"),
        "script": "Boa tarde à banca avaliadora. Todo estudante de Ciência da Computação conhece essa dor: você compreende a teoria em aula, abre o juiz online e recebe um seco: 'Wrong Answer no Teste 4'. O juiz diz O QUE está errado, mas nunca o PORQUÊ.\n\nDo outro lado, quando o aluno pede ajuda a uma IA genérica, ela cospe o código pronto. Isso destrói o processo pedagógico: o aluno copia, passa o teste, mas não desenvolve musculatura algorítmica.\n\nFoi para resolver esse abismo que criamos o AutoTutor CP: uma plataforma que integra juiz de execução real em C++ com tutoria socrática guiada por fundamentos científicos da literatura.",
        "stage_cue": "Olhar seguro para a banca, braços abertos ao falar do 'abismo', apontar para a comparação entre o juiz punitivo e a cola da IA genérica."
    },
    {
        "num": 2,
        "time": "00:40 - 01:20 (40s)",
        "badge": "FUNDAMENTAÇÃO CIENTÍFICA",
        "title": "A Tríade de Pesquisa: Ciência por Trás da Solução",
        "image": get_base64_image("slide_02.png"),
        "script": "O AutoTutor CP não é um simples invólucro de API comercial. Ele é fundamentado em três publicações de ponta da literatura:\n\nPrimeiro, AutoCode (ICLR 2026): os problemas inéditos são gerados em par com um oráculo C++ e suite de testes. O sistema compila e valida cruzadamente antes de exibir ao aluno, garantindo zero problemas inválidos.\n\nSegundo, OI-Assistant (IOI 2025): nosso RAG recupera exercícios e analogias pela essência matemática e invariantes do algoritmo — como subestrutura ótima ou monotonicidade —, e não por palavras soltas.\n\nE terceiro, CODIGEN (IEEE VL/HCC 2025): o tutor opera sob restrições cognitivas estritas. Ele diagnostica a quebra de invariantes e oferece uma escada gradual de dicas, impedindo que o aluno veja a solução antes de exercitar o raciocínio.",
        "stage_cue": "Postura acadêmica firme. Aponte para cada um dos 3 pilares com clareza mostrando o rigor metodológico."
    },
    {
        "num": 3,
        "time": "01:20 - 02:10 (50s)",
        "badge": "DEMONSTRAÇÃO DE PRODUTO 1",
        "title": "O Workspace de Resolução & O Juiz Online C++",
        "image": get_base64_image("slide_03.png"),
        "script": "Esta é a tela de resolução do estudante. Do lado esquerdo, temos a especificação formal do problema com restrições assintóticas de tempo e memória. No centro, o editor Monaco rodando C++17.\n\nAo submeter o código, a execução não roda em ambiente desprotegido: ela é despachada para o nosso juiz isolado 'isolated_judge.py', compilada via G++ com limites rígidos POSIX de 256MB e contenção por Bubblewrap.\n\nObservem o console: o juiz detectou Time Limit Exceeded. Em vez de deixar o aluno desamparado, o tutor socrático analisa o código submetido e intervém: 'Percebeu que para cada elemento você percorre todo o vetor novamente? Como manter essa busca em O(1) usando um acumulador de prefixo?'\n\nA IA não dá o código pronto. Ela guia o aluno exatamente para a quebra de complexidade.",
        "stage_cue": "Aponte para o editor Monaco no centro, depois para o console do juiz embaixo, e finalize destacando o painel lateral do tutor socrático."
    },
    {
        "num": 4,
        "time": "02:10 - 03:00 (50s)",
        "badge": "DEMONSTRAÇÃO DE PRODUTO 2",
        "title": "O Quadro Branco Interativo de Grafos (Whiteboard)",
        "image": get_base64_image("slide_04.png"),
        "script": "Um dos maiores gargalos cognitivos em computação é a abstração espacial de ponteiros e grafos. Por isso desenvolvemos o nosso Quadro Branco Interativo.\n\nAqui o aluno constrói o grafo livremente ou importa a topologia do problema. Ele adiciona vértices, conecta arestas direcionadas ou ponderadas e acopla a implementação do algoritmo de busca — como DFS, BFS ou Dijkstra.\n\nAo acionar a execução passo a passo, o motor sincroniza o runtime C++ com a malha visual: os nós mudam de cor conforme o ciclo de vida da busca, e a pilha de memória de recursão é desenhada ao vivo ao lado.\n\nO estudante enxerga visualmente o exato momento em que o backtracking ocorre, desmistificando o comportamento da pilha de execução do sistema.",
        "stage_cue": "Destaque o grafo visual com os nós interativos e a pilha de recursão viva ao lado, enfatizando a redução da carga cognitiva de abstração espacial."
    },
    {
        "num": 5,
        "time": "03:00 - 03:50 (50s)",
        "badge": "DEMONSTRAÇÃO DE PRODUTO 3",
        "title": "Diagnóstico Adaptativo & Calendário Diário Espaçado",
        "image": get_base64_image("slide_05.png"),
        "script": "Nenhum estudante começa do mesmo patamar. Por isso, eliminamos trilhas estáticas lineares que tratam todos como iguais.\n\nNa primeira tela à esquerda, no Onboarding, o estudante responde a um micro-quiz diagnóstico calibrado. Nosso backend processa o padrão de respostas e mapeia com precisão matemática os tópicos dominados e as lacunas conceituais — por exemplo, forte em recursão, mas com lacuna em programação dinâmica.\n\nA partir desse perfil, o motor algorítmico gera instantaneamente o Calendário Adaptativo à direita.\n\nReparem no equilíbrio: tarefas teóricas no Study Reader intercaladas com desafios práticos na Arena, respeitando o ritmo e a rotina do aluno com repetição espaçada. Toda a jornada é orientada por dados pedagógicos reais.",
        "stage_cue": "Aponte primeiro para a esquerda mostrando a detecção de lacunas conceituais, depois para a direita mostrando o calendário gerado sob medida."
    },
    {
        "num": 6,
        "time": "03:50 - 04:30 (40s)",
        "badge": "ARQUITETURA & RESILIÊNCIA",
        "title": "Engenharia de Software de Alta Resiliência",
        "image": get_base64_image("slide_06.png"),
        "script": "Para garantir confiabilidade de produção, nossa arquitetura foi projetada em camadas estritamente desacopladas:\n\nO frontend roda em Next.js 14 App Router com tipagem estrita TypeScript e design ergonômico sóbrio. O backend é impulsionado por FastAPI assíncrono e persistência transacional em SQLite.\n\nA execução de código utiliza sandbox Bubblewrap com limites POSIX, contendo com sucesso vazamentos de memória e fork-bombs.\n\nE um detalhe crucial para ambientes acadêmicos: nosso motor de IA é híbrido. Ele pode operar com Google Gemini ou OpenAI em nuvem, mas funciona 100% OFFLINE através do Ollama local, sem depender de internet.\n\nToda essa estrutura foi homologada com 365 testes no Pytest e auditada com um milhão de jornadas simuladas.",
        "stage_cue": "Tom de voz firme e técnico. Destaque os números de homologação e a capacidade de operar 100% offline sem internet."
    },
    {
        "num": 7,
        "time": "04:30 - 05:00 (30s)",
        "badge": "CONCLUSÃO & PERGUNTAS",
        "title": "Impacto Formativo & Encerramento",
        "image": get_base64_image("slide_07.png"),
        "script": "O AutoTutor CP resgata o propósito essencial do ensino de computação: não se trata de decorar sintaxe ou copiar código pronto de uma IA, mas de aprender a raciocinar algoritmicamente diante do desconhecido.\n\nUnindo pesquisa acadêmica validada, sandbox de execução segura e tutoria socrática adaptativa, entregamos uma solução pronta para transformar o treinamento de programação competitiva.\n\nAgradeço imensamente a atenção de todos os professores e membros da banca, e estamos abertos para as considerações e perguntas.",
        "stage_cue": "Pausa de 2 segundos. Postura ereta, respiração tranquila, olhar nos olhos dos avaliadores aguardando as perguntas."
    }
]

html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutoTutor CP — Apresentação Oficial (5 Minutos)</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #090d16;
      color: #f8fafc;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      user-select: none;
    }}
    .presentation-container {{
      position: relative;
      width: 100vw;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    .slide {{
      display: none;
      flex: 1;
      align-items: center;
      justify-content: center;
      padding: 16px 32px;
      height: calc(100vh - 56px);
      position: relative;
    }}
    .slide.active {{
      display: flex;
      animation: fadeIn 0.2s ease-in-out;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
    .slide img {{
      max-width: 100%;
      max-height: 100%;
      width: auto;
      height: auto;
      object-fit: contain;
      border-radius: 8px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }}
    /* Barra de Navegação Inferior */
    .controls-bar {{
      height: 56px;
      background: #0f172a;
      border-top: 1px solid #1e293b;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 32px;
      z-index: 100;
    }}
    .btn {{
      background: #1e293b;
      color: #f8fafc;
      border: 1px solid #334155;
      padding: 8px 18px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .btn:hover {{
      background: #334155;
      border-color: #475569;
    }}
    .btn-primary {{
      background: #0284c7;
      border-color: #38bdf8;
    }}
    .btn-primary:hover {{
      background: #0369a1;
    }}
    .slide-counter {{
      font-size: 14px;
      font-weight: 700;
      color: #94a3b8;
      font-variant-numeric: tabular-nums;
    }}
    /* Gaveta de Roteiro Falado (Speaker Notes) */
    .notes-drawer {{
      position: absolute;
      bottom: 56px;
      left: 0;
      right: 0;
      max-height: 280px;
      background: rgba(15, 23, 42, 0.98);
      backdrop-filter: blur(16px);
      border-top: 2px solid #38bdf8;
      padding: 24px 36px;
      overflow-y: auto;
      transform: translateY(100%);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 90;
      box-shadow: 0 -15px 30px rgba(0, 0, 0, 0.6);
    }}
    .notes-drawer.open {{
      transform: translateY(0);
    }}
    .notes-title {{
      font-size: 13px;
      font-weight: 800;
      color: #38bdf8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .notes-content {{
      font-size: 16px;
      color: #f1f5f9;
      line-height: 1.6;
      white-space: pre-line;
      margin-bottom: 14px;
    }}
    .cue-box {{
      background: rgba(52, 211, 153, 0.1);
      border-left: 3px solid #34d399;
      padding: 10px 14px;
      border-radius: 4px;
      font-size: 14px;
      color: #a7f3d0;
    }}
  </style>
</head>
<body>
  <div class="presentation-container">
"""

for s in slides:
    html_template += f"""
    <!-- SLIDE {s['num']} -->
    <div class="slide {'active' if s['num'] == 1 else ''}" id="slide-{s['num']}">
      <img src="{s['image']}" alt="Slide {s['num']} - {s['title']}">
      
      <!-- Notas do Orador -->
      <div class="notes-drawer" id="notes-{s['num']}">
        <div class="notes-title">
          <span>🎙 Roteiro Falado • Slide {s['num']} ({s['time']})</span>
          <span style="font-size: 12px; color: #94a3b8; font-weight: normal;">Pressione [N] para ocultar/abrir</span>
        </div>
        <div class="notes-content">"{s['script']}"</div>
        <div class="cue-box">🎭 <strong>Dica de Palco / Ação Prática:</strong> {s['stage_cue']}</div>
      </div>
    </div>
"""

html_template += """
    <!-- Barra de Controle Fixa -->
    <div class="controls-bar">
      <div style="display: flex; gap: 12px; align-items: center;">
        <button class="btn" onclick="prevSlide()" title="Slide Anterior (Seta Esquerda)">← Anterior</button>
        <button class="btn" onclick="nextSlide()" title="Próximo Slide (Seta Direita / Espaço)">Próximo →</button>
        <span class="slide-counter" id="slideIndicator">Slide 1 de 7</span>
      </div>

      <div style="display: flex; gap: 12px; align-items: center;">
        <button class="btn btn-primary" onclick="toggleNotes()" title="Exibir/Ocultar Roteiro Falado [N]">
          🎙 Roteiro Falado [N]
        </button>
        <button class="btn" onclick="toggleFullScreen()" title="Modo Tela Cheia [F]">
          ⛶ Tela Cheia [F]
        </button>
      </div>
    </div>
  </div>

  <script>
    let currentSlide = 1;
    const totalSlides = 7;
    let notesOpen = false;

    function showSlide(n) {
      if (n < 1) n = 1;
      if (n > totalSlides) n = totalSlides;
      currentSlide = n;

      for (let i = 1; i <= totalSlides; i++) {
        const el = document.getElementById(`slide-${i}`);
        if (el) {
          if (i === currentSlide) {
            el.classList.add('active');
            const drawer = document.getElementById(`notes-${i}`);
            if (drawer) {
              if (notesOpen) drawer.classList.add('open');
              else drawer.classList.remove('open');
            }
          } else {
            el.classList.remove('active');
          }
        }
      }

      document.getElementById('slideIndicator').innerText = `Slide ${currentSlide} de ${totalSlides}`;
    }

    function nextSlide() {
      if (currentSlide < totalSlides) {
        showSlide(currentSlide + 1);
      }
    }

    function prevSlide() {
      if (currentSlide > 1) {
        showSlide(currentSlide - 1);
      }
    }

    function toggleNotes() {
      notesOpen = !notesOpen;
      const currentDrawer = document.getElementById(`notes-${currentSlide}`);
      if (currentDrawer) {
        currentDrawer.classList.toggle('open', notesOpen);
      }
    }

    function toggleFullScreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
        }
      }
    }

    // Atalhos de teclado
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        nextSlide();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        prevSlide();
      } else if (e.key === 'n' || e.key === 'N') {
        toggleNotes();
      } else if (e.key === 'f' || e.key === 'F') {
        toggleFullScreen();
      } else if (e.key >= '1' && e.key <= '7') {
        showSlide(parseInt(e.key));
      }
    });
  </script>
</body>
</html>
"""

out_html1 = 'slides_apresentacao/apresentacao_autotutor_cp.html'
out_html2 = 'Apresentacao_AutoTutor_CP_Oficial.html'

with open(out_html1, 'w', encoding='utf-8') as f:
    f.write(html_template)

with open(out_html2, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"HTML oficial gerado com sucesso em:\n  1. {out_html1}\n  2. {out_html2}")
