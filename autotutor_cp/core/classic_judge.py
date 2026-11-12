"""Own deterministic suites and independent Python oracles for the local CSES pack.
No official judge tests are downloaded. Small cases use enumeration where practical.
"""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations, product, groupby, accumulate
from bisect import bisect_left
import math
import random

MOD=1000000007
ARRAYS={'increasing','distinct','maxsub','sticks','missingcoin','ferris','subsum','xor','rmq'}
COINS={'mincoins','coins1','coins2'}


def validate_classic(p,text):
    task=p['local_task'];parts=text.split()
    if not parts:raise ValueError('Entrada vazia.')
    if task=='repetitions':
        if len(parts)!=1 or not 1<=len(parts[0])<=1000000 or set(parts[0])-set('ACGT'):raise ValueError('DNA inválido.')
        return True
    if task in ('grid','rooms'):
        n=int(parts[0]);m=n if task=='grid' else int(parts[1]);start=1 if task=='grid' else 2
        if not 1<=n<=1000 or not 1<=m<=1000 or len(parts)!=start+n:raise ValueError('Dimensão inválida.')
        alphabet=set('.*' if task=='grid' else '.#')
        if any(len(row)!=m or set(row)-alphabet for row in parts[start:]):raise ValueError('Grade inválida.')
        return True
    v=list(map(int,parts));n=v[0]
    def bounded(values,low,high):
        if any(x<low or x>high for x in values):raise ValueError('Valor fora dos limites.')
    if task in ('bits','zeros','dice','digits'):
        if len(v)!=1 or not 1<=n<=(10**9 if task=='zeros' else 1000000):raise ValueError('N inválido.')
    elif task=='piles':
        if not 1<=n<=100000 or len(v)!=1+2*n:raise ValueError('Casos inválidos.')
        bounded(v[1:],0,10**9)
    elif task=='missing':
        if not 2<=n<=200000 or len(v)!=n or len(set(v[1:]))!=n-1:raise ValueError('Lista incompleta inválida.')
        bounded(v[1:],1,n)
    elif task in ARRAYS:
        if not 1<=n<=200000:raise ValueError('N inválido.')
        start=2 if task in ('ferris','subsum','xor','rmq') else 1
        a=v[start:start+n]
        if len(a)!=n:raise ValueError('Vetor incompleto.')
        bounded(a,-10**9 if task in ('maxsub','subsum') else 1,10**9)
        if task=='ferris':bounded([v[1]],1,10**9);bounded(a,1,v[1])
        if task=='subsum':bounded([v[1]],-10**9,10**9)
        if task in ('xor','rmq'):
            q=v[1]
            if not 1<=q<=200000 or len(v)!=2+n+2*q:raise ValueError('Consultas inválidas.')
            for i in range(2+n,len(v),2):
                if not 1<=v[i]<=v[i+1]<=n:raise ValueError('Intervalo inválido.')
        elif len(v)!=start+n:raise ValueError('Tokens excedentes.')
    elif task=='movies':
        if not 1<=n<=200000 or len(v)!=1+2*n:raise ValueError('Filmes inválidos.')
        if any(not 1<=v[i]<v[i+1]<=10**9 for i in range(1,len(v),2)):raise ValueError('Intervalo inválido.')
    elif task=='apartments':
        if len(v)<3:raise ValueError('Cabeçalho inválido.')
        m,k=v[1:3]
        if not 1<=n<=200000 or not 1<=m<=200000 or not 0<=k<=10**9 or len(v)!=3+n+m:raise ValueError('Apartamentos inválidos.')
        bounded(v[3:],1,10**9)
    elif task in COINS:
        if not 1<=n<=100 or len(v)!=n+2 or not 1<=v[1]<=1000000 or len(set(v[2:]))!=n:raise ValueError('Moedas inválidas.')
        bounded(v[2:],1,1000000)
    elif task=='books':
        if not 1<=n<=1000 or len(v)!=2+2*n or not 1<=v[1]<=100000:raise ValueError('Livros inválidos.')
        bounded(v[2:],1,1000)
    else:raise ValueError('Tarefa desconhecida.')
    return True


