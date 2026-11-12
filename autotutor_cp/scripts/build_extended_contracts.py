"""Original problem contracts with independent Python oracles, not scraped statements."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
HEADER='#include <bits/stdc++.h>\nusing namespace std;\n'
POINT=HEADER+r'''
long long mergeValue(long long a,long long b){return MERGE;}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);
int n,q;cin>>n>>q;int size=1;while(size<n)size*=2;vector<long long> t(2*size,0);
for(int i=0;i<n;i++)cin>>t[size+i];for(int i=size-1;i;i--)t[i]=mergeValue(t[2*i],t[2*i+1]);
while(q--){int op,x;long long y;cin>>op>>x>>y;
if(op==1){int p=size+x-1;t[p]=y;while(p>1){p/=2;t[p]=mergeValue(t[2*p],t[2*p+1]);}}
else{int l=size+x-1,r=size+(int)y;long long ans=0;while(l<r){if(l&1)ans=mergeValue(ans,t[l++]);if(r&1)ans=mergeValue(ans,t[--r]);l/=2;r/=2;}cout<<ans<<'\n';}}
}
'''
LAZY=HEADER+r'''
vector<long long> t,lz,a;
void build(int p,int l,int r){if(l==r){t[p]=a[l];return;}int m=(l+r)/2;build(p*2,l,m);build(p*2+1,m+1,r);t[p]=t[p*2]+t[p*2+1];}
void apply(int p,int l,int r,long long x){t[p]+=x*(r-l+1);lz[p]+=x;}
void push(int p,int l,int r){if(l!=r&&lz[p]){int m=(l+r)/2;apply(p*2,l,m,lz[p]);apply(p*2+1,m+1,r,lz[p]);lz[p]=0;}}
void add(int p,int l,int r,int ql,int qr,long long x){if(qr<l||r<ql)return;if(ql<=l&&r<=qr){apply(p,l,r,x);return;}push(p,l,r);int m=(l+r)/2;add(p*2,l,m,ql,qr,x);add(p*2+1,m+1,r,ql,qr,x);t[p]=t[p*2]+t[p*2+1];}
long long query(int p,int l,int r,int ql,int qr){if(qr<l||r<ql)return 0;if(ql<=l&&r<=qr)return t[p];push(p,l,r);int m=(l+r)/2;return query(p*2,l,m,ql,qr)+query(p*2+1,m+1,r,ql,qr);}
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);int n,q;cin>>n>>q;a.resize(n+1);t.resize(4*n+4);lz.resize(4*n+4);for(int i=1;i<=n;i++)cin>>a[i];build(1,1,n);while(q--){int op,l,r;cin>>op>>l>>r;if(op==1){long long x;cin>>x;add(1,1,n,l,r,x);}else cout<<query(1,1,n,l,r)<<'\n';}}
'''
GRAPH=HEADER+r'''
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);int n,m;cin>>n>>m;vector<vector<int>>g(n);for(int i=0,u,v;i<m;i++){cin>>u>>v;--u;--v;g[u].push_back(v);g[v].push_back(u);}BODY}
'''
BODIES={
'components':r'''vector<int>seen(n);int count=0;for(int root=0;root<n;root++){if(seen[root])continue;count++;vector<int>s{root};seen[root]=1;while(!s.empty()){int u=s.back();s.pop_back();for(int v:g[u])if(!seen[v]){seen[v]=1;s.push_back(v);}}}cout<<count<<'\n';''',
'bipartite':r'''vector<int>color(n,-1);bool ok=true;for(int root=0;root<n;root++){if(color[root]>=0)continue;vector<int>s{root};color[root]=0;while(!s.empty()){int u=s.back();s.pop_back();for(int v:g[u]){if(color[v]<0){color[v]=1-color[u];s.push_back(v);}else if(color[v]==color[u])ok=false;}}}cout<<(ok?"YES":"NO")<<'\n';''',
'cycle':r'''vector<int>seen(n),parent(n,-1);bool cycle=false;for(int root=0;root<n;root++){if(seen[root])continue;vector<int>s{root};seen[root]=1;while(!s.empty()){int u=s.back();s.pop_back();for(int v:g[u]){if(!seen[v]){seen[v]=1;parent[v]=u;s.push_back(v);}else if(v!=parent[u])cycle=true;}}}cout<<(cycle?"YES":"NO")<<'\n';''',
'nearest_source':r'''int k;cin>>k;queue<int>q;vector<int>d(n,-1);while(k--){int s;cin>>s;--s;d[s]=0;q.push(s);}while(!q.empty()){int u=q.front();q.pop();for(int v:g[u])if(d[v]<0){d[v]=d[u]+1;q.push(v);}}for(int i=0;i<n;i++)cout<<d[i]<<(i+1==n?'\n':' ');'''}

def main():
    rows=[]
    titles={'range_sum':'Telemetria: somas com atualizações','range_max':'Telemetria: maior leitura no intervalo','range_xor':'Telemetria: paridade bit a bit','range_add_sum':'Bônus em lote: incrementos e somas','components':'Ilhas de comunicação','bipartite':'Duas equipes sem conflito','nearest_source':'Distância ao posto mais próximo','cycle':'Rotas com circuito'}
    objectives={'range_sum':'Atribuir um valor a uma posição e consultar a soma de um intervalo.','range_max':'Atribuir um valor a uma posição e consultar o máximo de um intervalo.','range_xor':'Atribuir um valor a uma posição e consultar o XOR de um intervalo.','range_add_sum':'Adicionar um valor a todas as posições de um intervalo e consultar somas de intervalos.','components':'Contar componentes conexos, incluindo vértices isolados, em grafo não direcionado.','bipartite':'Decidir se um grafo não direcionado permite dividir os vértices em dois grupos sem arestas internas.','nearest_source':'Calcular para cada vértice a menor quantidade de arestas até qualquer fonte indicada.','cycle':'Decidir se um grafo simples não direcionado contém um ciclo em qualquer componente.'}
    for task,title in titles.items():
        ranges=task.startswith('range_');lazy=task=='range_add_sum';topic='Segment Tree' if ranges else 'Grafos'
        if ranges:
            statement=objectives[task]+'\n\n## Entrada\nN Q, seguidos por N inteiros não negativos. Em seguida Q operações. '
            statement+=('`1 L R X` adiciona X ao intervalo fechado [L,R]. ' if lazy else '`1 K X` substitui o valor na posição K por X. ')
            statement+='`2 L R` consulta o intervalo fechado [L,R]. Índices começam em 1.\n\n## Saída\nUma resposta por consulta, na ordem de entrada.\n\n## Restrições\n1 ≤ N,Q ≤ 30000; valores iniciais e X entre 0 e 10^9. 1 ≤ L ≤ R ≤ N. Use inteiros de 64 bits para somas.\nTempo: 2 s. Memória: 256 MB.'
            code=LAZY if lazy else POINT.replace('MERGE',{'range_sum':'a+b','range_max':'max(a,b)','range_xor':'a^b'}[task])
            example='3 3\n2 4 1\n2 1 3\n'+('1 1 2 3' if lazy else '1 2 7')+'\n2 '+('1 3' if lazy else '2 3')+'\n'
            expected={'range_sum':'7\n8\n','range_max':'4\n7\n','range_xor':'7\n6\n','range_add_sum':'7\n13\n'}[task];complexity='O((N+Q) log N)'
        else:
            statement=objectives[task]+'\n\n## Entrada\nN M, seguidos por M linhas U V, com 1 ≤ U < V ≤ N. Não existem arestas repetidas.'
            if task=='nearest_source':statement+=' Depois das arestas, K e uma linha com K fontes distintas entre 1 e N.'
            statement+='\n\n## Saída\n'+{'components':'Número de componentes.','bipartite':'YES se a divisão existe, NO caso contrário.','nearest_source':'N distâncias, na ordem dos vértices; -1 para vértices inacessíveis.','cycle':'YES se existe um ciclo, NO caso contrário.'}[task]
            statement+='\n\n## Restrições\n1 ≤ N ≤ 30000; 0 ≤ M ≤ 30000. Para múltiplas fontes, 1 ≤ K ≤ N.\nTempo: 2 s. Memória: 256 MB.'
            code=GRAPH.replace('BODY',BODIES[task]);example='4 2\n1 2\n2 3\n'+('2\n1 4\n' if task=='nearest_source' else '')
            expected={'components':'2\n','bipartite':'YES\n','cycle':'NO\n','nearest_source':'0 1 2 0\n'}[task];complexity='O(N+M)'
        rows.append(dict(id='extended_'+task,title=title,topic=topic,difficulty='Avançado' if lazy else 'Intermediário',family='segtree' if ranges else 'graph',extended_task=task,
            tags=[topic,task.replace('_',' ')],statement=statement,math_essence=objectives[task],core_concepts=[topic,'Lazy propagation' if lazy else 'BFS' if task=='nearest_source' else 'DFS e BFS' if not ranges else task.replace('_',' ')],approach_summary=objectives[task]+' Meta: '+complexity,complexity=complexity,
            std_cpp=code,brute_cpp='',constraints={'n_max':30000,'q_max':30000},time_limit_sec=2.0,memory_limit_mb=256,examples=[{'input':example,'expected_output':expected}],external=False,
            attribution={'statement':'Contrato autoral do AutoTutor','tests':'Oráculo Python independente; testes próprios.'}))
    (ROOT/'data/extended_contracts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print('Contratos criados:',len(rows))

if __name__=='__main__':main()
