import subprocess
import time
import os
from PIL import Image

# 1. Inicia um http server temporário na porta 8888
server = subprocess.Popen(['python3', '-m', 'http.server', '8888', '--directory', 'slides_apresentacao'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

try:
    pdf_path = os.path.abspath('slides_apresentacao/Apresentacao_AutoTutor_CP.pdf')
    cmd = [
        'google-chrome',
        '--headless=new',
        '--disable-gpu',
        '--virtual-time-budget=8000',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_path}',
        'http://localhost:8888/apresentacao_autotutor_cp.html'
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Chrome status:", res.returncode)

    # Verifica
    subprocess.run(['pdftoppm', '-png', '-r', '100', '-f', '1', '-l', '1', pdf_path, '/tmp/test_http_page1'])
    img_name = '/tmp/test_http_page1-01.png' if os.path.exists('/tmp/test_http_page1-01.png') else '/tmp/test_http_page1-1.png'
    im = Image.open(img_name)
    crop = im.crop((200, 250, 1800, 950))
    colors = crop.getcolors(maxcolors=1000000)
    print("Unique colors count in image crop:", len(colors) if colors else 'many')
finally:
    server.terminate()
