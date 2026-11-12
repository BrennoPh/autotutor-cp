import os
from PIL import Image, ImageDraw, ImageFont
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

SLIDES_DIR = 'slides_apresentacao/slides_png'
os.makedirs(SLIDES_DIR, exist_ok=True)
ASSETS_DIR = 'slides_apresentacao/assets'

# Fontes do sistema
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

font_cat = get_font(18, bold=True)
font_title = get_font(34, bold=True)
font_sub = get_font(18, bold=False)
font_footer = get_font(14, bold=False)
font_badge = get_font(14, bold=True)

slides_spec = [
    {
        "num": 1,
        "time": "00:00 - 00:40 (40s)",
        "category": "O GANCHO & O PROBLEMA",
        "title": "O Abismo na Programação Competitiva: Por que Alunos Travam?",
        "subtitle": "Juízes punem sem explicar a causa raiz; IAs genéricas entregam o código pronto e atrofiam o aprendizado.",
        "inner_image": "diagrama_slide1_problema.png",
        "script": """\"Boa tarde à banca avaliadora. Todo estudante de Ciência da Computação conhece essa dor: você compreende a teoria em aula, abre o juiz online e recebe um seco: 'Wrong Answer no Teste 4'. O juiz diz O QUE está errado, mas nunca o PORQUÊ.

Do outro lado, quando o aluno pede ajuda a uma IA genérica, ela cospe o código pronto. Isso destrói o processo pedagógico: o aluno copia, passa o teste, mas não desenvolve musculatura algorítmica.

Foi para resolver esse abismo que criamos o AutoTutor CP: uma plataforma que integra juiz de execução real em C++ com tutoria socrática guiada por fundamentos científicos da literatura.\""""
    },
    {
        "num": 2,
        "time": "00:40 - 01:20 (40s)",
        "category": "FUNDAMENTAÇÃO CIENTÍFICA",
        "title": "A Tríade de Pesquisa: Ciência por Trás da Solução",
        "subtitle": "Três pilares da literatura acadêmica que fundamentam geração, recuperação e tutoria sem alucinação.",
        "inner_image": "diagrama_slide2_pilares.png",
        "script": """\"O AutoTutor CP não é um simples invólucro de API comercial. Ele é fundamentado em três publicações de ponta da literatura:

Primeiro, AutoCode (ICLR 2026): os problemas inéditos são gerados em par com um oráculo C++ e suite de testes. O sistema compila e valida cruzadamente antes de exibir ao aluno, garantindo zero problemas inválidos.

Segundo, OI-Assistant (IOI 2025): nosso RAG recupera exercícios e analogias pela essência matemática e invariantes do algoritmo — como subestrutura ótima ou monotonicidade —, e não por palavras soltas.

E terceiro, CODIGEN (IEEE VL/HCC 2025): o tutor opera sob restrições cognitivas estritas. Ele diagnostica a quebra de invariantes e oferece uma escada gradual de dicas, impedindo que o aluno veja a solução antes de exercitar o raciocínio.\""""
    },
    {
        "num": 3,
        "time": "01:20 - 02:10 (50s)",
        "category": "DEMONSTRAÇÃO DE PRODUTO 1",
        "title": "O Workspace de Resolução & O Juiz Online C++",
        "subtitle": "Ambiente integrado com editor Monaco C++17, compilação isolada em sandbox Bubblewrap e tutor socrático em tempo real.",
        "inner_image": "arena_problem.png",
        "script": """\"Esta é a tela de resolução do estudante. Do lado esquerdo, temos a especificação formal do problema com restrições assintóticas de tempo e memória. No centro, o editor Monaco rodando C++17.

Ao submeter o código, a execução não roda em ambiente desprotegido: ela é despachada para o nosso juiz isolado 'isolated_judge.py', compilada via G++ com limites rígidos POSIX de 256MB e contenção por Bubblewrap.

Observem o console: o juiz detectou Time Limit Exceeded. Em vez de deixar o aluno desamparado, o tutor socrático analisa o código submetido e intervém: 'Percebeu que para cada elemento você percorre todo o vetor novamente? Como manter essa busca em O(1) usando um acumulador de prefixo?'

A IA não dá o código pronto. Ela guia o aluno exatamente para a quebra de complexidade.\""""
    },
    {
        "num": 4,
        "time": "02:10 - 03:00 (50s)",
        "category": "DEMONSTRAÇÃO DE PRODUTO 2",
        "title": "O Quadro Branco Interativo de Grafos (Whiteboard)",
        "subtitle": "Conexão intuitiva de nós topológicos sincronizada com código C++ e animação da pilha de execução viva.",
        "inner_image": "whiteboard_full.png",
        "script": """\"Um dos maiores gargalos cognitivos em computação é a abstração espacial de ponteiros e grafos. Por isso desenvolvemos o nosso Quadro Branco Interativo.

Aqui o aluno constrói o grafo livremente ou importa a topologia do problema. Ele adiciona vértices, conecta arestas direcionadas ou ponderadas e acopla a implementação do algoritmo de busca — como DFS, BFS ou Dijkstra.

Ao acionar a execução passo a passo, o motor sincroniza o runtime C++ com a malha visual: os nós mudam de cor conforme o ciclo de vida da busca, e a pilha de memória de recursão é desenhada ao vivo ao lado.

O estudante enxerga visualmente o exato momento em que o backtracking ocorre, desmistificando o comportamento da pilha de execução do sistema.\""""
    },
    {
        "num": 5,
        "time": "03:00 - 03:50 (50s)",
        "category": "DEMONSTRAÇÃO DE PRODUTO 3",
        "title": "Diagnóstico Adaptativo & Calendário Diário Espaçado",
        "subtitle": "Micro-quiz calibrado que mapeia lacunas conceituais e gera automaticamente um cronograma diário com repetição espaçada.",
        "inner_image": "composite_slide5_onboarding_calendar.png",
        "script": """\"Nenhum estudante começa do mesmo patamar. Por isso, eliminamos trilhas estáticas lineares que tratam todos como iguais.

Na primeira tela à esquerda, no Onboarding, o estudante responde a um micro-quiz diagnóstico calibrado. Nosso backend processa o padrão de respostas e mapeia com precisão matemática os tópicos dominados e as lacunas conceituais — por exemplo, forte em recursão, mas com lacuna em programação dinâmica.

A partir desse perfil, o motor algorítmico gera instantaneamente o Calendário Adaptativo à direita.

Reparem no equilíbrio: tarefas teóricas no Study Reader intercaladas com desafios práticos na Arena, respeitando o ritmo e a rotina do aluno com repetição espaçada. Toda a jornada é orientada por dados pedagógicos reais.\""""
    },
    {
        "num": 6,
        "time": "03:50 - 04:30 (40s)",
        "category": "ARQUITETURA & RESILIÊNCIA",
        "title": "Engenharia de Software de Alta Resiliência",
        "subtitle": "Next.js 14 moderno, backend assíncrono, isolamento sandbox Bubblewrap e suporte a LLM 100% offline via Ollama.",
        "inner_image": "diagrama_slide6_arquitetura.png",
        "script": """\"Para garantir confiabilidade de produção, nossa arquitetura foi projetada em camadas estritamente desacopladas:

O frontend roda em Next.js 14 App Router com tipagem estrita TypeScript e design ergonômico sóbrio. O backend é impulsionado por FastAPI assíncrono e persistência transacional em SQLite.

A execução de código utiliza sandbox Bubblewrap com limites POSIX, contendo com sucesso vazamentos de memória e fork-bombs.

E um detalhe crucial para ambientes acadêmicos: nosso motor de IA é híbrido. Ele pode operar com Google Gemini ou OpenAI em nuvem, mas funciona 100% OFFLINE através do Ollama local, sem depender de internet.

Toda essa estrutura foi homologada com 365 testes no Pytest e auditada com um milhão de jornadas simuladas.\""""
    },
    {
        "num": 7,
        "time": "04:30 - 05:00 (30s)",
        "category": "CONCLUSÃO & PERGUNTAS",
        "title": "Impacto Formativo & Encerramento",
        "subtitle": "Unindo o rigor do juiz de competição com a pedagogia socrática para formar a próxima geração de cientistas da computação.",
        "inner_image": "diagrama_slide7_conclusao.png",
        "script": """\"O AutoTutor CP resgata o propósito essencial do ensino de computação: não se trata de decorar sintaxe ou copiar código pronto de uma IA, mas de aprender a raciocinar algoritmicamente diante do desconhecido.

Unindo pesquisa acadêmica validada, sandbox de execução segura e tutoria socrática adaptativa, entregamos uma solução pronta para transformar o treinamento de programação competitiva.

Agradeço imensamente a atenção de todos os professores e membros da banca, e estamos abertos para as considerações e perguntas.\""""
    }
]

