#!/usr/bin/env python3
"""Script para importar livros pessoais e PDFs locais para o acervo de conhecimento (RAG) do AutoTutor."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys

# Garante que o diretório autotutor_cp esteja no sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.knowledge import KnowledgeBase


class ScannedPdfError(Exception):
    """Lançado quando o PDF é composto apenas por imagens escaneadas sem camada de texto OCR."""
    pass


def extract_text_from_pdf(pdf_path, max_pages=None):
    """Extrai texto de um arquivo PDF usando pdftotext do sistema ou pypdf."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

    # Método 1: pdftotext do sistema (muito rápido e preserva layout)
    pdftotext_bin = shutil.which("pdftotext") or ("/usr/bin/pdftotext" if Path("/usr/bin/pdftotext").exists() else None)
    if pdftotext_bin:
        cmd = [str(pdftotext_bin), "-layout"]
        if max_pages:
            cmd.extend(["-l", str(max_pages)])
        cmd.extend([str(pdf_path), "-"])
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            text = (res.stdout or "").strip()
            clean_sample = re.sub(r'[\s\x0c]', '', text)
            if len(clean_sample) >= 300:
                return res.stdout
            raise ScannedPdfError(
                "O PDF não possui camada de texto pesquisável (trata-se de uma digitalização por imagens/escaneamento sem OCR)."
            )
        except subprocess.CalledProcessError:
            pass
        except ScannedPdfError:
            raise

    # Método 2: biblioteca pypdf (se instalada)
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        num_pages = len(reader.pages)
        if max_pages:
            num_pages = min(num_pages, max_pages)
        pages = []
        for i in range(num_pages):
            text = reader.pages[i].extract_text() or ""
            pages.append(text)
        combined = "\n\n".join(pages)
        clean_sample = re.sub(r'[\s\x0c]', '', combined)
        if len(clean_sample) >= 300:
            return combined
        raise ScannedPdfError(
            "O PDF não possui camada de texto pesquisável (trata-se de uma digitalização por imagens/escaneamento sem OCR)."
        )
    except ImportError:
        pass

    raise RuntimeError(
        "Não foi possível extrair texto do PDF. Certifique-se de que o utilitário 'pdftotext' "
        "(pacote poppler-utils) ou a biblioteca Python 'pypdf' estejam instalados."
    )


