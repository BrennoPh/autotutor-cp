"""Explainable trio scoring. Exact small searches; bounded heuristic for large classes."""
from functools import lru_cache
from itertools import combinations
import math
import random

STRATEGIES=['Complementaridade','Equilíbrio entre trios','Níveis semelhantes']
TOPICS=['Fundamentos','Estruturas de Dados','Prefix Sum','Busca Binária','Matemática','Guloso','DP','Grafos','Árvores']


def team_metrics(team):
    coverage=sum(max(float(m.get('skills',{}).get(t,0)) for m in team) for t in TOPICS)/len(TOPICS)
    strengths=[sum(float(m.get('skills',{}).get(t,0)) for t in TOPICS)/len(TOPICS) for m in team]
    solved=[set(m.get('local_solved',[]))|set(m.get('verified_external',[])) for m in team]
    union=set().union(*solved)
    overlap=sum(len(a & b)/max(1,len(a | b)) for a,b in combinations(solved,2))/3
    unique=min(1,math.log1p(len(union))/math.log(31))
    mean=sum(strengths)/3
    spread=sum((s-mean)**2 for s in strengths)/3
    topics=sorted(TOPICS,key=lambda t:max(float(m.get('skills',{}).get(t,0)) for m in team),reverse=True)
    topics=[t for t in topics if any(m.get('skills',{}).get(t,0)>0 for m in team)][:3]
    return dict(coverage=coverage,mean_strength=mean,spread=spread,unique=unique,overlap=overlap,
                distinct_verified=len(union),topics=topics,evidence=sum(m.get('evidence',0) for m in team))


def score_team(team,strategy,target=0):
    m=team_metrics(team)
    if strategy=='Complementaridade':return .55*m['coverage']+.25*m['unique']+.2*m['mean_strength']-.1*m['overlap']
    if strategy=='Equilíbrio entre trios':return .4*m['coverage']+.2*m['mean_strength']-2*(m['mean_strength']-target)**2
    if strategy=='Níveis semelhantes':return .3*m['coverage']+.4*m['mean_strength']-2*m['spread']
    raise ValueError('Estratégia inválida.')


def form_trios(students,strategy='Complementaridade',mode='Turma inteira',seed=42):
    if strategy not in STRATEGIES or mode not in ('Turma inteira','Melhor trio'):raise ValueError('Critério de formação inválido.')
    if len(students)<3:raise ValueError('Selecione pelo menos três alunos.')
    if len(students)>120:raise ValueError('Selecione até 120 alunos por rodada de formação.')
    if len({s['id'] for s in students})!=len(students):raise ValueError('Há alunos repetidos na seleção.')
    students=sorted(students,key=lambda s:s['id'])
    n=len(students);target=sum(sum(s.get('skills',{}).get(t,0) for t in TOPICS)/len(TOPICS) for s in students)/n
    rng=random.Random(seed)
    @lru_cache(maxsize=100_000)
    def score(indices):return score_team([students[i] for i in indices],strategy,target)
    if mode=='Melhor trio':
        if n<=60:
            candidates=combinations(range(n),3);method='Busca exata de todos os trios candidatos'
        else:
            candidates=sorted({tuple(sorted(rng.sample(range(n),3))) for _ in range(12000)})
            method='Busca heurística em até 12.000 trios candidatos'
        best=max(candidates,key=lambda t:(score(tuple(t)),tuple(-i for i in t)))
        teams=[list(best)];waiting=[i for i in range(n) if i not in best]
    elif n<=12:
        @lru_cache(maxsize=None)
        def search(mask,free):
            if mask==0:return 0,(),()
            values=[i for i in range(n) if mask>>i&1]
            first=values[0];options=[]
            if free:
                value,groups,waiting=search(mask^(1<<first),free-1)
                options.append((value,groups,(first,)+waiting))
            if len(values)>=3:
                for a,b in combinations(values[1:],2):
                    triple=(first,a,b);rest=mask
                    for i in triple:rest^=1<<i
                    value,groups,waiting=search(rest,free)
                    options.append((score(triple)+value,(triple,)+groups,waiting))
            return max(options,key=lambda result:result[0])
        _,groups,unused=search((1<<n)-1,n%3)
        teams=[list(t) for t in groups];waiting=list(unused)
        method='Partição exata para a pontuação definida (até 12 alunos)'
    else:
        # Greedy multi-start plus swaps; no global-optimum claim for the partition problem.
        best=None;best_score=-float('inf')
        for restart in range(10):
            remaining=list(range(n));rng.shuffle(remaining);groups=[]
            while len(remaining)>=3:
                first=remaining.pop(0)
                pool=remaining[:24]
                pair=max(combinations(pool,2),key=lambda ab:score(tuple(sorted((first,*ab)))))
                group=sorted((first,*pair));groups.append(group)
                for i in pair:remaining.remove(i)
            value=sum(score(tuple(t)) for t in groups)
            if value>best_score:best_score=value;best=([list(t) for t in groups],list(remaining))
        teams,waiting=best
        for _ in range(2):
            for a,b in combinations(range(len(teams)),2):
                old=score(tuple(sorted(teams[a])))+score(tuple(sorted(teams[b])))
                best_swap=None
                for i in range(3):
                    for j in range(3):
                        ta,tb=teams[a][:],teams[b][:];ta[i],tb[j]=tb[j],ta[i]
                        value=score(tuple(sorted(ta)))+score(tuple(sorted(tb)))
                        if value>old+1e-12:old=value;best_swap=(ta,tb)
                if best_swap:teams[a],teams[b]=best_swap
        method='Heurística determinística: 10 partidas e duas rodadas de trocas; sem garantia de ótimo global'
    details=[]
    for indices in teams:
        members=[students[i] for i in indices];metrics=team_metrics(members)
        reason='Tópicos com evidência: '+(', '.join(metrics['topics']) or 'nenhum ainda')+'. '
        reason+=f'{metrics["distinct_verified"]} problemas locais ou externos confirmados distintos no conjunto. '
        if not metrics['evidence']:reason+='Sem histórico suficiente: a distribuição não representa uma avaliação de habilidade.'
        details.append(dict(members=[m['id'] for m in members],names=[m['name'] for m in members],score=round(score(tuple(sorted(indices))),5),reason=reason,metrics=metrics))
    return dict(teams=[[students[i]['id'] for i in t] for t in teams],waiting=[students[i]['id'] for i in waiting],
                details=details,strategy=strategy,method=method,seed=seed,
                note='Pontuação de planejamento baseada em evidências limitadas, não previsão de resultado em competição. Conclusões autodeclaradas têm peso reduzido.')
