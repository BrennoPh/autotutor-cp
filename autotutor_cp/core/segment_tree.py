"""Input contract and reproducible cases for point assignment / range minimum."""
from itertools import product
import random


def validate(problem, text):
    try:
        v=list(map(int,text.split()))
    except ValueError as exc:
        raise ValueError('A entrada deve conter apenas inteiros.') from exc
    if len(v)<2:raise ValueError('Informe N e Q.')
    n,q=v[:2]
    if not 1<=n<=problem['constraints']['n_max']:raise ValueError('N fora dos limites.')
    if not 1<=q<=problem['constraints'].get('q_max',200000):raise ValueError('Q fora dos limites.')
    if len(v)!=2+n+3*q:raise ValueError('Quantidade de valores ou operações inválida.')
    if any(not 0<=x<=10**9 for x in v[2:2+n]):raise ValueError('Valor fora dos limites.')
    for i in range(2+n,len(v),3):
        op,a,b=v[i:i+3]
        if op==1:
            if not 1<=a<=n or not 0<=b<=10**9:raise ValueError('Atualização inválida.')
        elif op==2:
            if not 1<=a<=b<=n:raise ValueError('Intervalo inválido.')
        else:raise ValueError('Operação inválida.')
    return True


def inputs(problem, seed):
    rng=random.Random(seed);cases=[]
    def add(values,ops,strategy):
        cases.append(dict(input=f'{len(values)} {len(ops)}\n'+' '.join(map(str,values))+'\n'+
                          ''.join(f'{op} {a} {b}\n' for op,a,b in ops),strategy=strategy))
    for n in range(1,min(3,problem['constraints']['n_max'])+1):
        queries=[(2,l,r) for l in range(1,n+1) for r in range(l,n+1)]
        for values in product((0,1,2),repeat=n):
            ops=list(queries)
            for k in range(1,n+1):
                for x in (10**9,0):ops.extend([(1,k,x),*queries])
            add(values,ops,'small_exhaustive')
    for n in (7,31,93):
        n=min(n,problem['constraints']['n_max'])
        values=[rng.choice((0,1,10**9,rng.randrange(10**9+1))) for _ in range(n)]
        ops=[(2,1,n),(2,1,1),(2,n,n)]
        for _ in range(100):
            k=rng.randint(1,n)
            ops.append((1,k,rng.choice((0,10**9))))
            l=rng.randint(1,n);ops.append((2,l,rng.randint(l,n)))
        add(values,ops,'random_extreme')
    n=problem['constraints']['n_max'];q=min(200000,2*n)
    values=[10**9]*n;values[0]=0;ops=[]
    for i in range(q):
        if i%2:ops.append((2,1,n))
        else:ops.append((1,(i//2)%n+1,i//2))
    add(values,ops,'tle_inducing')
    return cases