rendered_images = []

W, H = 1920, 1080
for s in slides_spec:
    slide_img = Image.new('RGB', (W, H), (15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(slide_img)

    # 1. Top Bar: Badge Categoria + Cronômetro
    draw.rounded_rectangle([60, 30, 480, 68], radius=8, fill=(30, 41, 59), outline=(56, 189, 248), width=1)
    draw.text((75, 38), f"SLIDE {s['num']} • {s['category']}", fill=(56, 189, 248), font=font_cat)

    time_w = len(s['time']) * 11 + 30
    draw.rounded_rectangle([W - 60 - time_w, 30, W - 60, 68], radius=8, fill=(30, 41, 59), outline=(52, 211, 153), width=1)
    draw.text((W - 45 - time_w, 38), f"⏱ {s['time']}", fill=(52, 211, 153), font=font_cat)

    # 2. Título & Subtítulo
    draw.text((60, 85), s["title"], fill=(248, 250, 252), font=font_title)
    draw.text((60, 135), s["subtitle"], fill=(148, 163, 184), font=font_sub)

    # 3. Imagem de Conteúdo
    inner_path = os.path.join(ASSETS_DIR, s["inner_image"])
    if os.path.exists(inner_path):
        inner_im = Image.open(inner_path)
        # Área de exibição: X=60, Y=180, W=1800, H=830
        target_w = 1800
        target_h = 830
        
        # Ajuste proporcional
        inner_im.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Centraliza dentro do quadro
        pos_x = 60 + (target_w - inner_im.width) // 2
        pos_y = 180 + (target_h - inner_im.height) // 2
        
        # Moldura de fundo
        draw.rounded_rectangle([pos_x - 3, pos_y - 3, pos_x + inner_im.width + 3, pos_y + inner_im.height + 3], radius=12, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        slide_img.paste(inner_im, (pos_x, pos_y))

    # 4. Rodapé
    draw.text((60, 1035), "AutoTutor CP — Plataforma EdTech de Programação Competitiva & Tutoria de IA", fill=(100, 116, 139), font=font_footer)
    draw.text((W - 140, 1035), f"{s['num']} / 7", fill=(148, 163, 184), font=font_footer)

    slide_file = os.path.join(SLIDES_DIR, f"slide_{s['num']:02d}.png")
    slide_img.save(slide_file, quality=95)
    rendered_images.append(slide_img)
    print(f"Slide {s['num']} renderizado em: {slide_file}")

# Salva PDF Oficial combinando todas as 7 imagens
pdf_out1 = "slides_apresentacao/Apresentacao_AutoTutor_CP.pdf"
pdf_out2 = "Apresentacao_AutoTutor_CP_Oficial.pdf"

if rendered_images:
    first = rendered_images[0]
    rest = rendered_images[1:]
    first.save(pdf_out1, save_all=True, append_images=rest, resolution=150)
    first.save(pdf_out2, save_all=True, append_images=rest, resolution=150)
    print(f"PDF Oficial gerado com sucesso em:\n  1. {pdf_out1}\n  2. {pdf_out2}")