def classic_inputs(p,seed=42):
    task=p['local_task'];rng=random.Random(seed);cases=[]
    def add(text,strategy='small_exhaustive'):cases.append({'input':text,'strategy':strategy})
    def arr(a,strategy='small_exhaustive'):
        header=str(len(a))
        if task=='ferris':header+=' '+str(min(10**9,max(a)+min(a)))
        if task=='subsum':header+=' 0'
        if task in ('xor','rmq'):
            qs=([(l,r) for l in range(1,len(a)+1) for r in range(l,len(a)+1)] if len(a)<=3 else [(1,len(a)),(1,1),(len(a),len(a))]+[(1,rng.randint(1,len(a))) for _ in range(12)])
            if strategy=='tle_inducing':qs=[(1,len(a))]*199998+qs[:2]
            header+=' '+str(len(qs))
        text=header+'\n'+' '.join(map(str,a))+'\n'
        if task in ('xor','rmq'):text+=''.join(f'{l} {r}\n' for l,r in qs)
        add(text,strategy)
    if task in ARRAYS:
        alphabet=(-2,0,3) if task in ('maxsub','subsum') else (1,2,4)
        for n in range(1,4):
            for a in product(alphabet,repeat=n):arr(a)
        if task=='subsum':
            for target in (-4,-1,1,3,10**9):add(f'5 {target}\n-2 1 3 -1 0\n')
            add('3 1000000000\n1000000000 1000000000 -1000000000\n','random_extreme')
        if task=='ferris':
            add('4 10\n5 5 5 5\n');add('3 9\n5 5 5\n')
        for a in ([1]*9,list(range(10,0,-1)),[10**9]*9):arr(a,'random_extreme')
        for _ in range(5):arr([rng.choice(alphabet) for _ in range(31)],'random_extreme')
        stress=([0]*200000 if task=='subsum' else [-10**9]*200000 if task=='maxsub' else [10**9 if i%2 else 1 for i in range(200000)])
        arr(stress,'tle_inducing')
    elif task=='missing':
        for n in range(2,7):
            for missing in range(1,n+1):add(str(n)+'\n'+' '.join(str(i) for i in range(1,n+1) if i!=missing)+'\n')
        a=list(range(1,101));a.remove(51);rng.shuffle(a);add('101\n'+' '.join(map(str,a+[101]))+'\n','random_extreme')
        add('200000\n'+' '.join(map(str,range(1,200000)))+'\n','tle_inducing')
    elif task=='repetitions':
        for n in range(1,4):
            for a in product('ACG',repeat=n):add(''.join(a)+'\n')
        add('AT'*100+'TTTT\n','random_extreme');add('G'*1000000+'\n','tle_inducing')
    elif task in ('bits','zeros','dice','digits'):
        for n in range(1,13):add(str(n)+'\n')
        for n in (25,99,100,999):add(str(n)+'\n','random_extreme')
        add(str(10**9 if task=='zeros' else 1000000)+'\n','tle_inducing')
    elif task=='piles':
        for a in range(9):add(f'9\n'+''.join(f'{a} {b}\n' for b in range(9)))
        add('4\n0 1000000000\n999999999 999999999\n4 2\n1 1\n','random_extreme')
        add('100000\n'+'1000000000 999999998\n'*100000,'tle_inducing')
    elif task=='movies':
        for n in range(1,4):
            for pairs in combinations([(1,2),(1,4),(2,3),(3,4),(2,5)],n):add(str(n)+'\n'+''.join(f'{a} {b}\n' for a,b in pairs))
        add('4\n1 100\n2 3\n3 4\n4 5\n','random_extreme')
        add('200000\n'+''.join(f'{i} {i+1}\n' for i in range(200000,0,-1)),'tle_inducing')
    elif task=='apartments':
        for a in product((1,3,5),repeat=2):
            for k in (0,1):add(f'2 3 {k}\n'+ ' '.join(map(str,a))+'\n2 3 5\n')
        add('1 1 1000000000\n1\n1000000000\n','random_extreme')
        add('200000 200000 0\n'+'1 '*200000+'\n'+'1 '*200000+'\n','tle_inducing')
    elif task in COINS:
        for coins in [(1,),(2,),(1,2),(2,3),(1,3,4)]:
            for target in range(1,9):add(f'{len(coins)} {target}\n'+' '.join(map(str,coins))+'\n')
        add('2 17\n6 9\n','random_extreme')
        add('3 1000000\n7 11 19\n','tle_inducing')
    elif task in ('grid','rooms'):
        blocked='*' if task=='grid' else '#'
        for mask in range(16):
            rows=[''.join(blocked if mask>>(r*2+c)&1 else '.' for c in range(2)) for r in range(2)]
            add(('2\n' if task=='grid' else '2 2\n')+'\n'.join(rows)+'\n')
        add(('1\n' if task=='grid' else '1 1\n')+'.\n','random_extreme')
        add(('1000\n' if task=='grid' else '1000 1000\n')+('\n'.join(['.'*1000]*1000))+'\n','tle_inducing')
    elif task=='books':
        for prices in product((1,3),repeat=3):
            for budget in (1,4,7):add(f'3 {budget}\n'+ ' '.join(map(str,prices))+'\n2 5 7\n')
        add('1 10\n3\n5\n','random_extreme')
        add('1000 100000\n'+'1000 '*1000+'\n'+'1000 '*1000+'\n','tle_inducing')
    return cases


