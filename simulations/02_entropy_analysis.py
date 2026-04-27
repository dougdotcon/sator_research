"""
EXP-02: Análise de Entropia de Shannon do Quadrado de Sator
============================================================
Mede H(X) em 4 direções de leitura e compara com texto aleatório.
Gera GIF animado mostrando como a simetria reduz a entropia.
Output: figures/entropy_maps/ + results/entropy/02_entropy_data.csv
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation, PillowWriter
import csv, os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures", "entropy_maps")
RES_DIR = os.path.join(BASE, "results", "entropy")
ANI_DIR = os.path.join(BASE, "figures", "animations")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)
os.makedirs(ANI_DIR, exist_ok=True)

SATOR = ["SATOR","AREPO","TENET","OPERA","ROTAS"]

def words_to_matrix(words):
    return np.array([list(w.upper()) for w in words])

def shannon_entropy(symbols):
    """H(X) = -sum p_i log2 p_i"""
    if len(symbols)==0: return 0.0
    counts=Counter(symbols)
    N=len(symbols)
    return -sum((c/N)*np.log2(c/N) for c in counts.values() if c>0)

def positional_entropy(M):
    """Calcula entropia em cada posição considerando a redundância das simetrias."""
    n=len(M)
    pos_entropy=np.zeros((n,n))
    # Para cada posição, quais outras posições têm o mesmo valor por simetria?
    for i in range(n):
        for j in range(n):
            # Conjunto de posições que devem ter o mesmo valor
            orbit={(i,j),(j,i),(n-1-i,n-1-j),(n-1-j,n-1-i)}
            symbols=[M[r][c] for r,c in orbit]
            pos_entropy[i][j]=shannon_entropy(symbols)
    return pos_entropy

def directional_entropy(M):
    """Calcula entropia em cada uma das 4 direções de leitura."""
    n=len(M)
    # LR: esquerda → direita (linhas normais)
    lr=[''.join(M[i]) for i in range(n)]
    # RL: direita → esquerda (linhas invertidas)
    rl=[''.join(M[i][::-1]) for i in range(n)]
    # TB: cima → baixo (colunas normais)
    tb=[''.join(M[:,j]) for j in range(n)]
    # BT: baixo → cima (colunas invertidas)
    bt=[''.join(M[:,j][::-1]) for j in range(n)]

    results={}
    for name, seqs in [('LR→',lr),('←RL',rl),('↓TB',tb),('↑BT',bt)]:
        all_chars=''.join(seqs)
        results[name]=shannon_entropy(list(all_chars))
    return results

def global_sator_entropy(M):
    """Entropia global de toda a matriz."""
    return shannon_entropy(list(''.join(''.join(row) for row in M)))

def random_matrix_entropy(n=5, trials=1000, seed=42):
    """Entropia média de matrizes aleatórias de letras."""
    rng=np.random.RandomState(seed)
    alphabet=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    entropies=[]
    for _ in range(trials):
        M=rng.choice(alphabet,size=(n,n))
        h=shannon_entropy(list(''.join(''.join(r) for r in M)))
        entropies.append(h)
    return np.mean(entropies), np.std(entropies)

def conditional_entropy_under_symmetry(M):
    """
    H(M_ij | simetrias) — entropia condicional de uma posição
    dado que conhecemos as simetrias da matriz.
    Para o Sator, deve ser ≈ 0 pois cada posição determina as outras.
    """
    n=len(M)
    orbit_map={}
    for i in range(n):
        for j in range(n):
            orbit=frozenset([(i,j),(j,i),(n-1-i,n-1-j),(n-1-j,n-1-i)])
            orbit_map[(i,j)]=orbit
    # Entropia condicional: dado os valores da órbita, qual a incerteza?
    cond_entropy_map=np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            orbit=orbit_map[(i,j)]
            vals=[M[r][c] for r,c in orbit]
            # Se todos iguais (caso Sator), entropia é 0
            if len(set(vals))==1:
                cond_entropy_map[i][j]=0.0
            else:
                cond_entropy_map[i][j]=shannon_entropy(vals)
    return cond_entropy_map

# ─── Visualizações ────────────────────────────────────────────────────────────

def plot_entropy_heatmap(M, save_path):
    """Heatmap de entropia posicional vs texto aleatório."""
    ent_sator=positional_entropy(M)
    cond_sator=conditional_entropy_under_symmetry(M)
    rand_mean,rand_std=random_matrix_entropy()
    dir_ent=directional_entropy(M)
    glob_ent=global_sator_entropy(M)

    fig,axes=plt.subplots(1,3,figsize=(18,6))
    fig.patch.set_facecolor('#0d1117')

    cmap='plasma'

    # 1. Entropia posicional naive
    ax=axes[0]
    ax.set_facecolor('#161b22')
    im=ax.imshow(ent_sator,cmap=cmap,vmin=0,vmax=3)
    ax.set_title('Entropia Posicional Naive\n$H(M_{ij})$ por posição',
                 color='white',fontsize=11,fontweight='bold')
    for i in range(5):
        for j in range(5):
            ax.text(j,i,f'{ent_sator[i,j]:.2f}\n{SATOR[i][j]}',
                    ha='center',va='center',fontsize=9,
                    color='white' if ent_sator[i,j]<2 else '#0d1117',fontweight='bold')
    plt.colorbar(im,ax=ax,label='bits')
    ax.set_xticks([]); ax.set_yticks([])

    # 2. Entropia condicional (dada as simetrias)
    ax2=axes[1]
    ax2.set_facecolor('#161b22')
    im2=ax2.imshow(cond_sator,cmap=cmap,vmin=0,vmax=3)
    ax2.set_title('Entropia Condicional\n$H(M_{ij}|\\text{simetrias})$',
                  color='white',fontsize=11,fontweight='bold')
    for i in range(5):
        for j in range(5):
            ax2.text(j,i,f'{cond_sator[i,j]:.2f}\n{SATOR[i][j]}',
                     ha='center',va='center',fontsize=9,
                     color='white',fontweight='bold')
    plt.colorbar(im2,ax=ax2,label='bits')
    ax2.set_xticks([]); ax2.set_yticks([])
    ax2.text(2,-0.8,'→ Entropia condicional ≈ 0 para posições simétricas',
             ha='center',color='#4ECDC4',fontsize=9)

    # 3. Comparação direcional e global
    ax3=axes[2]
    ax3.set_facecolor('#161b22')
    ax3.axis('off')
    ax3.set_title('Análise Direcional de Entropia',color='white',fontsize=11,fontweight='bold')

    # Bar chart emulado com texto
    dirs=list(dir_ent.keys())
    vals=[dir_ent[d] for d in dirs]

    ypos=np.linspace(0.85,0.45,4)
    for yp,d,v in zip(ypos,dirs,vals):
        bar_w=v/5.0
        ax3.barh(yp,bar_w,height=0.08,color='#45B7D1',
                 transform=ax3.transAxes,left=0.1)
        ax3.text(0.06,yp,d,transform=ax3.transAxes,
                 color='white',fontsize=12,va='center',fontweight='bold')
        ax3.text(0.14+bar_w,yp,f'{v:.4f} bits',transform=ax3.transAxes,
                 color='#4ECDC4',fontsize=10,va='center')

    diff=max(vals)-min(vals)
    ax3.text(0.5,0.3,f'Δ direcional = {diff:.6f} bits',transform=ax3.transAxes,
             color='#FFEAA7',fontsize=11,ha='center',fontweight='bold')
    ax3.text(0.5,0.22,f'H(Sator global) = {glob_ent:.4f} bits',transform=ax3.transAxes,
             color='#FF6B6B',fontsize=11,ha='center')
    ax3.text(0.5,0.14,f'H(aleatório) = {rand_mean:.4f} ± {rand_std:.4f}',transform=ax3.transAxes,
             color='#8b949e',fontsize=10,ha='center')
    ax3.text(0.5,0.06,f'Redução vs aleatório: {rand_mean-glob_ent:.4f} bits',transform=ax3.transAxes,
             color='#96CEB4',fontsize=10,ha='center')

    plt.suptitle('EXP-02 — Análise de Entropia de Shannon | Quadrado de Sator',
                 color='white',fontsize=14,fontweight='bold',y=1.01)
    fig.text(0.5,-0.02,'Programa de Pesquisa Sator | Douglas H. M. Fulber | 2026',
             ha='center',color='#8b949e',fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path,dpi=150,bbox_inches='tight',facecolor='#0d1117')
    plt.close(); print(f"✓ {save_path}")
    return dir_ent, glob_ent, rand_mean, rand_std

def create_entropy_gif(M, save_path):
    """
    GIF animado mostrando como a entropia cai quando revelamos as simetrias.
    Quadro 0: Matriz random (alta entropia)
    Quadros 1-3: Aplicando simetrias progressivamente
    Quadro 4: Sator perfeito (entropia condicional ≈ 0)
    """
    fig,ax=plt.subplots(figsize=(8,6))
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#161b22')
    ax.set_xticks([]); ax.set_yticks([])
    n=5

    rng=np.random.RandomState(1337)
    alphabet=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    # Frames de estado:
    # 0: completamente aleatório
    # 1: coluna=linha (word square)
    # 2: + simetria central
    # 3: + palíndromo central
    # 4: Sator perfeito
    # 5-8: destaque das simetrias
    FRAMES=20
    stages=[]

    # Stage 0: aleatório
    M0=rng.choice(alphabet,size=(n,n))
    stages.append(('Matriz Aleatória',M0.tolist(),
                   f'H = {global_sator_entropy(M0):.3f} bits','#FF6B6B'))

    # Stage 1: aplicar transposição
    M1=M0.copy()
    for i in range(n):
        for j in range(i+1,n):
            M1[i][j]=M1[j][i]
    stages.append(('Word Square (M = Mᵀ)',M1.tolist(),
                   f'H = {global_sator_entropy(M1):.3f} bits','#FFEAA7'))

    # Stage 2: aplicar simetria central
    M2=M1.copy()
    for i in range(n):
        for j in range(n):
            if i*n+j < (n-1-i)*n+(n-1-j):
                M2[n-1-i][n-1-j]=M2[i][j]
    stages.append(('+ Simetria Central',M2.tolist(),
                   f'H = {global_sator_entropy(M2):.3f} bits','#45B7D1'))

    # Stage 3: Sator original
    stages.append(('Quadrado de Sator',M.tolist(),
                   f'H = {global_sator_entropy(M):.3f} bits','#4ECDC4'))

    # Repeat stage 3 com destaque
    for _ in range(2):
        stages.append(('Sator — Entropia Mínima',M.tolist(),
                       f'H(M|simetrias) ≈ 0 bits ✓','#96CEB4'))

    cmap_cells={0:'#FF6B6B',1:'#FFEAA7',2:'#45B7D1',3:'#4ECDC4',4:'#96CEB4',5:'#96CEB4'}

    patches_cache=[]
    texts_cache=[]
    title_obj=ax.text(2.5,5.4,'',ha='center',va='bottom',color='white',
                      fontsize=13,fontweight='bold')
    subtitle=ax.text(2.5,-0.55,'',ha='center',va='top',color='#8b949e',fontsize=11)
    ax.set_xlim(-0.1,n+0.1); ax.set_ylim(-0.9,n+0.8)

    frame_to_stage=[int(i*len(stages)/FRAMES) for i in range(FRAMES)]

    # Pre-draw cells
    cell_patches=[[None]*n for _ in range(n)]
    cell_texts=[[None]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            r=plt.Rectangle([j,n-1-i],1,1,facecolor='#21262d',
                             edgecolor='#30363d',linewidth=1.5)
            ax.add_patch(r)
            t=ax.text(j+.5,n-1-i+.5,'?',ha='center',va='center',
                      fontsize=18,fontweight='bold',color='white',family='monospace')
            cell_patches[i][j]=r
            cell_texts[i][j]=t

    def update(frame):
        s=frame_to_stage[frame]
        title,mat,ht,col=stages[min(s,len(stages)-1)]
        title_obj.set_text(title)
        subtitle.set_text(ht)
        subtitle.set_color(col)
        for i in range(n):
            for j in range(n):
                cell_patches[i][j].set_facecolor(col if s>=3 else '#21262d')
                cell_patches[i][j].set_alpha(0.75+0.2*(s/len(stages)))
                cell_texts[i][j].set_text(mat[i][j])
                cell_texts[i][j].set_color('#0d1117' if s>=3 else 'white')
        return []

    anim=FuncAnimation(fig,update,frames=FRAMES,interval=220,blit=False)
    writer=PillowWriter(fps=4)
    anim.save(save_path,writer=writer,dpi=100)
    plt.close(); print(f"✓ GIF: {save_path}")

def save_csv(dir_ent, glob_ent, rand_mean, rand_std, path):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['Métrica','Valor (bits)','Nota'])
        for d,v in dir_ent.items():
            w.writerow([f'Direcional {d}',f'{v:.6f}','Entropia de leitura'])
        w.writerow(['Global Sator',f'{glob_ent:.6f}','Toda a matriz'])
        w.writerow(['Aleatório (média)',f'{rand_mean:.6f}','N=1000 amostras'])
        w.writerow(['Aleatório (std)',f'{rand_std:.6f}','N=1000 amostras'])
        w.writerow(['Δ (aleatório-Sator)',f'{rand_mean-glob_ent:.6f}','Ganho estrutural'])
        max_dir=max(dir_ent.values()); min_dir=min(dir_ent.values())
        w.writerow(['Δ direcional',f'{max_dir-min_dir:.6f}','Invariância direcional'])
    print(f"✓ {path}")

if __name__=='__main__':
    print("="*55)
    print("EXP-02: ANÁLISE DE ENTROPIA DE SHANNON")
    print("="*55)
    M=np.array([list(w) for w in SATOR])
    dir_ent,glob_ent,rand_mean,rand_std=plot_entropy_heatmap(
        M, os.path.join(FIG_DIR,"entropy_heatmap.png"))
    print(f"\nResultados:")
    for d,v in dir_ent.items():
        print(f"  H({d}) = {v:.4f} bits")
    print(f"  H(global Sator)   = {glob_ent:.4f} bits")
    print(f"  H(aleatório)      = {rand_mean:.4f} ± {rand_std:.4f}")
    print(f"  Δ direcional      = {max(dir_ent.values())-min(dir_ent.values()):.6f}")
    create_entropy_gif(M, os.path.join(ANI_DIR,"entropy_reduction.gif"))
    save_csv(dir_ent,glob_ent,rand_mean,rand_std,
             os.path.join(RES_DIR,"02_entropy_data.csv"))
    print("\nEXP-02 COMPLETO ✓")