def extract_text_from_djvu(djvu_path):
    """Tenta extrair texto de arquivo DjVu se djvutxt estiver disponível."""
    bin_path = shutil.which("djvutxt") or ("/usr/bin/djvutxt" if Path("/usr/bin/djvutxt").exists() else None)
    if bin_path:
        try:
            res = subprocess.run([str(bin_path), str(djvu_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if res.stdout and len(res.stdout.strip()) > 100:
                return res.stdout
        except Exception:
            pass
    return None


def clean_book_text(text):
    """Remove ruídos comuns de digitalização e paginação."""
    # Remove números de página isolados
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.M)
    # Remove cabeçalhos repetidos de página comuns
    text = re.sub(r'^\s*(Page|Página)\s+\d+\s*(of\s+\d+)?\s*$', '', text, flags=re.M | re.I)
    # Normaliza múltiplos espaços e quebras de linha em excesso
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def chunk_text(text, max_chunk_chars=3500, min_chunk_chars=300):
    """Divide o texto em seções coerentes respeitando parágrafos e cabeçalhos."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_len = 0
    current_heading = 'Introdução / Início'

    heading_pattern = re.compile(r'^(?:#{1,4}\s+|Chapter\s+\d+|Capítulo\s+\d+|\d+\.\d+\s+)(.+)$', re.I | re.M)

    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue

        first_line = p_clean.splitlines()[0]
        h_match = heading_pattern.match(first_line)
        if h_match:
            current_heading = h_match.group(1).strip()[:100]

        p_len = len(p_clean)
        if current_len + p_len > max_chunk_chars and current_len >= min_chunk_chars:
            chunks.append((current_heading, '\n\n'.join(current_chunk)))
            current_chunk = [p_clean]
            current_len = p_len
        else:
            current_chunk.append(p_clean)
            current_len += p_len + 2

    if current_chunk:
        chunks.append((current_heading, '\n\n'.join(current_chunk)))

    return chunks


def import_book(file_path, title=None, author=None, topic=None, dry_run=False, kb=None):
    """Importa um livro (PDF, TXT ou MD) para o banco de dados do RAG."""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"Erro: Arquivo '{file_path}' não existe.")
        return 0

    suffix = file_path.suffix.lower()
    if suffix == '.djvu':
        djvu_text = extract_text_from_djvu(file_path)
        if not djvu_text:
            print(f"\n📖 Processando: {file_path.name}")
            print("  ⚠️ [PULADO: FORMATO DJVU] O arquivo está no formato DjVu e a ferramenta 'djvutxt' não está instalada.")
            print("     Como resolver no Ubuntu/Debian:")
            print("       sudo apt update && sudo apt install -y djvulibre-bin")
            print("     Após instalar, execute este script novamente para importar os trechos.")
            return 0
        raw_text = djvu_text
    elif suffix == '.pdf':
        title = title or file_path.stem.replace('_', ' ').replace('-', ' ').title()
        author = author or "Autor do livro (acervo pessoal)"
        print(f"\n📖 Processando: {file_path.name}")
        print(f"  Título: {title}")
        print(f"  Autor: {author}")
        if topic:
            print(f"  Tópico associado: {topic}")
        try:
            raw_text = extract_text_from_pdf(file_path)
        except ScannedPdfError:
            print("  ⚠️ [PULADO: PDF ESCANEADO SEM OCR]")
            print("     Este arquivo é uma fotocópia escaneada de livro físico (fotos de páginas, sem texto selecionável).")
            print("     Como torná-lo pesquisável no Linux:")
            print("       sudo apt install -y ocrmypdf tesseract-ocr-por")
            print(f"       ocrmypdf '{file_path.name}' '{file_path.stem}_ocr.pdf'")
            return 0
        except Exception as exc:
            print(f"  ❌ Erro ao ler PDF: {exc}")
            return 0
    elif suffix in ('.txt', '.md'):
        title = title or file_path.stem.replace('_', ' ').replace('-', ' ').title()
        author = author or "Autor do livro (acervo pessoal)"
        print(f"\n📖 Processando: {file_path.name}")
        print(f"  Título: {title}")
        print(f"  Autor: {author}")
        raw_text = file_path.read_text(encoding='utf-8', errors='ignore')
    else:
        print(f"\n📖 Processando: {file_path.name}")
        print(f"  ⚠️ Formato não suportado: '{suffix}'. Formatos aceitos: .pdf, .txt, .md")
        return 0

    cleaned = clean_book_text(raw_text)
    if len(cleaned) < 300:
        print("  ⚠️ Texto extraído muito curto ou ilegível após limpeza. Pulando...")
        return 0

    chunks = chunk_text(cleaned)
    print(f"  ✓ Texto extraído: {len(cleaned):,} caracteres.")
    print(f"  ✓ Seções geradas: {len(chunks)} trechos para o RAG.")

    if dry_run:
        print("  [DRY-RUN] Exibindo amostra do primeiro trecho:")
        sample_heading, sample_body = chunks[0]
        print(f"  --- Trecho 1 ({sample_heading}) ---")
        print(f"  {sample_body[:300]}...\n")
        return len(chunks)

    kb = kb or KnowledgeBase()
    safe_slug = re.sub(r'[^a-z0-9_-]', '', title.lower().replace(' ', '-'))[:30] or "livro"
    documents = []

    for i, (heading, body) in enumerate(chunks):
        doc_url = f"https://local.autotutor/livros/{safe_slug}?part={i+1}"
        doc_title = f"{title} · Parte {i+1}: {heading}"
        if topic:
            doc_title += f" [{topic}]"

        documents.append({
            'url': doc_url,
            'source': f"Livro: {title}",
            'title': doc_title,
            'language': 'Português/Inglês',
            'license': 'Acervo pessoal local do usuário',
            'kind': 'user_book',
            'authors': author,
            'content': body
        })

    kb.import_documents(documents)
    print(f"  ✓ {len(documents)} trechos indexados com sucesso no banco de conhecimento!")
    return len(documents)


def main():
    parser = argparse.ArgumentParser(description="Importador de Livros e PDFs para o RAG do AutoTutor")
    parser.add_argument("--pdf", help="Caminho para um arquivo PDF individual")
    parser.add_argument("--dir", help="Pasta com PDFs/TXTs para importar (padrão: data/meus_livros)")
    parser.add_argument("--title", help="Título do livro (opcional, deduzido do nome do arquivo)")
    parser.add_argument("--author", help="Nome do autor do livro")
    parser.add_argument("--topic", help="Assunto canônico (ex.: graph, dp, math, binary, prefix)")
    parser.add_argument("--dry-run", action="store_true", help="Simula a extração sem salvar no banco")
    args = parser.parse_args()

    default_dir = BASE_DIR / "data" / "meus_livros"
    target_dir = Path(args.dir) if args.dir else (default_dir if not args.pdf else None)

    total_chunks = 0
    total_books = 0
    if args.pdf:
        n = import_book(args.pdf, title=args.title, author=args.author, topic=args.topic, dry_run=args.dry_run)
        if n > 0:
            total_books += 1
            total_chunks += n
    elif target_dir and target_dir.exists():
        files = sorted(
            list(target_dir.glob("*.pdf"))
            + list(target_dir.glob("*.txt"))
            + list(target_dir.glob("*.md"))
            + list(target_dir.glob("*.djvu"))
        )
        if not files:
            print(f"Nenhum arquivo encontrado em '{target_dir}'.")
            print("Coloque seus livros nessa pasta e execute novamente este script!")
            return

        print(f"Encontrados {len(files)} arquivos na pasta '{target_dir}'.")
        for f in files:
            if f.name.lower().startswith('readme'):
                continue
            n = import_book(f, dry_run=args.dry_run)
            if n > 0:
                total_books += 1
                total_chunks += n
    else:
        print("Uso:")
        print("  Para importar todos os livros da pasta data/meus_livros:")
        print(f"    python autotutor_cp/scripts/import_user_books.py --dir {default_dir}")
        print("  Para importar um PDF específico:")
        print("    python autotutor_cp/scripts/import_user_books.py --pdf caminho/livro.pdf --title 'Nome do Livro'")
        print("  Para apenas testar sem gravar no banco:")
        print("    python autotutor_cp/scripts/import_user_books.py --dir data/meus_livros --dry-run")

    if total_chunks > 0:
        mode_str = "[DRY-RUN] " if args.dry_run else ""
        print(f"\n🎉 {mode_str}Concluído! {total_books} livro(s) processado(s) com sucesso, gerando {total_chunks} trechos indexados no acervo do AutoTutor.")


if __name__ == "__main__":
    main()
