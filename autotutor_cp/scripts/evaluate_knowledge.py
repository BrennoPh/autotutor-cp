"""Offline retrieval checks on the imported corpus, without paid API calls."""
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.knowledge import KnowledgeBase

CASES=[('BFS','breadth|graph traversal|grafos'),('DFS','depth|graph traversal|tree'),
 ('soma de prefixos','prefix'),('programação dinâmica','dynamic programming|introduction to dp|^dp'),
 ('problemas ad hoc','ad hoc'),('árvores','arvor|árvor|tree'),('busca binária','binary|busca bin.ria'),
 ('ordenação','sort|ordena'),('dijkstra','dijkstra'),('fenwick','fenwick'),('knapsack','knapsack|mochila')]


def main():
    kb=KnowledgeBase();results=[]
    for query,pattern in CASES:
        hits=kb.search(query,limit=5,per_document=1)
        results.append(dict(query=query,passed=any(re.search(pattern,h['title'],re.I) for h in hits),titles=[h['title'] for h in hits]))
    report=dict(scope='Correspondência dos tópicos esperados nos cinco primeiros resultados; não avalia a qualidade de respostas de IA.',stats=kb.stats(),checks=results,passed=sum(r['passed'] for r in results),total=len(results))
    print(json.dumps(report,ensure_ascii=False,indent=2));return int(not all(r['passed'] for r in results))

if __name__=='__main__':raise SystemExit(main())
