import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Paleta de Cores
    COLOR_BG = RGBColor(15, 23, 42)        # Slate 900
    COLOR_CARD = RGBColor(30, 41, 59)      # Slate 800
    COLOR_BORDER = RGBColor(51, 65, 85)    # Slate 700
    COLOR_WHITE = RGBColor(248, 250, 252)  # Slate 50
    COLOR_MUTED = RGBColor(148, 163, 184)  # Slate 400
    COLOR_CYAN = RGBColor(56, 189, 248)    # Sky 400
    COLOR_EMERALD = RGBColor(52, 211, 153) # Emerald 400
    COLOR_ROSE = RGBColor(251, 113, 133)   # Rose 400
    COLOR_AMBER = RGBColor(251, 191, 36)   # Amber 400

    slides_data = [
        {
            "num": 1,
            "time": "00:00 - 00:40 (40s)",
            "category": "O GANCHO & O PROBLEMA",
            "title": "O Abismo na Programação Competitiva: Por que Alunos Travam?",
            "subtitle": "Juízes punem sem explicar a causa raiz; IAs genéricas entregam o código pronto e atrofiam o aprendizado.",
            "image": "slides_apresentacao/assets/diagrama_slide1_problema.png",
            "script": """[00:00 - 00:40 | O PROBLEMA]
\"Boa tarde à banca avaliadora. Todo estudante de Ciência da Computação conhece essa dor: você compreende a teoria em aula, abre o juiz online e recebe um seco: 'Wrong Answer no Teste 4'. O juiz diz O QUE está errado, mas nunca o PORQUÊ.

Do outro lado, quando o aluno pede ajuda a uma IA genérica, ela cospe o código pronto. Isso destrói o processo pedagógico: o aluno copia, passa o teste, mas não desenvolve musculatura algorítmica.

Foi para resolver esse abismo que criamos o AutoTutor CP: uma plataforma que integra juiz de execução real em C++ com tutoria socrática guiada por fundamentos científicos da literatura.\"

AÇÃO DE PALCO: Olhar seguro para a banca, braços abertos ao falar do 'abismo', apontar para a comparação entre o juiz punitivo e a cola da IA genérica.""",
            "key_points": [
                "• Juiz Tradicional: Veredito seco (Wrong Answer / TLE) sem rastreabilidade da causa cognitiva.",
                "• IA Genérica (ChatGPT): Resposta pronta que gera ilusão de competência e atrofia o raciocínio.",
                "• A Solução AutoTutor CP: Diálogo socrático com pre-flight check e sandbox local."
            ]
        },
        {
            "num": 2,
            "time": "00:40 - 01:20 (40s)",
            "category": "FUNDAMENTAÇÃO CIENTÍFICA",
            "title": "A Tríade de Pesquisa: Ciência por Trás da Solução",
            "subtitle": "Três pilares da literatura acadêmica que fundamentam geração, recuperação e tutoria sem alucinação.",
            "image": "slides_apresentacao/assets/diagrama_slide2_pilares.png",
            "script": """[00:40 - 01:20 | FUNDAMENTOS CIENTÍFICOS]
\"O AutoTutor CP não é um simples invólucro de API comercial. Ele é fundamentado em três publicações de ponta da literatura:

Primeiro, AutoCode (ICLR 2026): os problemas inéditos são gerados em par com um oráculo C++ e suite de testes. O sistema compila e valida cruzadamente antes de exibir ao aluno, garantindo zero problemas inválidos.

Segundo, OI-Assistant (IOI 2025): nosso RAG recupera exercícios e analogias pela essência matemática e invariantes do algoritmo — como subestrutura ótima ou monotonicidade —, e não por palavras soltas.

E terceiro, CODIGEN (IEEE VL/HCC 2025): o tutor opera sob restrições cognitivas estritas. Ele diagnostica a quebra de invariantes e oferece uma escada gradual de dicas, impedindo que o aluno veja a solução antes de exercitar o raciocínio.\"

AÇÃO DE PALCO: Postura acadêmica firme. Aponte para cada um dos 3 pilares com clareza mostrando o rigor metodológico.""",
            "key_points": [
                "• AutoCode (ICLR 2026): Geração de problemas validada por oráculo duplo e testes compilados.",
                "• OI-Assistant (IOI 2025): RAG estrutural por invariantes matemáticos e complexidade assintótica.",
                "• CODIGEN (IEEE VL/HCC 2025): Escada de dicas graduais (Conceitual -> Estrutural -> Assintótica)."
            ]
        },
        {
            "num": 3,
            "time": "01:20 - 02:10 (50s)",
            "category": "DEMONSTRAÇÃO DE PRODUTO 1",
            "title": "O Workspace de Resolução & O Juiz Online C++",
            "subtitle": "Ambiente integrado de prática com compilação G++17 isolada em sandbox e tutoria socrática em tempo real.",
            "image": "slides_apresentacao/assets/arena_problem.png",
            "script": """[01:20 - 02:10 | WORKSPACE E JUIZ]
\"Esta é a tela de resolução do estudante. Do lado esquerdo, temos a especificação formal do problema com restrições assintóticas de tempo e memória. No centro, o editor Monaco rodando C++17.

Ao submeter o código, a execução não roda em ambiente desprotegido: ela é despachada para o nosso juiz isolado 'isolated_judge.py', compilada via G++ com limites rígidos POSIX de 256MB e contenção por Bubblewrap.

Observem o console: o juiz detectou Time Limit Exceeded. Em vez de deixar o aluno desamparado, o tutor socrático analisa o código submetido e intervém: 'Percebeu que para cada elemento você percorre todo o vetor novamente? Como manter essa busca em O(1) usando um acumulador de prefixo?'

A IA não dá o código pronto. Ela guia o aluno exatamente para a quebra de complexidade.\"

AÇÃO DE PALCO: Aponte para o editor Monaco no centro, depois para o console do juiz embaixo, e finalize destacando o painel lateral do tutor socrático.""",
            "key_points": [
                "• Editor Monaco C++17 com autocompletion, realce sintático e painel split-view.",
                "• Sandbox POSIX: Limites rígidos de 256MB (RLIMIT_AS) e proteção Bubblewrap contra fork/memory bombs.",
                "• Veredito em Tempo Real: Detecção exata de AC, WA, TLE, CE e RE com diagnóstico do erro.",
                "• AI Tutor Contextual: Recebe código + veredito e faz perguntas reflexivas sem entregar a resposta."
            ]
        },
        {
            "num": 4,
            "time": "02:10 - 03:00 (50s)",
            "category": "DEMONSTRAÇÃO DE PRODUTO 2",
            "title": "O Quadro Branco Interativo de Grafos (Whiteboard)",
            "subtitle": "Conexão intuitiva de nós topológicos sincronizada com código C++ e animação da pilha de execução viva.",
            "image": "slides_apresentacao/assets/whiteboard_full.png",
            "script": """[02:10 - 03:00 | QUADRO BRANCO DE GRAFOS]
\"Um dos maiores gargalos cognitivos em computação é a abstração espacial de ponteiros e grafos. Por isso desenvolvemos o nosso Quadro Branco Interativo.

Aqui o aluno constrói o grafo livremente ou importa a topologia do problema. Ele adiciona vértices, conecta arestas direcionadas ou ponderadas e acopla a implementação do algoritmo de busca — como DFS, BFS ou Dijkstra.

Ao acionar a execução passo a passo, o motor sincroniza o runtime C++ com a malha visual: os nós mudam de cor conforme o ciclo de vida da busca, e a pilha de memória de recursão é desenhada ao vivo ao lado.

O estudante enxerga visualmente o exato momento em que o backtracking ocorre, desmistificando o comportamento da pilha de execução do sistema.\"

AÇÃO DE PALCO: Destaque o grafo visual com os nós interativos e a pilha de recursão viva ao lado, enfatizando a redução da carga cognitiva de abstração espacial.""",
            "key_points": [
                "• Canvas Topológico Interativo: Adição e conexão livre de nós e arestas direcionadas/ponderadas.",
                "• Sincronização Código-Visual: Algoritmos C++ acoplados à topologia do grafo.",
                "• Rastreamento de Estados: Vértices mudam de cor (Descoberto -> Em Processamento -> Finalizado).",
                "• Pilha de Execução Viva: Renderização em tempo real do empilhamento e backtracking da memória."
            ]
        },
        {
            "num": 5,
            "time": "03:00 - 03:50 (50s)",
            "category": "DEMONSTRAÇÃO DE PRODUTO 3",
            "title": "Diagnóstico Adaptativo & Calendário Diário Espaçado",
            "subtitle": "Micro-quiz calibrado que mapeia lacunas conceituais e gera automaticamente um cronograma diário com repetição espaçada.",
            "image": "slides_apresentacao/assets/composite_slide5_onboarding_calendar.png",
            "script": """[03:00 - 03:50 | ONBOARDING E CALENDÁRIO]
\"Nenhum estudante começa do mesmo patamar. Por isso, eliminamos trilhas estáticas lineares que tratam todos como iguais.

Na primeira tela à esquerda, no Onboarding, o estudante responde a um micro-quiz diagnóstico calibrado. Nosso backend processa o padrão de respostas e mapeia com precisão matemática os tópicos dominados e as lacunas conceituais — por exemplo, forte em recursão, mas com lacuna em programação dinâmica.

A partir desse perfil, o motor algorítmico gera instantaneamente o Calendário Adaptativo à direita.

Reparem no equilíbrio: tarefas teóricas no Study Reader intercaladas com desafios práticos na Arena, respeitando o ritmo e a rotina do aluno com repetição espaçada. Toda a jornada é orientada por dados pedagógicos reais.\"

AÇÃO DE PALCO: Aponte primeiro para a esquerda mostrando a detecção de lacunas conceituais, depois para a direita mostrando o calendário gerado sob medida.""",
            "key_points": [
                "• Micro-Quiz Diagnóstico (/onboarding): Avaliação rápida de DP, Grafos, Busca Binária e Prefix Sum.",
                "• Mapeamento de Lacunas: Identifica o ponto cego conceitual do aluno antes de sugerir desafios.",
                "• Calendário Adaptativo (/calendar): Cronograma diário com estudo teórico e prática na Arena.",
                "• Repetição Espaçada: Revisões programadas para retenção de memória de longo prazo."
            ]
        },
        {
            "num": 6,
            "time": "03:50 - 04:30 (40s)",
            "category": "ARQUITETURA & RESILIÊNCIA",
            "title": "Engenharia de Software de Alta Resiliência",
            "subtitle": "Next.js 14 moderno, backend assíncrono, isolamento sandbox Bubblewrap e suporte a LLM 100% offline.",
            "image": "slides_apresentacao/assets/diagrama_slide6_arquitetura.png",
            "script": """[03:50 - 04:30 | ARQUITETURA E RESILIÊNCIA]
\"Para garantir confiabilidade de produção, nossa arquitetura foi projetada em camadas estritamente desacopladas:

O frontend roda em Next.js 14 App Router com tipagem estrita TypeScript e design ergonômico sóbrio. O backend é impulsionado por FastAPI assíncrono e persistência transacional em SQLite.

A execução de código utiliza sandbox Bubblewrap com limites POSIX, contendo com sucesso vazamentos de memória e fork-bombs.

E um detalhe crucial para ambientes acadêmicos: nosso motor de IA é híbrido. Ele pode operar com Google Gemini ou OpenAI em nuvem, mas funciona 100% OFFLINE através do Ollama local, sem depender de internet.

Toda essa estrutura foi homologada com 365 testes no Pytest e auditada com um milhão de jornadas simuladas.\"

AÇÃO DE PALCO: Tom de voz firme e técnico. Destaque os números de homologação e a capacidade de operar 100% offline sem internet.""",
            "key_points": [
                "• Frontend: Next.js 14 App Router, TypeScript, Monaco Editor, Cytoscape, UI Linear Dark.",
                "• Backend: FastAPI assíncrono, autenticação Bearer Token, persistência ACID em SQLite.",
                "• Sandbox POSIX: Limite de 256MB e Bubblewrap contendo memory bombs e chamadas não autorizadas.",
                "• Multi-LLM Híbrido: Gemini / OpenAI e execução 100% OFFLINE via Ollama Local.",
                "• Homologação: 365 testes Pytest aprovados e 1.000.000 de estudantes sintéticos simulados."
            ]
        },
        {
            "num": 7,
            "time": "04:30 - 05:00 (30s)",
            "category": "CONCLUSÃO & PERGUNTAS",
            "title": "Impacto Formativo & Encerramento",
            "subtitle": "Unindo o rigor do juiz de competição com a pedagogia socrática para formar a próxima geração de cientistas da computação.",
            "image": "slides_apresentacao/assets/diagrama_slide7_conclusao.png",
            "script": """[04:30 - 05:00 | CONCLUSÃO E Q&A]
\"O AutoTutor CP resgata o propósito essencial do ensino de computação: não se trata de decorar sintaxe ou copiar código pronto de uma IA, mas de aprender a raciocinar algoritmicamente diante do desconhecido.

Unindo pesquisa acadêmica validada, sandbox de execução segura e tutoria socrática adaptativa, entregamos uma solução pronta para transformar o treinamento de programação competitiva.

Agradeço imensamente a atenção de todos os professores e membros da banca, e estamos abertos para as considerações e perguntas.\"

AÇÃO DE PALCO: Pausa de 2 segundos. Postura ereta, respiração tranquila, olhar nos olhos dos avaliadores aguardando as perguntas.""",
            "key_points": [
                "• Fim da Atrofia Cognitiva: Alunos aprendem a pensar e analisar complexidade por conta própria.",
                "• Arquitetura Aberta e Segura: Sandbox resiliente, testes exaustivos e operação offline.",
                "• Autor: Brenno Phelipe Silva dos Santos | Fundamentos da Inteligência Artificial.",
                "• Aberto formalmente para as perguntas da banca avaliadora."
            ]
        }
    ]

    for item in slides_data:
        slide = prs.slides.add_slide(blank_layout)
        
        # Background escuro
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = COLOR_BG

        # Top Bar: Badge de Categoria + Tempo Cronometrado
        top_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.5))
        tf_top = top_box.text_frame
        tf_top.word_wrap = True
        tf_top.margin_left = tf_top.margin_top = tf_top.margin_right = tf_top.margin_bottom = 0
        p_top = tf_top.paragraphs[0]
        p_top.text = f"SLIDE {item['num']}  •  {item['category']}  •  TEMPO: {item['time']}"
        p_top.font.size = Pt(13)
        p_top.font.bold = True
        p_top.font.color.rgb = COLOR_CYAN

        # Título do Slide
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = item["title"]
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

        # Subtítulo do Slide
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = item["subtitle"]
        p_sub.font.size = Pt(14)
        p_sub.font.color.rgb = COLOR_MUTED

        # Imagem Principal (Centralizada / Widescreen)
        img_path = item["image"]
        if os.path.exists(img_path):
            # Imagem colocada em posição de destaque: W=11.73 polegadas, H=4.9 polegadas
            slide.shapes.add_picture(img_path, Inches(0.8), Inches(2.05), width=Inches(11.733))

        # Notas do Orador (Script Falado Exato)
        notes_slide = slide.notes_slide
        tf_notes = notes_slide.notes_text_frame
        tf_notes.text = f"=== SCRIPT FALADO DO SLIDE {item['num']} ({item['time']}) ===\n\n" + item["script"]

    # Salva nas duas localizações para máxima conveniência
    out1 = "slides_apresentacao/Apresentacao_AutoTutor_CP.pptx"
    out2 = "Apresentacao_AutoTutor_CP_Oficial.pptx"
    prs.save(out1)
    prs.save(out2)
    print(f"Apresentação PPTX gerada com sucesso em:\n  1. {out1}\n  2. {out2}")

if __name__ == "__main__":
    build_presentation()
