# 📚 Pasta de Livros Pessoais do Usuário

Coloque aqui os seus livros em formato **PDF**, **TXT** ou **Markdown** que você deseja adicionar ao acervo do tutor inteligente (RAG).

### Como importar os livros desta pasta para o AutoTutor:

No terminal, execute:
```bash
autotutor_cp/.venv/bin/python autotutor_cp/scripts/import_user_books.py
```

Ou para importar um arquivo PDF específico:
```bash
autotutor_cp/.venv/bin/python autotutor_cp/scripts/import_user_books.py --pdf "caminho/para/meu_livro.pdf" --title "Nome do Livro" --author "Nome do Autor"
```

Para apenas visualizar como o livro será fatiado sem salvar no banco de dados (modo de teste):
```bash
autotutor_cp/.venv/bin/python autotutor_cp/scripts/import_user_books.py --pdf "caminho/para/meu_livro.pdf" --dry-run
```

O script extrai o texto, limpa numerações de página e cabeçalhos repetidos, e indexa os capítulos no banco de dados local do seu AutoTutor (`autotutor_cp/data/knowledge.sqlite3`), ficando disponível imediatamente para as gerações de estudo!
