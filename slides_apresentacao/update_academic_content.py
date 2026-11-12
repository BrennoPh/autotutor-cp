import re

file_path = 'slides_apresentacao/build_academic_presentation.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Atualiza os dados matemáticos do Slide 4 para refletir exatamente os pesos 0.25, 0.45, 0.30 do rag_retriever.py
formula_old = 'Score_Final(P, Q) = w_1 * Sim_Cosseno(V_1^P, V_1^Q) + w_2 * Sim_Cosseno(V_2^P, V_2^Q) + w_3 * Sim_Cosseno(V_3^P, V_3^Q)'
formula_new = 'Score_Final(P, Q) = 0.25 * TFIDF_enunciado + 0.45 * TFIDF_essencia_matematica + 0.30 * TFIDF_estrategia'

code = code.replace(formula_old, formula_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Código de apresentação atualizado com a fórmula exata do OI-Assistant!")
