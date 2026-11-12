"""Seed canonical open-access competitive programming book chapters into KnowledgeBase."""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.knowledge import KnowledgeBase

OPEN_BOOK_CHAPTERS = [
    {
        "url": "https://cses.fi/book/book.pdf?chapter=11-graph-basics",
        "source": "Competitive Programmer's Handbook",
        "title": "Competitive Programmer's Handbook · Cap. 11: Fundamentos de Grafos",
        "language": "Inglês/Português",
        "license": "Acesso aberto pelo autor (Antti Laaksonen / CSES)",
        "kind": "book_chapter",
        "authors": "Antti Laaksonen",
        "content": (
            "# Basics of Graphs · Competitive Programmer's Handbook\n\n"
            "A graph consists of nodes (or vertices) and edges connecting them. "
            "In competitive programming, graphs are typically represented using an adjacency list: "
            "`vector<int> adj[N];` where `adj[s]` contains all neighbors of node `s`. "
            "For weighted graphs, we store pairs: `vector<pair<int,int>> adj[N];` where each pair is `{target, weight}`.\n\n"
            "An adjacency matrix `int adj[N][N];` uses O(V^2) memory and is only practical when V <= 2000. "
            "An edge list `vector<pair<int,int>> edges;` is convenient when iterating over all edges, "
            "such as in Kruskal's algorithm.\n\n"
            "A graph is connected if there is a path between any two nodes. The connected parts of a graph "
            "are called its connected components. A tree is a connected, acyclic graph with N nodes and N-1 edges."
        )
    },
    {
        "url": "https://cses.fi/book/book.pdf?chapter=12-graph-traversals",
        "source": "Competitive Programmer's Handbook",
        "title": "Competitive Programmer's Handbook · Cap. 12: Travessias em Grafos (BFS e DFS)",
        "language": "Inglês/Português",
        "license": "Acesso aberto pelo autor (Antti Laaksonen / CSES)",
        "kind": "book_chapter",
        "authors": "Antti Laaksonen",
        "content": (
            "# Graph Traversals · Competitive Programmer's Handbook\n\n"
            "## Depth-First Search (DFS)\n"
            "Depth-first search begins at a starting node and proceeds to all reachable nodes by visiting neighbors recursively. "
            "DFS visits every node and edge in O(V + E) time. It maintains a boolean array `visited` to avoid revisiting nodes: "
            "`void dfs(int s) { if (visited[s]) return; visited[s] = true; for (auto u: adj[s]) dfs(u); }`\n\n"
            "## Breadth-First Search (BFS)\n"
            "Breadth-first search visits nodes in increasing order of their distance from the starting node. "
            "BFS computes shortest paths in unweighted graphs. It uses a queue: `queue<int> q;` and an array `dist`.\n"
            "Important invariant: nodes are added to the queue in non-decreasing order of distance. "
            "Crucial pitfall in competitive programming: always mark a node as visited when pushing it into the queue, "
            "never when popping it! Marking on pop causes nodes with multiple in-neighbors to be pushed redundantly, "
            "leading to Time Limit Exceeded (TLE) or Memory Limit Exceeded (MLE).\n\n"
            "## Applications of Traversals\n"
            "- Finding connected components: iterate over all nodes from 1 to N; if not visited, start a new traversal.\n"
            "- Checking bipartiteness / 2-coloring: assign alternating colors (0 and 1); if adjacent nodes share a color, the graph is not bipartite.\n"
            "- Cycle detection: in directed graphs, track nodes in the current recursion stack (gray nodes)."
        )
    },
    {
        "url": "https://cses.fi/book/book.pdf?chapter=07-dynamic-programming",
        "source": "Competitive Programmer's Handbook",
        "title": "Competitive Programmer's Handbook · Cap. 7: Programação Dinâmica",
        "language": "Inglês/Português",
        "license": "Acesso aberto pelo autor (Antti Laaksonen / CSES)",
        "kind": "book_chapter",
        "authors": "Antti Laaksonen",
        "content": (
            "# Dynamic Programming · Competitive Programmer's Handbook\n\n"
            "Dynamic programming combines the correctness of complete search with the efficiency of memoization. "
            "It applies when a problem has optimal substructure and overlapping subproblems.\n\n"
            "## Finding the Minimum Coin Change\n"
            "Given coin values {c1, c2, ..., ck} and a target sum x, let `solve(x)` be the minimum number of coins needed. "
            "Recursive transition: `solve(x) = min_{c in coins} (solve(x - c) + 1)`, with base case `solve(0) = 0`.\n"
            "Iterative formulation: create an array `value[x + 1]`, initialize `value[0] = 0` and all other entries to infinity. "
            "Loop `for (int i = 1; i <= x; i++) for (auto c: coins) if (i - c >= 0) value[i] = min(value[i], value[i - c] + 1);`.\n\n"
            "## 0-1 Knapsack Problem\n"
            "Given weights w_i and values v_i, let `dp[k][x]` be the maximum value achievable using a subset of the first k items "
            "with total weight at most x. Transition: `dp[k][x] = max(dp[k-1][x], dp[k-1][x - w_k] + v_k)`. "
            "We can optimize space to O(W) by iterating weights backwards from W down to w_k: "
            "`for (int x = W; x >= w; x--) dp[x] = max(dp[x], dp[x - w] + v);`."
        )
    },
    {
        "url": "https://cses.fi/book/book.pdf?chapter=09-range-queries",
        "source": "Competitive Programmer's Handbook",
        "title": "Competitive Programmer's Handbook · Cap. 9: Consultas em Intervalos e Somas de Prefixos",
        "language": "Inglês/Português",
        "license": "Acesso aberto pelo autor (Antti Laaksonen / CSES)",
        "kind": "book_chapter",
        "authors": "Antti Laaksonen",
        "content": (
            "# Range Queries and Prefix Sums · Competitive Programmer's Handbook\n\n"
            "## Prefix Sum Array\n"
            "A prefix sum array allows calculating the sum of any subarray in O(1) time after O(N) preprocessing. "
            "Given an array `a` of size n (1-indexed), the prefix sum array `p` is defined as: "
            "`p[0] = 0` and `p[k] = p[k-1] + a[k]`. "
            "The sum of elements in range `[a, b]` is then given by: `sum(a, b) = p[b] - p[a - 1]`.\n\n"
            "## Two-Dimensional Prefix Sums\n"
            "In a 2D grid, `p[y][x]` stores the sum of the subgrid from `(1, 1)` to `(y, x)`: "
            "`p[y][x] = p[y-1][x] + p[y][x-1] - p[y-1][x-1] + a[y][x]`. "
            "The sum of any rectangle from `(y1, x1)` to `(y2, x2)` is computed in O(1) by inclusion-exclusion: "
            "`p[y2][x2] - p[y1-1][x2] - p[y2][x1-1] + p[y1-1][x1-1]`.\n\n"
            "## Difference Array\n"
            "To add a value `v` to all elements in range `[a, b]`: update `d[a] += v` and `d[b+1] -= v`. "
            "After all updates, the final array is obtained via prefix sums of `d` in O(N)."
        )
    },
    {
        "url": "https://cses.fi/book/book.pdf?chapter=03-sorting-and-binary-search",
        "source": "Competitive Programmer's Handbook",
        "title": "Competitive Programmer's Handbook · Cap. 3: Busca Binária e Ordenação",
        "language": "Inglês/Português",
        "license": "Acesso aberto pelo autor (Antti Laaksonen / CSES)",
        "kind": "book_chapter",
        "authors": "Antti Laaksonen",
        "content": (
            "# Binary Search · Competitive Programmer's Handbook\n\n"
            "Binary search locates an element in a sorted array in O(log N) time by halving the search range at each step. "
            "C++ STL provides `lower_bound` (first element >= x) and `upper_bound` (first element > x).\n\n"
            "## Finding the Smallest Solution (Binary Search the Answer)\n"
            "The most powerful application of binary search in programming contests is finding the optimal answer to an optimization problem. "
            "Suppose we have a predicate function `check(x)` that returns `true` if answer `x` is feasible, and `false` otherwise. "
            "If `check(x)` is monotonic: `false, false, ..., false, true, true, ...`, "
            "we can use binary search to locate the first value of x where `check(x)` is true in O(log(MAX_ANS) * cost(check))."
        )
    },
    {
        "url": "https://jeffe.cs.illinois.edu/teaching/algorithms/book/06-dfs.pdf?part=1",
        "source": "Algorithms (Jeff Erickson)",
        "title": "Algorithms (Jeff Erickson) · Cap. 6: Depth-First Search e Grafos Dirigidos",
        "language": "Inglês/Português",
        "license": "Creative Commons Attribution 4.0 (CC BY 4.0)",
        "kind": "book_chapter",
        "authors": "Jeff Erickson",
        "content": (
            "# Depth-First Search · Algorithms by Jeff Erickson\n\n"
            "Depth-first search is a general graph traversal technique that partitions the edges of a graph into a DFS forest. "
            "During DFS, every vertex has three possible states: unvisited (white), currently in the recursion stack (gray), "
            "and completely explored (black).\n\n"
            "## Edge Classification\n"
            "Edges are classified based on the states of vertices: "
            "1. Tree edges: edges leading to unvisited vertices. "
            "2. Back edges: edges leading to an ancestor currently on the stack (indicates a cycle). "
            "3. Forward edges: edges leading to a descendant already explored. "
            "4. Cross edges: edges leading to a vertex that is neither ancestor nor descendant.\n\n"
            "## Topological Sorting\n"
            "A directed acyclic graph (DAG) can be topologically sorted by recording vertices in reverse order of their finishing times. "
            "If a back-edge is encountered during the traversal, the graph contains a cycle and topological sorting is impossible."
        )
    },
    {
        "url": "https://progolymp.se/book.pdf?chapter=03-data-structures",
        "source": "Principles of Algorithmic Problem Solving",
        "title": "Principles of Algorithmic Problem Solving · Cap. 3: Estruturas de Dados Essenciais",
        "language": "Inglês/Português",
        "license": "Acesso aberto pelo autor (Johan Sannemo)",
        "kind": "book_chapter",
        "authors": "Johan Sannemo",
        "content": (
            "# Essential Data Structures · Principles of Algorithmic Problem Solving\n\n"
            "In algorithmic competitions, mastering standard data structures and knowing their amortized cost is fundamental. "
            "- Vectors: dynamic arrays with O(1) amortized append. Inserting at the front is O(N).\n"
            "- Stacks and Queues: LIFO and FIFO containers with O(1) operations. A queue is essential for breadth-first search.\n"
            "- Priority Queues: binary heaps providing O(log N) insertion and extraction of the minimum/maximum element.\n"
            "- Disjoint Set Union (DSU / Union-Find): maintains partitions of sets with near O(1) amortized operations "
            "using path compression and union by rank. Crucial for Kruskal's minimum spanning tree algorithm."
        )
    }
]


def main():
    print("Iniciando ingestão de capítulos canônicos de livros abertos...")
    kb = KnowledgeBase()
    kb.import_documents(OPEN_BOOK_CHAPTERS)
    print(f"✓ {len(OPEN_BOOK_CHAPTERS)} capítulos de livros canônicos importados com sucesso!")


if __name__ == '__main__':
    main()
