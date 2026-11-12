import subprocess
import os
from PIL import Image

html_path = os.path.abspath('slides_apresentacao/apresentacao_autotutor_cp.html')
pdf_path = os.path.abspath('slides_apresentacao/Apresentacao_AutoTutor_CP.pdf')

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

print_styles = """
  <style>
    @media print {
      @page {
        size: 1920px 1080px;
        margin: 0;
      }
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
      body, html {
        width: 1920px !important;
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        background: #0f172a !important;
      }
      .controls-bar, .notes-drawer {
        display: none !important;
      }
      .slide {
        display: block !important;
        width: 1920px !important;
        height: 1080px !important;
        page-break-after: always !important;
        page-break-inside: avoid !important;
        padding: 40px 60px !important;
        background: #0f172a !important;
        box-sizing: border-box !important;
      }
      .slide-header {
        height: 140px !important;
        margin-bottom: 20px !important;
      }
      .slide-title {
        font-size: 34px !important;
        color: #ffffff !important;
      }
      .slide-subtitle {
        font-size: 18px !important;
        color: #94a3b8 !important;
      }
      .slide-body {
        display: block !important;
        width: 1800px !important;
        height: 840px !important;
        margin: 0 auto !important;
      }
      .image-wrapper {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 1800px !important;
        height: 840px !important;
        background: #1e293b !important;
        border: 2px solid #334155 !important;
        border-radius: 16px !important;
        overflow: hidden !important;
      }
      .image-wrapper img {
        width: 100% !important;
        height: 100% !important;
        max-width: 1800px !important;
        max-height: 840px !important;
        object-fit: contain !important;
        display: block !important;
      }
    }
  </style>
"""

printable_html = content.replace('</head>', print_styles + '</head>')
tmp_print_html = '/tmp/presentation_printable2.html'
with open(tmp_print_html, 'w', encoding='utf-8') as f:
    f.write(printable_html)

cmd = [
    'google-chrome',
    '--headless=new',
    '--disable-gpu',
    '--virtual-time-budget=5000',
    '--no-pdf-header-footer',
    f'--print-to-pdf={pdf_path}',
    tmp_print_html
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Chrome print status:", res.returncode)

# Converter primeira página para conferir
subprocess.run(['pdftoppm', '-png', '-r', '100', '-f', '1', '-l', '1', pdf_path, '/tmp/test_pdf_page1'])

im = Image.open('/tmp/test_pdf_page1-01.png' if os.path.exists('/tmp/test_pdf_page1-01.png') else '/tmp/test_pdf_page1-1.png')
print('Page 1 size:', im.size)
crop = im.crop((200, 250, 1800, 950))
colors = crop.getcolors(maxcolors=1000000)
print('Number of colors in image area:', len(colors) if colors else 'many')
