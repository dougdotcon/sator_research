"""
EXP-01: Sator Square Formal Validator
Verifica as 3 propriedades matemáticas e visualiza as órbitas do grupo de Klein.
Output: figures/symmetry_viz/ + results/entropy/01_validation_report.csv
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv, os, json
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures", "symmetry_viz")
RES_DIR = os.path.join(BASE, "results", "entropy")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

SATOR = ["SATOR","AREPO","TENET","OPERA","ROTAS"]

def words_to_matrix(words):
    return np.array([list(w.upper()) for w in words])

def check_word_square(M):
    n=len(M); errors=[]
    for i in range(n):
        for j in range(n):
            if M[i][j]!=M[j][i]: errors.append((i,j))
    return len(errors)==0, errors

def check_central_symmetry(M):
    n=len(M); errors=[]
    for i in range(n):
        for j in range(n):
            if M[i][j]!=M[n-1-i][n-1-j]: errors.append((i,j))
    return len(errors)==0, errors

def check_palindrome_center(M):
    c=M[2]; n=len(c)
    return all(c[k]==c[n-1-k] for k in range(n)), "".join(c)

def check_reverse_pairs(words):
    return {
        'W1_W5': (words[0], words[4][::-1], words[0]==words[4][::-1]),
        'W2_W4': (words[1], words[3][::-1], words[1]==words[3][::-1]),
        'W3_palindrome': (words[2], words[2][::-1], words[2]==words[2][::-1]),
    }

def calculate_orbits(n=5):
    orbit_map={}; cid=0; visited=set()
    for i in range(n):
        for j in range(n):
            if (i,j) not in visited:
                orbit={(i,j),(j,i),(n-1-i,n-1-j),(n-1-j,n-1-i)}
                for pos in orbit:
                    if pos not in visited:
                        orbit_map[pos]=cid; visited.add(pos)
                cid+=1
    return orbit_map, cid

def full_validation(words):
    M=words_to_matrix(words)
    ws_ok,ws_err=check_word_square(M)
    cs_ok,cs_err=check_central_symmetry(M)
    pal_ok,pal_w=check_palindrome_center(M)
    rev=check_reverse_pairs(words)
    report={
        'timestamp':datetime.now().isoformat(),'words':words,
        'word_square':{'passed':ws_ok,'errors':ws_err},
        'central_symmetry':{'passed':cs_ok,'errors':cs_err},
        'palindrome_center':{'passed':pal_ok,'word':pal_w},
        'reverse_pairs':rev,
        'overall':ws_ok and cs_ok and pal_ok and all(v[2] for v in rev.values())
    }
    return report, M

PALETTE=['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7','#DDA0DD','#98D8C8','#F7DC6F','#BB8FCE']

def plot_orbits(M, orbit_map, n_orbits, path):
    fig,axes=plt.subplots(1,2,figsize=(16,7))
    fig.patch.set_facecolor('#0d1117')
    n=len(M)
    for ax,(title,color_fn) in zip(axes,[
        ("Órbitas do Grupo de Klein $G=\\mathbb{Z}_2\\times\\mathbb{Z}_2$",
         lambda i,j: PALETTE[orbit_map[(i,j)]%len(PALETTE)]),
        ("Simetrias Verificadas",
         lambda i,j: '#1f6feb' if i==j else ('#f78166' if i==2 else '#21262d'))
    ]):
        ax.set_facecolor('#161b22')
        ax.set_title(title,color='white',fontsize=12,pad=12,fontweight='bold')
        for i in range(n):
            for j in range(n):
                rect=plt.Rectangle([j,n-1-i],1,1,facecolor=color_fn(i,j),alpha=0.88,
                                    edgecolor='#30363d',linewidth=2)
                ax.add_patch(rect)
                ax.text(j+.5,n-1-i+.5,M[i][j],ha='center',va='center',
                        fontsize=22,fontweight='bold',color='#0d1117',family='monospace')
        ax.set_xlim(0,n); ax.set_ylim(0,n)
        ax.set_xticks([]); ax.set_yticks([])

    # Legend for orbits on left
    leg=[mpatches.Patch(color=PALETTE[i],label=f'Órbita {i}') for i in range(n_orbits)]
    axes[0].legend(handles=leg,loc='upper left',bbox_to_anchor=(-0.02,-0.04),ncol=3,
                   facecolor='#161b22',edgecolor='#30363d',labelcolor='white',fontsize=9)
    # Annotations right
    notes=[
        ('✓ M = Mᵀ','#4ECDC4'),('✓ M[i,j]=M[4-i,4-j]','#4ECDC4'),
        ('✓ TENET palíndrome','#4ECDC4'),('✓ ROTAS=rev(SATOR)','#4ECDC4'),
        (f'{n_orbits} órbitas | $|\\Sigma|^{{25}}\\to|\\Sigma|^{n_orbits}$','#FFEAA7'),
    ]
    ax2=axes[1]
    for k,(txt,c) in enumerate(notes):
        ax2.text(5.1,4.5-k*0.75,txt,color=c,fontsize=10,va='center')
    ax2.set_xlim(0,7); ax2.set_ylim(0,5)

    plt.suptitle('EXP-01 — Validação Formal do Quadrado de Sator',
                 color='white',fontsize=14,fontweight='bold',y=1.01)
    plt.tight_layout()
    plt.savefig(path,dpi=150,bbox_inches='tight',facecolor='#0d1117')
    plt.close(); print(f"✓ {path}")

def save_csv(report, path):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['Propriedade','Status','Detalhes'])
        w.writerow(['Timestamp',report['timestamp'],''])
        w.writerow(['Palavras',' | '.join(report['words']),''])
        w.writerow(['Word Square',report['word_square']['passed'],
                    f"erros:{len(report['word_square']['errors'])}"])
        w.writerow(['Simetria Central',report['central_symmetry']['passed'],
                    f"erros:{len(report['central_symmetry']['errors'])}"])
        w.writerow(['Palíndromo Central',report['palindrome_center']['passed'],
                    report['palindrome_center']['word']])
        for k,v in report['reverse_pairs'].items():
            w.writerow([k,v[2],f"{v[0]}<->{v[1]}"])
        w.writerow(['GLOBAL',report['overall'],''])
    print(f"✓ {path}")

if __name__=='__main__':
    print("="*55)
    print("EXP-01: VALIDADOR FORMAL DO QUADRADO DE SATOR")
    print("="*55)
    report,M=full_validation(SATOR)
    for k,v in report.items():
        if k not in ('timestamp','words'):
            print(f"  {k}: {v}")
    orbit_map,n_orbits=calculate_orbits()
    print(f"\n  Órbitas Klein G: {n_orbits}")
    print(f"  Compressão: 26^{{-{25-n_orbits}}} ≈ {26**(-(25-n_orbits)):.2e}")
    plot_orbits(M,orbit_map,n_orbits,os.path.join(FIG_DIR,"sator_orbits.png"))
    save_csv(report,os.path.join(RES_DIR,"01_validation_report.csv"))
    print("\nEXP-01 COMPLETO ✓")
