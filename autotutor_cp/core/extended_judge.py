"""Independent input contracts and Python oracles for additional local exercises."""
from collections import deque
from itertools import product,combinations
import math,random

RANGE_TASKS={'range_sum','range_max','range_xor','range_add_sum'}
GRAPH_TASKS={'components','bipartite','nearest_source','cycle'}


def parse(task,text):
    values=list(map(int,text.split()));it=iter(values);n=next(it);q=next(it)
    if task in RANGE_TASKS:
        a=[next(it) for _ in range(n)];ops=[]
        for _ in range(q):
            op=next(it);x=next(it);y=next(it)
            ops.append((op,x,y,next(it)) if task=='range_add_sum' and op==1 else (op,x,y))
        result=(n,a,ops)
    else:
        edges=[(next(it),next(it)) for _ in range(q)]
        sources=[next(it) for _ in range(next(it))] if task=='nearest_source' else []
        result=(n,edges,sources)
    if next(it,None) is not None:raise ValueError('Tokens excedentes.')
    return result


def validate(p,text):
    task=p['extended_task']
    try:
        header=list(map(int,text.split()[:2]))
        if len(header)!=2 or not 1<=header[0]<=p['constraints']['n_max']:raise ValueError('N inválido.')
        if not 0<=header[1]<=30000 or (task in RANGE_TASKS and header[1]==0):raise ValueError('Quantidade inválida.')
        n,a,b=parse(task,text)
        if task in RANGE_TASKS:
            if any(not 0<=x<=10**9 for x in a):raise ValueError('Valor inicial inválido.')
            for op in b:
                t,l,r=op[:3]
                if t not in (1,2):raise ValueError('Operação inválida.')
                if t==2 or task=='range_add_sum':
                    if not 1<=l<=r<=n:raise ValueError('Intervalo inválido.')
                    if len(op)==4 and not 0<=op[3]<=10**9:raise ValueError('Incremento inválido.')
                elif not (1<=l<=n and 0<=r<=10**9):raise ValueError('Atualização inválida.')
        else:
            if any(not 1<=u<v<=n for u,v in a) or len(set(a))!=len(a):raise ValueError('Arestas devem ser únicas, com 1 <= u < v <= N.')
            if task=='nearest_source' and (not b or len(set(b))!=len(b) or any(not 1<=x<=n for x in b)):raise ValueError('Fontes inválidas.')
        return True
    except (StopIteration,IndexError) as exc:raise ValueError('Entrada incompleta.') from exc


def inputs(p,seed=42):
    task=p['extended_task'];rng=random.Random(seed);cases=[]
    def add(text,strategy):cases.append(dict(input=text,strategy=strategy))
    if task in RANGE_TASKS:
        def array(a,ops,strategy):add(f'{len(a)} {len(ops)}\n'+ ' '.join(map(str,a))+'\n'+''.join(' '.join(map(str,o))+'\n' for o in ops),strategy)
        for n in range(1,4):
            for a in product((0,1,3),repeat=n):
                queries=[(2,l,r) for l in range(1,n+1) for r in range(l,n+1)]
                updates=[(1,1,n,2),(1,n,n,10**9)] if task=='range_add_sum' else [(1,1,10**9),(1,n,0)]
                ops=list(queries)
                for u in updates:ops.extend([u,*queries])
                array(a,ops,'small_exhaustive')
        for n in (7,31,97):
            a=[rng.choice((0,1,10**9)) for _ in range(n)];ops=[]
            for _ in range(60):
                l=rng.randint(1,n);r=rng.randint(l,n)
                ops.extend([(1,l,r,rng.choice((0,2,10**9))) if task=='range_add_sum' else (1,l,rng.choice((0,2,10**9))),(2,l,r)])
            array(a,ops,'random_extreme')
        n=p['constraints']['n_max'];ops=[]
        for i in range(15000):ops.extend([(1,1,n,10**9) if task=='range_add_sum' else (1,i%n+1,i%11),(2,1,n)])
        array([10**9]*n,ops,'tle_inducing')
    else:
        def graph(n,edges,strategy,sources=None):
            text=f'{n} {len(edges)}\n'+''.join(f'{u} {v}\n' for u,v in edges)
            if task=='nearest_source':
                sources=sources or [1];text+=str(len(sources))+'\n'+' '.join(map(str,sources))+'\n'
            add(text,strategy)
        for n in range(1,5):
            edges=list(combinations(range(1,n+1),2))
            for mask in range(1<<len(edges)):graph(n,[e for i,e in enumerate(edges) if mask>>i&1],'small_exhaustive',[1,n] if n>1 else [1])
        for _ in range(3):
            n=17;edges=[(u,v) for u,v in combinations(range(1,n+1),2) if rng.random()<.1]
            graph(n,edges,'random_extreme',[3,8])
        n=p['constraints']['n_max'];graph(n,[(i,i+1) for i in range(1,n)],'tle_inducing',[1,n])
        graph(5,[(1,2),(2,3),(1,3)],'random_extreme',[4])
    return cases


