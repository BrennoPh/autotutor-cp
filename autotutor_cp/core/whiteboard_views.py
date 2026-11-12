"""Interactive AI Whiteboard for Competitive Programming."""
import json
from html import escape
import streamlit as st
import streamlit.components.v1 as components
from core.ui import heading, html, badge, empty
from core.whiteboard_engine import (
    WHITEBOARD_PRESETS,
    generate_ai_whiteboard_diagram,
    analyze_board_structure,
    parse_graph_from_text,
    generate_algorithm_execution_tape
)

DEFAULT_DFS_CODE = [
    "def dfs(u):",
    "    visited[u] = True",
    "    in_stack[u] = True",
    "    for v in adj[u]:",
    "        if not visited[v]:",
    "            dfs(v)",
    "        elif in_stack[v]:",
    "            # Ciclo detectado",
    "            pass",
    "    in_stack[u] = False"
]

DEFAULT_BFS_CODE = [
    "def bfs(origem):",
    "    visited[origem] = True",
    "    queue.append(origem)",
    "    while queue:",
    "        u = queue.pop(0)",
    "        for v in adj[u]:",
    "            if not visited[v]:",
    "                visited[v] = True",
    "                queue.append(v)"
]


def whiteboard_canvas_html(initial_preset=None, height=640, simulation_steps=None, code_lines=None):
    """Gera o componente HTML5/JS do Quadro Branco com suporte a desenho e fita de execução."""
    preset_data = json.dumps(initial_preset or {}, ensure_ascii=False)
    steps_data = json.dumps(simulation_steps or [], ensure_ascii=False)
    lines_data = json.dumps(code_lines or DEFAULT_DFS_CODE, ensure_ascii=False)
    preset_title = initial_preset.get('title', '') if initial_preset else ''

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{preset_title}</title>
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
        body {{
          font-family: system-ui, -apple-system, sans-serif;
          background: #0f172a;
          color: #f8fafc;
          overflow: hidden;
          padding: 6px;
        }}
        .wb-container {{
          display: flex;
          flex-direction: column;
          height: {height - 12}px;
          background: #1e293b;
          border-radius: 12px;
          border: 1px solid #334155;
          box-shadow: 0 4px 20px rgba(0,0,0,0.3);
          overflow: hidden;
        }}
        .wb-toolbar {{
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          background: #0f172a;
          border-bottom: 1px solid #334155;
        }}
        .btn {{
          display: inline-flex;
          align-items: center;
          gap: 4px;
          background: #334155;
          color: #f1f5f9;
          border: 1px solid #475569;
          border-radius: 6px;
          padding: 5px 10px;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.15s ease;
        }}
        .btn:hover {{ background: #475569; }}
        .btn.active {{
          background: #4f46e5;
          border-color: #6366f1;
          color: #ffffff;
          box-shadow: 0 0 10px rgba(99,102,241,0.5);
        }}
        .btn-playback {{
          background: #1e293b;
          border-color: #6366f1;
          color: #a5b4fc;
          font-weight: 600;
        }}
        .btn-playback:hover {{ background: #4f46e5; color: #ffffff; }}
        .separator {{
          width: 1px;
          height: 22px;
          background: #334155;
          margin: 0 4px;
        }}
        .color-dot {{
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid transparent;
          cursor: pointer;
          transition: transform 0.1s;
        }}
        .color-dot:hover {{ transform: scale(1.15); }}
        .color-dot.active {{ border-color: #ffffff; transform: scale(1.15); }}
        .wb-main-split {{
          display: flex;
          flex: 1;
          height: calc(100% - 48px);
          overflow: hidden;
        }}
        .wb-canvas-wrap {{
          position: relative;
          flex: 1;
          background: #090d16;
          background-image: radial-gradient(#1e293b 1px, transparent 1px);
          background-size: 20px 20px;
          cursor: crosshair;
        }}
        canvas {{
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
        }}
        .status-badge {{
          position: absolute;
          bottom: 10px;
          left: 12px;
          background: rgba(15, 23, 42, 0.9);
          color: #94a3b8;
          padding: 4px 10px;
          border-radius: 6px;
          font-size: 11px;
          border: 1px solid #334155;
          pointer-events: none;
        }}
        input[type="text"] {{
          background: #1e293b;
          border: 1px solid #475569;
          color: #ffffff;
          padding: 4px 8px;
          border-radius: 5px;
          font-size: 12px;
          width: 60px;
        }}
        .wb-side-panel {{
          width: 320px;
          background: #0f172a;
          border-left: 1px solid #334155;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
          font-family: monospace;
          font-size: 11px;
          padding: 8px;
          gap: 8px;
        }}
        .code-box {{
          background: #090d16;
          border: 1px solid #1e293b;
          border-radius: 8px;
          padding: 6px;
          overflow-x: auto;
        }}
        .code-line {{
          padding: 1px 4px;
          border-radius: 4px;
          color: #94a3b8;
          white-space: pre;
        }}
        .code-line.active {{
          background: rgba(99, 102, 241, 0.25);
          color: #ffffff;
          border-left: 3px solid #6366f1;
          font-weight: bold;
        }}
        .stack-box {{
          background: #090d16;
          border: 1px solid #1e293b;
          border-radius: 8px;
          padding: 6px;
          min-height: 80px;
          max-height: 140px;
          overflow-y: auto;
          display: flex;
          flex-direction: column-reverse;
          gap: 3px;
        }}
        .stack-frame {{
          padding: 3px 6px;
          border-radius: 4px;
          background: rgba(245, 158, 11, 0.15);
          border: 1px solid rgba(245, 158, 11, 0.4);
          color: #fde68a;
          font-size: 11px;
        }}
        .log-box {{
          background: #090d16;
          border: 1px solid #1e293b;
          border-radius: 8px;
          padding: 8px;
          color: #cbd5e1;
          font-family: system-ui, sans-serif;
          font-size: 11px;
          line-height: 1.4;
        }}
      </style>
    </head>
    <body>
      <div class="wb-container">
        <!-- Barra de Ferramentas Principal -->
        <div class="wb-toolbar">
          <button class="btn active" id="btn-pen" title="Caneta livre">✏️ Caneta</button>
          <button class="btn" id="btn-node" title="Inserir nó">⭕ Nó</button>
          <input type="text" id="node-label" value="1" title="Rótulo">
          <button class="btn" id="btn-arrow" title="Seta">➡️ Seta</button>
          <button class="btn" id="btn-line" title="Aresta">➖ Aresta</button>
          <button class="btn" id="btn-rect" title="Caixa">🔲 Caixa</button>
          <button class="btn" id="btn-eraser" title="Borracha">🧹 Borracha</button>
          
          <div class="separator"></div>
          
          <div class="color-dot active" style="background:#6366f1" data-color="#6366f1" title="Índigo"></div>
          <div class="color-dot" style="background:#06b6d4" data-color="#06b6d4" title="Ciano"></div>
          <div class="color-dot" style="background:#10b981" data-color="#10b981" title="Verde"></div>
          <div class="color-dot" style="background:#f59e0b" data-color="#f59e0b" title="Âmbar"></div>
          <div class="color-dot" style="background:#ef4444" data-color="#ef4444" title="Vermelho"></div>

          <div class="separator"></div>

          <button class="btn" id="btn-undo" title="Desfazer">↶ Desfazer</button>
          <button class="btn" id="btn-clear" title="Limpar">🗑️ Limpar</button>
          <button class="btn" id="btn-download" style="background:#10b981;border-color:#059669">💾 Baixar PNG</button>

          <div class="separator"></div>

          <!-- Controles de Playback de Passos -->
          <button class="btn btn-playback" id="btn-reset" title="Reiniciar">🔄 Reset</button>
          <button class="btn btn-playback" id="btn-prev" title="Passo anterior">⏮ Passo</button>
          <button class="btn btn-playback" id="btn-play" title="Executar">▶ Play</button>
          <button class="btn btn-playback" id="btn-next" title="Próximo passo">Passo ⏭</button>
          <span id="step-label" style="font-size:11px;color:#a5b4fc;font-family:monospace">Passo: 0/0</span>
        </div>

        <div class="wb-main-split">
          <div class="wb-canvas-wrap" id="canvas-container">
            <canvas id="wb-canvas"></canvas>
            <div class="status-badge" id="status-text">{preset_title or 'Pronto · Modo: Caneta Livre'}</div>
          </div>

          <!-- Painel Lateral de Rastreamento de Algoritmo -->
          <div class="wb-side-panel" id="side-panel">
            <div style="font-weight:bold;color:#f8fafc;display:flex;justify-content:space-between">
              <span>Linhas do Código</span>
              <span id="active-line-badge" style="color:#6366f1">L--</span>
            </div>
            <div class="code-box" id="code-container"></div>

            <div style="font-weight:bold;color:#f8fafc;display:flex;justify-content:space-between;margin-top:4px">
              <span>Call Stack (Pilha)</span>
              <span id="stack-size-badge" style="color:#f59e0b">0 frames</span>
            </div>
            <div class="stack-box" id="stack-container">
              <div style="color:#64748b;text-align:center;margin:auto">Pilha vazia</div>
            </div>

            <div style="font-weight:bold;color:#f8fafc;margin-top:4px">Rastreamento da Ação</div>
            <div class="log-box" id="log-text">Pressione "Play" ou "Passo ⏭" para iniciar a execução do algoritmo no grafo.</div>
          </div>
        </div>
      </div>

      <script>
        const canvas = document.getElementById('wb-canvas');
        const container = document.getElementById('canvas-container');
        const ctx = canvas.getContext('2d');
        const statusText = document.getElementById('status-text');
        const nodeLabelInput = document.getElementById('node-label');
        const stepLabel = document.getElementById('step-label');
        const codeContainer = document.getElementById('code-container');
        const stackContainer = document.getElementById('stack-container');
        const logText = document.getElementById('log-text');
        const btnPlay = document.getElementById('btn-play');

        let currentTool = 'pen';
        let currentColor = '#6366f1';
        let currentWidth = 3;
        let isDrawing = false;
        let startX = 0, startY = 0;
        let shapes = [];
        let currentPath = [];

        // Dados de Simulação
        const simSteps = {steps_data};
        const codeLines = {lines_data};
        let currentStepIdx = 0;
        let isPlaying = false;
        let playInterval = null;

        // Renderiza código no painel
        function renderCodePanel(activeLine) {{
          codeContainer.innerHTML = '';
          codeLines.forEach((line, idx) => {{
            const div = document.createElement('div');
            div.className = 'code-line' + (idx + 1 === activeLine ? ' active' : '');
            div.textContent = (idx + 1).toString().padStart(2, ' ') + '  ' + line;
            codeContainer.appendChild(div);
          }});
          document.getElementById('active-line-badge').textContent = activeLine ? 'L' + activeLine : 'L--';
        }}
        renderCodePanel(1);

        function resizeCanvas() {{
          const rect = container.getBoundingClientRect();
          const dpr = window.devicePixelRatio || 1;
          canvas.width = rect.width * dpr;
          canvas.height = rect.height * dpr;
          ctx.scale(dpr, dpr);
          redraw();
        }}
        window.addEventListener('resize', resizeCanvas);
        setTimeout(resizeCanvas, 50);

        // Ferramentas
        const toolBtns = {{
          pen: document.getElementById('btn-pen'),
          node: document.getElementById('btn-node'),
          arrow: document.getElementById('btn-arrow'),
          line: document.getElementById('btn-line'),
          rect: document.getElementById('btn-rect'),
          eraser: document.getElementById('btn-eraser')
        }};

        Object.keys(toolBtns).forEach(t => {{
          toolBtns[t].addEventListener('click', () => {{
            Object.values(toolBtns).forEach(b => b.classList.remove('active'));
            toolBtns[t].classList.add('active');
            currentTool = t;
            statusText.textContent = 'Modo: ' + t;
          }});
        }});

        // Cores
        document.querySelectorAll('.color-dot').forEach(dot => {{
          dot.addEventListener('click', () => {{
            document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
            dot.classList.add('active');
            currentColor = dot.getAttribute('data-color');
          }});
        }});

        function getPos(e) {{
          const rect = canvas.getBoundingClientRect();
          const clientX = e.touches ? e.touches[0].clientX : e.clientX;
          const clientY = e.touches ? e.touches[0].clientY : e.clientY;
          return {{ x: clientX - rect.left, y: clientY - rect.top }};
        }}

        function redraw() {{
          const rect = container.getBoundingClientRect();
          ctx.clearRect(0, 0, rect.width, rect.height);

          const step = simSteps[currentStepIdx] || null;
          const nodeStates = step ? step.node_states : {{}};
          const edgeStates = step ? step.edge_states : {{}};

          shapes.forEach(shape => {{
            ctx.save();
            if (shape.type === 'path') {{
              ctx.strokeStyle = shape.color;
              ctx.lineWidth = shape.width;
              ctx.lineCap = 'round';
              ctx.beginPath();
              shape.points.forEach((pt, i) => {{
                if (i === 0) ctx.moveTo(pt.x, pt.y);
                else ctx.lineTo(pt.x, pt.y);
              }});
              ctx.stroke();
            }} else if (shape.type === 'node') {{
              const st = nodeStates[shape.label] || 'unvisited';
              let fill = '#1e1b4b';
              let stroke = shape.color;
              if (st === 'visiting') {{
                fill = '#f59e0b';
                stroke = '#fbbf24';
              }} else if (st === 'visited') {{
                fill = '#10b981';
                stroke = '#34d399';
              }}

              ctx.fillStyle = fill;
              ctx.strokeStyle = stroke;
              ctx.lineWidth = 3;
              ctx.beginPath();
              ctx.arc(shape.x, shape.y, 22, 0, Math.PI * 2);
              ctx.fill();
              ctx.stroke();

              ctx.fillStyle = '#ffffff';
              ctx.font = 'bold 13px system-ui, sans-serif';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(shape.label, shape.x, shape.y);
            }} else if (shape.type === 'arrow' || shape.type === 'line') {{
              const edgeKey = shape.fromId && shape.toId ? shape.fromId + '-' + shape.toId : '';
              const eSt = edgeStates[edgeKey] || 'normal';

              ctx.strokeStyle = eSt === 'back_edge' ? '#ef4444' : (eSt === 'traversed' ? '#38bdf8' : shape.color);
              ctx.lineWidth = eSt === 'traversed' ? 4 : 2.5;
              if (eSt === 'back_edge') ctx.setLineDash([5, 3]);

              ctx.beginPath();
              ctx.moveTo(shape.x1, shape.y1);
              ctx.lineTo(shape.x2, shape.y2);
              ctx.stroke();

              if (shape.type === 'arrow') {{
                const angle = Math.atan2(shape.y2 - shape.y1, shape.x2 - shape.x1);
                const headLen = 13;
                ctx.fillStyle = ctx.strokeStyle;
                ctx.beginPath();
                ctx.moveTo(shape.x2, shape.y2);
                ctx.lineTo(shape.x2 - headLen * Math.cos(angle - Math.PI / 6), shape.y2 - headLen * Math.sin(angle - Math.PI / 6));
                ctx.lineTo(shape.x2 - headLen * Math.cos(angle + Math.PI / 6), shape.y2 - headLen * Math.sin(angle + Math.PI / 6));
                ctx.closePath();
                ctx.fill();
              }}
            }} else if (shape.type === 'rect') {{
              ctx.strokeStyle = shape.color;
              ctx.lineWidth = 2;
              ctx.fillStyle = 'rgba(79, 70, 229, 0.15)';
              ctx.fillRect(shape.x, shape.y, shape.w, shape.h);
              ctx.strokeRect(shape.x, shape.y, shape.w, shape.h);
            }}
            ctx.restore();
          }});
        }}

        // Eventos de Desenho
        canvas.addEventListener('mousedown', startDraw);
        canvas.addEventListener('mousemove', draw);
        window.addEventListener('mouseup', endDraw);
        canvas.addEventListener('touchstart', (e) => {{ e.preventDefault(); startDraw(e); }}, {{passive: false}});
        canvas.addEventListener('touchmove', (e) => {{ e.preventDefault(); draw(e); }}, {{passive: false}});
        window.addEventListener('touchend', endDraw);

        function startDraw(e) {{
          isDrawing = true;
          const pos = getPos(e);
          startX = pos.x;
          startY = pos.y;

          if (currentTool === 'pen' || currentTool === 'eraser') {{
            currentPath = [pos];
          }} else if (currentTool === 'node') {{
            const lbl = nodeLabelInput.value || '1';
            shapes.push({{ type: 'node', x: pos.x, y: pos.y, label: lbl, color: currentColor }});
            if (!isNaN(parseInt(lbl))) nodeLabelInput.value = parseInt(lbl) + 1;
            redraw();
            isDrawing = false;
          }}
        }}

        function draw(e) {{
          if (!isDrawing) return;
          const pos = getPos(e);

          if (currentTool === 'pen' || currentTool === 'eraser') {{
            currentPath.push(pos);
            ctx.save();
            ctx.strokeStyle = currentTool === 'eraser' ? '#090d16' : currentColor;
            ctx.lineWidth = currentTool === 'eraser' ? 24 : currentWidth;
            ctx.lineCap = 'round';
            ctx.beginPath();
            if (currentPath.length > 1) {{
              const p1 = currentPath[currentPath.length - 2];
              const p2 = currentPath[currentPath.length - 1];
              ctx.moveTo(p1.x, p1.y);
              ctx.lineTo(p2.x, p2.y);
              ctx.stroke();
            }}
            ctx.restore();
          }} else {{
            redraw();
            ctx.save();
            ctx.strokeStyle = currentColor;
            ctx.lineWidth = 2;
            if (currentTool === 'arrow' || currentTool === 'line') {{
              ctx.beginPath();
              ctx.moveTo(startX, startY);
              ctx.lineTo(pos.x, pos.y);
              ctx.stroke();
            }} else if (currentTool === 'rect') {{
              ctx.strokeRect(startX, startY, pos.x - startX, pos.y - startY);
            }}
            ctx.restore();
          }}
        }}

        function endDraw(e) {{
          if (!isDrawing) return;
          isDrawing = false;
          const pos = e.changedTouches ? getPos(e.changedTouches[0]) : (e.clientX ? getPos(e) : {{x: startX, y: startY}});

          if (currentTool === 'pen' || currentTool === 'eraser') {{
            if (currentPath.length > 0) {{
              shapes.push({{
                type: 'path',
                points: currentPath,
                color: currentTool === 'eraser' ? '#090d16' : currentColor,
                width: currentTool === 'eraser' ? 24 : currentWidth
              }});
            }}
            currentPath = [];
          }} else if (currentTool === 'arrow' || currentTool === 'line') {{
            if (Math.hypot(pos.x - startX, pos.y - startY) > 5) {{
              shapes.push({{ type: currentTool, x1: startX, y1: startY, x2: pos.x, y2: pos.y, color: currentColor }});
            }}
          }} else if (currentTool === 'rect') {{
            shapes.push({{
              type: 'rect',
              x: Math.min(startX, pos.x),
              y: Math.min(startY, pos.y),
              w: Math.abs(pos.x - startX),
              h: Math.abs(pos.y - startY),
              color: currentColor
            }});
          }}
          redraw();
        }}

        // Ações da Toolbar
        document.getElementById('btn-undo').addEventListener('click', () => {{
          if (shapes.length > 0) {{
            shapes.pop();
            redraw();
            statusText.textContent = 'Ação desfeita';
          }} else {{
            statusText.textContent = 'Nada para desfazer';
          }}
        }});

        document.getElementById('btn-clear').addEventListener('click', () => {{
          shapes = [];
          redraw();
          statusText.textContent = 'Quadro limpo com sucesso!';
        }});

        document.getElementById('btn-download').addEventListener('click', () => {{
          const link = document.createElement('a');
          link.download = 'autotutor-quadro-branco.png';
          link.href = canvas.toDataURL('image/png');
          link.click();
          statusText.textContent = 'Download do PNG iniciado!';
        }});

        // Carrega Preset ou Nós Iniciais
        const initPreset = {preset_data};
        if (initPreset && initPreset.nodes) {{
          initPreset.nodes.forEach(n => {{
            shapes.push({{ type: 'node', x: n.x, y: n.y, label: n.label, color: n.color || '#4f46e5' }});
          }});
          if (initPreset.edges) {{
            initPreset.edges.forEach(ed => {{
              const nFrom = initPreset.nodes.find(n => n.id === ed.from);
              const nTo = initPreset.nodes.find(n => n.id === ed.to);
              if (nFrom && nTo) {{
                shapes.push({{
                  type: ed.directed ? 'arrow' : 'line',
                  fromId: ed.from,
                  toId: ed.to,
                  x1: nFrom.x, y1: nFrom.y,
                  x2: nTo.x, y2: nTo.y,
                  color: ed.color || '#6366f1'
                }});
              }}
            }});
          }}
          redraw();
        }}

        // Lógica de Playback de Passos
        function updateStepView() {{
          if (simSteps.length === 0) {{
            stepLabel.textContent = 'Passo: 0/0';
            return;
          }}
          stepLabel.textContent = `Passo: ${{currentStepIdx + 1}}/${{simSteps.length}}`;
          const step = simSteps[currentStepIdx];
          if (!step) return;

          renderCodePanel(step.line);

          // Atualiza Pilha
          stackContainer.innerHTML = '';
          const stack = step.call_stack || [];
          if (stack.length === 0) {{
            stackContainer.innerHTML = '<div style="color:#64748b;text-align:center;margin:auto">Pilha vazia</div>';
          }} else {{
            stack.forEach(frame => {{
              const fDiv = document.createElement('div');
              fDiv.className = 'stack-frame';
              fDiv.textContent = frame;
              stackContainer.appendChild(fDiv);
            }});
          }}
          document.getElementById('stack-size-badge').textContent = `${{stack.length}} frames`;
          logText.textContent = step.log || '';
          redraw();
        }}

        document.getElementById('btn-next').addEventListener('click', () => {{
          if (currentStepIdx < simSteps.length - 1) {{
            currentStepIdx++;
            updateStepView();
          }}
        }});

        document.getElementById('btn-prev').addEventListener('click', () => {{
          if (currentStepIdx > 0) {{
            currentStepIdx--;
            updateStepView();
          }}
        }});

        document.getElementById('btn-reset').addEventListener('click', () => {{
          currentStepIdx = 0;
          if (isPlaying) togglePlay();
          updateStepView();
        }});

        function togglePlay() {{
          isPlaying = !isPlaying;
          if (isPlaying) {{
            btnPlay.textContent = '⏸ Pause';
            btnPlay.style.background = '#f59e0b';
            playInterval = setInterval(() => {{
              if (currentStepIdx >= simSteps.length - 1) {{
                togglePlay();
              }} else {{
                currentStepIdx++;
                updateStepView();
              }}
            }}, 650);
          }} else {{
            btnPlay.textContent = '▶ Play';
            btnPlay.style.background = '#1e293b';
            if (playInterval) clearInterval(playInterval);
          }}
        }}
        btnPlay.addEventListener('click', togglePlay);

        updateStepView();
      </script>
    </body>
    </html>
    """


def render_whiteboard(store, profile_id, go, llm, user):
    """Renderiza o Quadro Branco Inteligente com editor de código customizado e simulação passo a passo."""
    heading(
        'LOUSA INTELIGENTE & SIMULADOR DE CÓDIGO',
        'Quadro Branco & Laboratório de Algoritmos',
        'Rascunhe livremente, digite seu próprio algoritmo, defina grafos e veja a execução animada passo a passo na memória.'
    )

    wb_tab1, wb_tab2, wb_tab3, wb_tab4 = st.tabs([
        '⚡ Executar Meu Código no Grafo',
        '🎨 Desenho Livre & Modelagem',
        '🤖 Gerador de Grafos (IA)',
        '📚 Meus Quadros Salvos'
    ])

    with wb_tab1:
        st.markdown('#### Editor de Código do Aluno & Simulação de Passos')
        st.caption('Digite seu próprio algoritmo em Python/C++, informe a lista de arestas e visualize a animação da execução com Call Stack em tempo real.')

        ctrl_col1, ctrl_col2 = st.columns([1, 1], gap='medium')

        with ctrl_col1:
            code_preset = st.selectbox(
                'Carregar Template de Código:',
                [
                    'DFS Recursiva Clássica',
                    'DFS com Detecção de Ciclo (Back-Edge)',
                    'BFS com Fila FIFO (Menor Caminho)'
                ],
                key='wb_code_template'
            )

            default_code = "\n".join(DEFAULT_DFS_CODE)
            if 'BFS' in code_preset:
                default_code = "\n".join(DEFAULT_BFS_CODE)
            elif 'Ciclo' in code_preset:
                default_code = "\n".join(DEFAULT_DFS_CODE)

            user_algorithm_code = st.text_area(
                'Seu Código do Algoritmo:',
                value=st.session_state.get('wb_custom_code', default_code),
                height=180,
                key='wb_user_code_input'
            )

        with ctrl_col2:
            st.markdown('**Definição do Grafo (Arestas):**')
            st.caption('Formato: digite pares de vértices por linha (ex.: `1 2` ou `1 -> 2`).')

            quick_preset = st.selectbox(
                'Preencher com Grafo Clássico:',
                ['-- Personalizado / Manual --', 'DAG (5 nós)', 'Ciclo com Back-Edge', 'Árvore Binária', 'Camadas BFS', 'Grafo Bipartido'],
                key='wb_quick_graph_preset'
            )

            preset_edges_text = "1 2\n1 3\n2 4\n3 4"
            if quick_preset == 'DAG (5 nós)':
                preset_edges_text = "1 2\n1 3\n2 4\n3 4\n4 5"
            elif quick_preset == 'Ciclo com Back-Edge':
                preset_edges_text = "1 2\n2 3\n3 4\n4 1"
            elif quick_preset == 'Árvore Binária':
                preset_edges_text = "1 2\n1 3\n2 4\n2 5\n3 6\n3 7"
            elif quick_preset == 'Camadas BFS':
                preset_edges_text = "S A\nS B\nA C\nB D"
            elif quick_preset == 'Grafo Bipartido':
                preset_edges_text = "U1 V1\nU1 V2\nU2 V2\nU3 V3"

            user_edges_text = st.text_area(
                'Lista de Arestas do Grafo:',
                value=st.session_state.get('wb_edges_input', preset_edges_text),
                height=110,
                key='wb_edges_input_area'
            )

            parsed_graph = parse_graph_from_text(user_edges_text)
            avail_nodes = [n['id'] for n in parsed_graph['nodes']]

            start_col, run_col = st.columns([1, 1.5])
            with start_col:
                start_vertex = st.selectbox(
                    'Vértice Inicial:',
                    avail_nodes if avail_nodes else ['1'],
                    key='wb_start_vertex'
                )
            with run_col:
                st.write('')
                st.write('')
                if st.button('▶ Executar Meu Algoritmo', type='primary', use_container_width=True, key='btn_run_algo'):
                    code_lines = [l for l in user_algorithm_code.splitlines() if l.strip()]
                    tape = generate_algorithm_execution_tape(
                        user_algorithm_code,
                        parsed_graph['nodes'],
                        parsed_graph['edges'],
                        start_node=start_vertex,
                        max_steps=500
                    )
                    st.session_state.wb_simulation_steps = tape
                    st.session_state.wb_simulation_lines = code_lines
                    st.session_state.wb_active_graph = parsed_graph
                    st.toast(f'Simulação pronta! {len(tape)} passos gravados. Use os botões Play/Passo no quadro.')
                    st.rerun()

        # Canvas com Fita de Execução Ativa
        active_graph = st.session_state.get('wb_active_graph', parsed_graph)
        active_steps = st.session_state.get('wb_simulation_steps', [])
        active_lines = st.session_state.get('wb_simulation_lines', [l for l in user_algorithm_code.splitlines() if l.strip()])

        st.markdown('---')
        st.caption(f'Grafo Atual: **{len(active_graph["nodes"])} vértices** e **{len(active_graph["edges"])} arestas**. Simulação ativa com **{len(active_steps)} passos**.')

        canvas_interactive_code = whiteboard_canvas_html(
            initial_preset=active_graph,
            height=600,
            simulation_steps=active_steps,
            code_lines=active_lines
        )
        components.html(canvas_interactive_code, height=610, scrolling=False)

    with wb_tab2:
        st.markdown('#### Lousa de Desenho Livre e Rascunho')
        st.caption('Carimbe vértices, trace arestas e rascunhe livremente com o mouse ou caneta.')

        # Presets rápidos
        preset_cols = st.columns([1, 1, 1, 1, 1, 2])
        if preset_cols[0].button('DAG / TopoSort', key='btn_preset_dag', use_container_width=True):
            st.session_state.active_preset = 'dag'
            st.toast('Preset DAG carregado!')
            st.rerun()
        if preset_cols[1].button('Ciclo / Back Edge', key='btn_preset_cycle', use_container_width=True):
            st.session_state.active_preset = 'cycle'
            st.toast('Preset Ciclo carregado!')
            st.rerun()
        if preset_cols[2].button('Árvore Binária', key='btn_preset_tree', use_container_width=True):
            st.session_state.active_preset = 'tree'
            st.toast('Preset Árvore carregado!')
            st.rerun()
        if preset_cols[3].button('Camadas BFS', key='btn_preset_bfs', use_container_width=True):
            st.session_state.active_preset = 'bfs_layers'
            st.toast('Preset Camadas BFS carregado!')
            st.rerun()
        if preset_cols[4].button('Grafo Bipartido', key='btn_preset_bipartite', use_container_width=True):
            st.session_state.active_preset = 'bipartite'
            st.toast('Preset Bipartido carregado!')
            st.rerun()
        if preset_cols[5].button('Novo Quadro em Branco', key='btn_preset_clean', use_container_width=True):
            st.session_state.active_preset = None
            st.toast('Quadro limpo!')
            st.rerun()

        active_preset_name = st.session_state.get('active_preset')
        preset_obj = WHITEBOARD_PRESETS.get(active_preset_name) if active_preset_name else None

        if preset_obj:
            with st.expander(f"💡 Sobre esta estrutura: {preset_obj['title']}", expanded=True):
                st.write(preset_obj['description'])

        free_canvas_code = whiteboard_canvas_html(initial_preset=preset_obj, height=580)
        components.html(free_canvas_code, height=590, scrolling=False)

        # Análise do Tutor
        st.divider()
        st.markdown('### 🔍 Consultar o Tutor sobre sua Modelagem')
        with st.form('analyze_board_form'):
            user_notes = st.text_area(
                'Descreva seu raciocínio ou as dúvidas da sua modelagem',
                placeholder='Ex.: "Desenhei um grafo com 4 nós onde o vértice 4 volta para o 1. Quero saber se isso invalida o Topological Sort e qual o impacto na complexidade."',
                height=90
            )
            submit_analysis = st.form_submit_button('Pedir Análise da IA sobre a Estrutura →')

        if submit_analysis:
            if not user_notes.strip():
                st.warning('Descreva o que você desenhou para que o tutor possa analisar as propriedades.')
            else:
                with st.spinner('O tutor está analisando a modelagem…'):
                    analysis_res = analyze_board_structure(llm, user_notes)
                    st.session_state.last_board_analysis = analysis_res
                    st.toast('Análise do tutor concluída!')

        if st.session_state.get('last_board_analysis'):
            with st.container(border=True):
                st.markdown('#### 📋 Parecer Pedagógico do Tutor')
                st.markdown(st.session_state.last_board_analysis)

        # Salvar na biblioteca
        save_col1, save_col2 = st.columns([2, 1])
        with save_col1:
            board_title = st.text_input(
                'Título para salvar este quadro na sua biblioteca',
                value=f"Quadro de Estudo: {preset_obj['title'] if preset_obj else 'Modelagem Livre'}",
                key='save_board_title'
            )
        with save_col2:
            st.write('')
            st.write('')
            if st.button('Salvar Quadro na Biblioteca', type='primary', key='btn_save_board', use_container_width=True):
                store.add_artifact(
                    profile_id,
                    'whiteboard',
                    board_title,
                    {
                        'preset': active_preset_name,
                        'analysis': st.session_state.get('last_board_analysis', ''),
                        'source': f"{llm.provider} · {llm.model}"
                    }
                )
                st.toast('Quadro salvo com sucesso na biblioteca!')
                st.success('Quadro salvo com sucesso na sua biblioteca!')

    with wb_tab3:
        st.markdown('#### Gerador de Exemplos e Diagramas por IA')
        st.caption('Peça à IA para gerar instâncias conceituais para desenhar ou projetar no quadro.')

        example_presets = [
            'Desenhe um DAG com 5 nós e mostre a ordem de finalização da DFS',
            'Gere um grafo com 6 nós e destaque uma Back Edge que forma um ciclo',
            'Crie uma representação visual de um Labirinto 4x4 para busca com BFS',
            'Desenhe uma árvore binária de busca e mostre o caminho da raiz até a chave 42',
            'Gere uma tabela 3x4 de Programação Dinâmica com setas de dependência de estados'
        ]

        preset_click = st.selectbox('Exemplos rápidos de maratona:', ['-- Escolha uma sugestão ou digite abaixo --'] + example_presets)
        custom_prompt = st.text_area(
            'Ou digite qualquer instrução visual para a IA projetar na lousa:',
            value=preset_click if preset_click != '-- Escolha uma sugestão ou digite abaixo --' else '',
            height=90
        )

        if st.button('Gerar Diagrama para o Quadro →', type='primary', key='btn_gen_ai_board'):
            if not custom_prompt.strip():
                st.warning('Digite uma instrução ou escolha um dos exemplos rápidos.')
            else:
                with st.spinner('A IA está construindo o diagrama estruturado…'):
                    res = generate_ai_whiteboard_diagram(llm, custom_prompt)
                    st.session_state.last_generated_diagram = res
                    st.toast('Diagrama gerado com sucesso!')

        gen = st.session_state.get('last_generated_diagram')
        if gen:
            with st.container(border=True):
                st.markdown('### 📊 Visualização Gerada para o Quadro')
                st.markdown(gen['text'])
                if gen.get('mermaid'):
                    with st.expander('Código Mermaid do Diagrama', expanded=False):
                        st.code(gen['mermaid'], language='mermaid')

    with wb_tab4:
        st.markdown('#### Meus Quadros de Modelagem Salvos')
        boards = store.artifacts(profile_id, kind='whiteboard', limit=50)
        if not boards:
            empty('Nenhum quadro salvo ainda', 'Desenhe ou simule algoritmos no Quadro Branco e salve-os para consultá-los a qualquer momento.')
        else:
            for b in boards:
                with st.container(border=True):
                    b_col1, b_col2 = st.columns([3, 1])
                    payload = b.get('payload', {})
                    with b_col1:
                        st.markdown(f"### {b['title']}")
                        st.caption(f"Salvo em {b.get('created_at', 'data recente')} · Fonte: {payload.get('source', 'Local')}")
                    with b_col2:
                        if st.button('Carregar no Laboratório →', key=f"load_saved_{b['id']}", use_container_width=True):
                            if payload.get('preset'):
                                st.session_state.active_preset = payload['preset']
                            st.toast(f"Quadro '{b['title']}' carregado no laboratório!")
                            st.rerun()

                    if payload.get('analysis'):
                        with st.expander('Ver análise salva do tutor'):
                            st.write(payload['analysis'])