def oracle(task,text,small=False):
    """Independent small brute force; scalable cross-checks on the larger cases."""
    p=text.split()
    if task=='repetitions':return str(max(len(list(g)) for _,g in groupby(p[0])))+'\n'
    if task in ('grid','rooms'):
        n=int(p[0]);m=n if task=='grid' else int(p[1]);g=p[1 if task=='grid' else 2:]
        if task=='grid':
            if small:
                def visit(r,c):
                    if r>=n or c>=n or g[r][c]=='*':return 0
                    if r==n-1 and c==n-1:return 1
                    return visit(r+1,c)+visit(r,c+1)
                ans=visit(0,0)
            else:
                dp=[[0]*n for _ in range(n)];dp[0][0]=int(g[0][0]=='.')
                for r in range(n):
                    for c in range(n):
                        if (r or c) and g[r][c]=='.':dp[r][c]=((dp[r-1][c] if r else 0)+(dp[r][c-1] if c else 0))%MOD
                ans=dp[-1][-1]
        else:
            # Union-find scan, independent from C++ flood fill.
            parent=list(range(n*m));ans=0
            def root(x):
                while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
                return x
            for r in range(n):
                for c in range(m):
                    if g[r][c]!='.':continue
                    ans+=1
                    for a,b in ((r-1,c),(r,c-1)):
                        if a>=0 and b>=0 and g[a][b]=='.':
                            x,y=root(r*m+c),root(a*m+b)
                            if x!=y:parent[x]=y;ans-=1
        return str(ans)+'\n'
    v=list(map(int,p));n=v[0]
    if task=='missing':ans=next(i for i in range(1,n+1) if i not in set(v[1:])) if small else n*(n+1)//2-sum(v[1:])
    elif task=='bits':ans=len(list(product((0,1),repeat=n))) if small else pow(2,n,MOD)
    elif task=='zeros':
        if small:ans=len(str(math.factorial(n)))-len(str(math.factorial(n)).rstrip('0'))
        else:
            ans=0
            while n:n//=5;ans+=n
    elif task=='piles':
        @lru_cache(None)
        def possible(a,b):
            if min(a,b)<0:return False
            if a==b==0:return True
            return possible(a-1,b-2) or possible(a-2,b-1)
        def check(a,b):
            if small:return possible(a,b)
            x,y=2*a-b,2*b-a
            return min(x,y)>=0 and x%3==y%3==0
        return ''.join(('YES' if check(a,b) else 'NO')+'\n' for a,b in zip(v[1::2],v[2::2]))
    elif task in ARRAYS:
        start=2 if task in ('ferris','subsum','xor','rmq') else 1;a=v[start:start+n]
        if task=='increasing':
            if small:ans=min(sum(b[i]-a[i] for i in range(n)) for b in product(range(min(a),max(a)+1),repeat=n) if all(b[i]>=a[i] for i in range(n)) and all(b[i]<=b[i+1] for i in range(n-1)))
            else:ans=sum(mx-x for mx,x in zip(accumulate(a,max),a))
        elif task=='distinct':ans=sum(x not in a[:i] for i,x in enumerate(a)) if small else len(set(a))
        elif task=='maxsub':
            if small:ans=max(sum(a[l:r]) for l in range(n) for r in range(l+1,n+1))
            else:
                low=0;total=0;ans=-10**30
                for x in a:total+=x;ans=max(ans,total-low);low=min(low,total)
        elif task=='sticks':
            b=range(min(a),max(a)+1) if small else [sorted(a)[(n-1)//2]]
            ans=min(sum(abs(x-y) for x in a) for y in b)
        elif task=='missingcoin':
            if small:
                sums={0}
                for x in a:sums|={s+x for s in sums}
                ans=next(x for x in range(1,sum(a)+2) if x not in sums)
            else:
                ans=1
                for x in sorted(a):
                    if x>ans:break
                    ans+=x
        elif task=='ferris':
            capacity=v[1]
            if small:
                @lru_cache(None)
                def solve(mask):
                    if not mask:return 0
                    i=(mask&-mask).bit_length()-1;rest=mask^(1<<i);best=1+solve(rest)
                    for j in range(i+1,n):
                        if rest>>j&1 and a[i]+a[j]<=capacity:best=min(best,1+solve(rest^(1<<j)))
                    return best
                ans=solve((1<<n)-1)
            else:
                a.sort();left=0;right=n-1;ans=0
                while left<=right:
                    ans+=1
                    if left<right and a[left]+a[right]<=capacity:left+=1
                    right-=1
        elif task=='subsum':
            target=v[1]
            if small:ans=sum(sum(a[l:r])==target for l in range(n) for r in range(l+1,n+1))
            else:
                # Group all prefix positions, count ordered index pairs using binary search.
                groups={}
                for i,s in enumerate(accumulate(a,initial=0)):groups.setdefault(s,[]).append(i)
                ans=sum(sum(bisect_left(groups.get(s-target,[]),j) for j in js) for s,js in groups.items())
        else:
            queries=list(zip(v[start+n::2],v[start+n+1::2]));cache={}
            if task=='xor' and not small:prefix=list(accumulate(a,lambda x,y:x^y,initial=0))
            for l,r in queries:
                if (l,r) in cache:continue
                if task=='xor':
                    value=0
                    if small:
                        for x in a[l-1:r]:value^=x
                    else:value=prefix[r]^prefix[l-1]
                else:value=min(a[l-1:r])
                cache[l,r]=value
            return ''.join(str(cache[l,r])+'\n' for l,r in queries)
    elif task=='movies':
        pairs=list(zip(v[1::2],v[2::2]));ans=0
        if small:
            for mask in range(1<<n):
                chosen=sorted(pairs[i] for i in range(n) if mask>>i&1)
                if all(chosen[i][1]<=chosen[i+1][0] for i in range(len(chosen)-1)):ans=max(ans,len(chosen))
        else:
            last=0
            for l,r in sorted(pairs,key=lambda z:z[1]):
                if l>=last:ans+=1;last=r
    elif task=='apartments':
        m,k=v[1:3];a=v[3:3+n];b=v[3+n:]
        if small:
            @lru_cache(None)
            def assign(i,used):
                if i==n:return 0
                return max([assign(i+1,used)]+[1+assign(i+1,used|1<<j) for j in range(m) if not used>>j&1 and abs(a[i]-b[j])<=k])
            ans=assign(0,0)
        else:
            a.sort();b.sort();j=0;ans=0
            for x in a:
                while j<m and b[j]<x-k:j+=1
                if j<m and b[j]<=x+k:ans+=1;j+=1
    elif task in COINS or task=='dice':
        target=n if task=='dice' else v[1];coins=list(range(1,7)) if task=='dice' else v[2:]
        if small:
            @lru_cache(None)
            def solve(rem,index=0):
                if rem==0:return 0 if task=='mincoins' else 1
                if rem<0:return 10**9 if task=='mincoins' else 0
                if task=='mincoins':return 1+min(solve(rem-c) for c in coins)
                if task=='coins2':
                    if index==len(coins):return 0
                    return sum(solve(rem-k*coins[index],index+1) for k in range(rem//coins[index]+1))
                return sum(solve(rem-c) for c in coins if c<=rem)
            ans=solve(target)
            if task=='mincoins' and ans>=10**9:ans=-1
        else:
            d=[target+1 if task=='mincoins' else 0]*(target+1);d[0]=0 if task=='mincoins' else 1
            if task=='coins2':
                for c in coins:
                    for s in range(c,target+1):d[s]=(d[s]+d[s-c])%MOD
            else:
                for s in range(1,target+1):
                    values=[d[s-c] for c in coins if c<=s]
                    d[s]=(1+min(values,default=target+1)) if task=='mincoins' else sum(values)%MOD
            ans=d[target]
            if task=='mincoins' and ans>target:ans=-1
        if task!='mincoins':ans%=MOD
    elif task=='digits':
        if small:
            @lru_cache(None)
            def walk(x):return 0 if x==0 else 1+min(walk(x-int(c)) for c in str(x) if c!='0')
            ans=walk(n)
        else:
            d=[0]*(n+1)
            for x in range(1,n+1):d[x]=1+min(d[x-int(c)] for c in str(x) if c!='0')
            ans=d[n]
    elif task=='books':
        budget=v[1];prices=v[2:2+n];pages=v[2+n:]
        if small:ans=max(sum(pages[i] for i in range(n) if mask>>i&1) for mask in range(1<<n) if sum(prices[i] for i in range(n) if mask>>i&1)<=budget)
        else:
            d=[0]*(budget+1)
            for price,value in zip(prices,pages):
                previous=d[:]
                for money in range(price,budget+1):d[money]=max(previous[money],previous[money-price]+value)
            ans=d[budget]
    else:raise ValueError('Oráculo desconhecido.')
    return str(ans)+'\n'
