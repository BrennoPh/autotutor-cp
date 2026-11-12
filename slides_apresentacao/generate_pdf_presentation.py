import subprocess
import os

html_path = os.path.abspath('slides_apresentacao/apresentacao_autotutor_cp.html')
pdf_path1 = os.path.abspath('slides_apresentacao/Apresentacao_AutoTutor_CP.pdf')
pdf_path2 = os.path.abspath('Apresentacao_AutoTutor_CP_Oficial.pdf')

# Criar versão específica para impressão (onde todos os 7 slides aparecem como páginas individuais)
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Substitui estilos para garantir que no print cada slide seja uma página separada 16:9
print_styles = """
  <style>
    @media print {
      @page {
        size: 1920px 1080px;
        margin: 0;
      }
      body, html {
        width: 1920px !important;
        height: auto !important;
        overflow: visible !important;
        background: #0f172a !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
      .controls-bar, .notes-drawer {
        display: none !important;
      }
      .slide {
        display: flex !important;
        width: 1920px !important;
        height: 1080px !important;
        page-break-after: always !important;
        page-break-inside: avoid !important;
        padding: 48px 80px !important;
        opacity: 1 !important;
        box-sizing: border-box !important;
      }
      .slide-title {
        font-size: 38px !important;
      }
      .slide-subtitle {
        font-size: 20px !important;
      }
      .badge, .time-badge {
        font-size: 16px !important;
        padding: 6px 18px !important;
      }
    }
  </style>
"""

printable_html = content.replace('</head>', print_styles + '</head>')
tmp_print_html = '/tmp/presentation_printable.html'
with open(tmp_print_html, 'w', encoding='utf-8') as f:
    f.write(printable_html)

cmd = [
    'google-chrome',
    '--headless=new',
    '--disable-gpu',
    '--no-pdf-header-footer',
    f'--print-to-pdf={pdf_path1}',
    tmp_print_html
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Resultado PDF 1:", res.returncode, res.stdout, res.stderr)

if os.path.exists(pdf_path1):
    import shutil
    shutil.copyfile(pdf_path1, pdf_path2)
    print(f"PDF gerado com sucesso em:\n  1. {pdf_path1}\n  2. {pdf_path2}")
