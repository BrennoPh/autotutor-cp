"""Explicit input grammars and reproducible structured test generators."""
import functools
import itertools
import json
import random
from config import DATA_PATH


@functools.lru_cache(maxsize=1)
def load_problems():
    return json.loads(DATA_PATH.read_text(encoding='utf-8')) + json.loads(DATA_PATH.with_name('local_classics.json').read_text(encoding='utf-8')) + json.loads(DATA_PATH.with_name('extended_contracts.json').read_text(encoding='utf-8'))


def clear_cache():
    """Clear cached problems catalog."""
    load_problems.cache_clear()


def generate_inputs(problem, seed=42):
    if problem.get('extended_task'):
        from core.extended_judge import inputs
        return inputs(problem,seed)
    if problem.get('local_task'):
        from core.classic_judge import classic_inputs
        return classic_inputs(problem, seed)
    if problem['family']=='segtree':
        from core.segment_tree import inputs
        return inputs(problem,seed)
    rng = random.Random(seed)
    family = problem['family']
    limit = problem['constraints']['n_max']
    cases = []

    def add(text, strategy):
        cases.append({'input': text, 'strategy': strategy})

    def array_case(a, strategy):
        n = len(a)
        if family == 'prefix':
            queries = ([(1, n)] * min(n, 50000) if strategy == 'tle_inducing' else [(1, n), (1, 1), (n, n)])
            add(f'{n} {len(queries)}\n' + ' '.join(map(str, a)) + '\n' +
                ''.join(f'{l} {r}\n' for l, r in queries), strategy)
        elif family == 'binary':
            add(f'{n} {max(1, n // 2)}\n' + ' '.join(map(str, a)) + '\n', strategy)
        else:
            add(f'{n}\n' + ' '.join(map(str, a)) + '\n', strategy)

    if family in ('prefix', 'binary', 'dp'):
        alphabet = (1, 2) if family == 'binary' else (0, 1, 2)
        for n in range(1, 4):
            for a in itertools.product(alphabet, repeat=n):
                array_case(a, 'small_exhaustive')
        for n in (7, 31, 93):
            array_case([rng.randint(1 if family == 'binary' else 0, 10**9) for _ in range(n)], 'random_extreme')
        array_case([10**9] * min(limit, 1000), 'random_extreme')
        array_case([10**9 if i % 2 else 1 for i in range(limit)], 'tle_inducing')
    elif family == 'greedy':
        def intervals(items, strategy):
            add(str(len(items)) + '\n' + ''.join(f'{l} {r}\n' for l, r in items), strategy)
        options = [(0, 1), (0, 2), (1, 2), (2, 3)]
        for n in range(1, 4):
            for items in itertools.combinations_with_replacement(options, n):
                intervals(items, 'small_exhaustive')
        intervals([(0, 100), (0, 1), (1, 2), (2, 3), (1, 3)], 'random_extreme')
        intervals([(i, i + rng.randint(1, 10)) for i in range(100)], 'random_extreme')
        intervals([(i, i + 1) for i in reversed(range(limit))], 'tle_inducing')
    elif family == 'graph':
        def graph(n, edges, strategy):
            add(f'{n} {len(edges)}\n' + ''.join(f'{a} {b}\n' for a, b in edges) + f'1 {n}\n', strategy)
        for n in range(1, 5):
            edges = list(itertools.combinations(range(1, n + 1), 2))
            for mask in range(1 << len(edges)):
                graph(n, [e for i, e in enumerate(edges) if mask >> i & 1], 'small_exhaustive')
        graph(10, [], 'random_extreme')
        graph(20, [(i, j) for i in range(1, 21) for j in range(i + 1, 21)], 'random_extreme')
        graph(limit, [(i, i + 1) for i in range(1, limit)], 'tle_inducing')
    elif family == 'tree':
        def tree(n, edges, strategy):
            add(str(n) + '\n' + ''.join(f'{a} {b}\n' for a, b in edges), strategy)
        tree(1, [], 'small_exhaustive')
        for n in range(2, 6):
            for parents in itertools.product(*(range(1, i) for i in range(2, n + 1))):
                tree(n, [(p, i) for i, p in enumerate(parents, 2)], 'small_exhaustive')
        tree(100, [(1, i) for i in range(2, 101)], 'random_extreme')
        tree(100, [(rng.randrange(1, i), i) for i in range(2, 101)], 'random_extreme')
        tree(limit, [(i, i + 1) for i in range(1, limit)], 'tle_inducing')
    else:
        raise ValueError('Família de entrada desconhecida.')
    return cases


def validate_input(problem, text):
    """Reject malformed generated inputs independently of the reference programs."""
    if problem.get('extended_task'):
        from core.extended_judge import validate
        return validate(problem,text)
    if problem.get('local_task'):
        from core.classic_judge import validate_classic
        return validate_classic(problem,text)
    if problem['family']=='segtree':
        from core.segment_tree import validate
        return validate(problem,text)
    tokens = list(map(int, text.split()))
    it = iter(tokens)
    n = next(it)
    if not 1 <= n <= problem['constraints']['n_max']:
        raise ValueError('N fora dos limites.')
    family = problem['family']
    if family == 'prefix':
        q = next(it)
        if not 1 <= q <= 200000:
            raise ValueError('Q fora dos limites.')
        values = [next(it) for _ in range(n)]
        for _ in range(q):
            l, r = next(it), next(it)
            if not 1 <= l <= r <= n:
                raise ValueError('Intervalo inválido.')
    elif family in ('dp', 'binary'):
        if family == 'binary' and not 1 <= next(it) <= n:
            raise ValueError('K inválido.')
        values = [next(it) for _ in range(n)]
    elif family == 'greedy':
        values = []
        for _ in range(n):
            l, r = next(it), next(it)
            if not 0 <= l < r <= 10**9:
                raise ValueError('Intervalo inválido.')
    else:
        values = []
        m = next(it) if family == 'graph' else n - 1
        if not 0 <= m <= 200000:
            raise ValueError('M inválido.')
        edges = set()
        parent = list(range(n + 1))
        def root(v):
            while parent[v] != v:
                v = parent[v]
            return v
        for _ in range(m):
            a, b = next(it), next(it)
            edge = tuple(sorted((a, b)))
            if not (1 <= a <= n and 1 <= b <= n) or a == b or edge in edges:
                raise ValueError('Aresta inválida.')
            edges.add(edge)
            if family == 'tree':
                ra, rb = root(a), root(b)
                if ra == rb:
                    raise ValueError('Árvore contém ciclo.')
                parent[ra] = rb
        if family == 'graph' and not (1 <= next(it) <= n and 1 <= next(it) <= n):
            raise ValueError('Origem/destino inválidos.')
    if any(v < (1 if family == 'binary' else 0) or v > 10**9 for v in values):
        raise ValueError('Valor fora dos limites.')
    if list(it):
        raise ValueError('Tokens excedentes.')
    return True