def oracle(task,text,small=False):
    n,a,b=parse(task,text)
    if task in RANGE_TASKS:
        # Blocks + lazy offsets, independent of the C++ segment-tree implementation.
        size=max(1,math.isqrt(n));count=(n+size-1)//size;lazy=[0]*count;aggregates=[0]*count
        def combine(vals):
            if task=='range_max':return max(vals,default=0)
            if task=='range_xor':
                value=0
                for x in vals:value^=x
                return value
            return sum(vals)
        def rebuild(k):aggregates[k]=combine(a[k*size:min(n,(k+1)*size)])
        for k in range(count):rebuild(k)
        out=[]
        for op in b:
            t,l,r=op[:3];l-=1
            if t==1 and task!='range_add_sum':a[l]=r;rebuild(l//size);continue
            r-=1;answer=0
            for k in range(l//size,r//size+1):
                start=k*size;end=min(n,(k+1)*size);lo=max(l,start);hi=min(r+1,end)
                if t==1:
                    if lo==start and hi==end:lazy[k]+=op[3]
                    else:
                        for i in range(lo,hi):a[i]+=op[3]
                        rebuild(k)
                else:
                    value=aggregates[k]+lazy[k]*(end-start) if lo==start and hi==end else combine([a[i]+lazy[k] for i in range(lo,hi)])
                    if task=='range_max':answer=max(answer,value)
                    elif task=='range_xor':answer^=value
                    else:answer+=value
            if t==2:out.append(str(answer))
        return '\n'.join(out)+'\n'
    edges=a;sources=b
    if task in ('components','cycle'):
        parent=list(range(n));components=n
        def find(x):
            while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
            return x
        cycle=False
        for u,v in edges:
            x,y=find(u-1),find(v-1)
            if x==y:cycle=True
            else:parent[x]=y;components-=1
        return (str(components) if task=='components' else 'YES' if cycle else 'NO')+'\n'
    if task=='bipartite' and small:
        answer=any(all(colors[u-1]!=colors[v-1] for u,v in edges) for colors in product((0,1),repeat=n))
        return ('YES' if answer else 'NO')+'\n'
    graph=[[] for _ in range(n)]
    for u,v in edges:graph[u-1].append(v-1);graph[v-1].append(u-1)
    if task=='bipartite':
        colors=[-1]*n
        for root in range(n):
            if colors[root]>=0:continue
            colors[root]=0;queue=deque([root])
            while queue:
                u=queue.popleft()
                for v in graph[u]:
                    if colors[v]==colors[u]:return 'NO\n'
                    if colors[v]<0:colors[v]=1-colors[u];queue.append(v)
        return 'YES\n'
    if small:
        dist=[[0 if i==j else n+1 for j in range(n)] for i in range(n)]
        for u,v in edges:dist[u-1][v-1]=dist[v-1][u-1]=1
        for k in range(n):
            for i in range(n):
                for j in range(n):dist[i][j]=min(dist[i][j],dist[i][k]+dist[k][j])
        result=[min(dist[s-1][v] for s in sources) for v in range(n)]
        return ' '.join(str(d if d<=n else -1) for d in result)+'\n'
    dist=[-1]*n;queue=deque(s-1 for s in sources)
    for s in sources:dist[s-1]=0
    while queue:
        u=queue.popleft()
        for v in graph[u]:
            if dist[v]<0:dist[v]=dist[u]+1;queue.append(v)
    return ' '.join(map(str,dist))+'\n'
