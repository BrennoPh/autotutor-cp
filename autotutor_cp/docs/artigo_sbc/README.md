> Esta versão anterior foi preservada. A revisão com foco em fundamentos está em `output/fundamentos_2026-11-05/entrega/artigo/` na raiz do projeto, acompanhada de apresentação e protocolo atualizado.

# Artigo AutoTutor — formato SBC

Artigo em português, com abstract em inglês, foco nos fundamentos de IA e resultados exploratórios do protótipo. PDF: 10 páginas. Não demonstra ganho de aprendizagem e não relata treinamento dos pesos.

## Arquivos

- `artigo.tex`: texto e figura vetorial TikZ.
- `referencias.bib`: bibliografia científica e fontes do corpus.
- `sbc-template.sty` e `sbc.bst`: estilo SBC, cópia do espelho público do IME/USP: https://linux.ime.usp.br/~capella/mac0499/local/ARTIGO/template-latex/ . Estilo com atualização de dezembro de 2017.
- `artigo.pdf`: versão compilada e conferida visualmente.
- `evidencias/`: resultados exploratórios usados no texto, sem dados privados de alunos.

## Compilação

Na pasta destes arquivos, execute:

```sh
pdflatex -interaction=nonstopmode -halt-on-error artigo.tex
bibtex artigo
pdflatex -interaction=nonstopmode -halt-on-error artigo.tex
pdflatex -interaction=nonstopmode -halt-on-error artigo.tex
```

Requer LaTeX com português/babel, fontes Times, AMS e TikZ. No Overleaf, carregue os arquivos e selecione `artigo.tex` como documento principal (pdfLaTeX).

## Antes de submeter

Preencha as macros de autor, instituição, local e e-mail no início de `artigo.tex`. Confirme o limite de páginas e a versão de modelo exigidos pelo evento; não foi informado um evento específico. O arquivo não usa hyperref porque a combinação do estilo de 2017 com os hooks de babel do ambiente local apresentou incompatibilidade. URLs e citações permanecem no texto.

A avaliação usa 12 consultas e cinco questões sintéticas, sem participantes. Resultados de formato e correção não devem ser interpretados como estudo de eficácia educacional ou ranking de provedores.
