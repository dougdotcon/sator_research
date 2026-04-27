"""
EXP-03: Prova Computacional de Raridade do Quadrado de Sator
=============================================================
Monte Carlo: testa N matrizes aleatórias contra cada filtro de simetria.
Demonstra a raridade extrema de quadrados Sator-like.
Output: figures/rarity/ + results/rarity/03_rarity_data.csv
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv, os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures", "rarity")
RES_DIR = os.path.join(BASE, "results", "rarity")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

SATOR = ["SATOR","AREPO","TENET","OPERA","ROTAS"]
ALPHA = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
N_ALPHA = len(ALPHA)

def is_word_square(M):
    n = len(M)
    return all(M[i][j]==M[j][i] for i in range(n) for j in range(n))

def is_central_symmetric(M):
    n = len(M)
    return all(M[i][j]==M[n-1-i][n-1-j] for i in range(n) for j in range(n))

def is_palindrome_center(M):
    c = M[2]; n = len(c)
    return all(c[k]==c[n-1-k] for k in range(n))

def random_5x5(rng):
    return rng.choice(ALPHA, size=(5,5))

def monte_carlo_rarity(N=500_000, seed=42):
    """Roda Monte Carlo com N matrizes aleatórias e conta hits em cada filtro."""
    rng = np.random.RandomState(seed)
    counts = {
        'total': N,
        'word_square': 0,
        'central_sym': 0,
        'palindrome_center': 0,
        'ws_and_cs': 0,
        'all_three': 0,
    }
    for trial in range(N):
        M = random_5x5(rng)
        ws = is_word_square(M)
        cs = is_central_symmetric(M)
        pc = is_palindrome_center(M)
        if ws: counts['word_square'] += 1
        if cs: counts['central_sym'] += 1
        if pc: counts['palindrome_center'] += 1
        if ws and cs: counts['ws_and_cs'] += 1
        if ws and cs and pc: counts['all_three'] += 1
        if (trial+1) % 100_000 == 0:
            print(f"  [{trial+1:,}/{N:,}] ws={counts['word_square']} cs={counts['central_sym']} all={counts['all_three']}")
    return counts

def theoretical_probabilities():
    """Calcula probabilidades teóricas (sem restrição de vocabulário)."""
    # P(word square) = 1/26^10 (10 posições livres na parte superior da diagonal)
    # Mas simplificando: P(M[i,j]=M[j,i]) = 1/26 por par
    n_pairs_ws = 10  # C(5,2) = 10 pares off-diagonal
    p_ws = (1/N_ALPHA)**n_pairs_ws

    # P(central sym) = (1/26)^12 (12 posições únicas excluindo anti-diagonais)
    # Rigoroso: 25 posições, grupo Klein tem 9 órbitas independentes
    n_orbits = 9
    # mas: central sym sozinha: ceil(25/2)=13 posições independentes
    p_cs = (1/N_ALPHA)**12

    # P(palindrome center) = 1/26^2
    p_pc = (1/N_ALPHA)**2

    # P(todos) ≈ 1/26^(25-9) = 1/26^16 (9 órbitas livres, 16 determinadas)
    p_all = (1/N_ALPHA)**16

    return {
        'word_square': p_ws,
        'central_sym': p_cs,
        'palindrome_center': p_pc,
        'all_three_approx': p_all,
    }

def plot_rarity_funnel(counts, theory, save_path):
    """Funil de raridade: cada filtro reduz o espaço."""
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.patch.set_facecolor('#0d1117')

    N = counts['total']
    stages = [
        ('Matrizes\nAleatórias', N, '#8b949e', '100%'),
        ('Word Square\n$M=M^T$', counts['word_square'], '#FF6B6B', f"{counts['word_square']/N*100:.3f}%"),
        ('+ Sym. Central\n$M[i,j]=M[4-i,4-j]$', counts['ws_and_cs'], '#FFEAA7', f"{counts['ws_and_cs']/N*100:.5f}%"),
        ('+ Palíndromo\nCentral', counts['all_three'], '#4ECDC4', f"{counts['all_three']/N*100:.6f}%"),
    ]

    # ── Subplot 1: Funil logarítmico ─────────────────────────────────────────
    ax = axes[0]
    ax.set_facecolor('#161b22')
    ax.set_title('Funil de Raridade (Monte Carlo)\n'
                 f'N = {N:,} matrizes aleatórias 5×5',
                 color='white', fontsize=12, fontweight='bold')

    vals = [s[1] for s in stages]
    labels = [s[0] for s in stages]
    colors = [s[2] for s in stages]
    pcts = [s[3] for s in stages]

    bars = ax.barh(range(len(stages)), [max(v,0.1) for v in vals],
                   color=colors, edgecolor='#30363d', linewidth=1.5,
                   log=True, height=0.5)

    for i, (bar, v, pct) in enumerate(zip(bars, vals, pcts)):
        ax.text(max(v*1.1, 1), i, f'{v:,}  ({pct})',
                va='center', color='white', fontsize=10, fontweight='bold')

    ax.set_yticks(range(len(stages)))
    ax.set_yticklabels(labels, color='white', fontsize=10)
    ax.set_xlabel('Contagem (escala log)', color='white', fontsize=10)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#30363d')
    ax.set_facecolor('#161b22')
    ax.xaxis.label.set_color('white')

    # ── Subplot 2: Probabilidades teóricas ──────────────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor('#161b22')
    ax2.set_title('Probabilidades Teóricas (sem filtro lexical)\n'
                  '$|\\Sigma|=26$, grupo de Klein $\\mathbb{Z}_2\\times\\mathbb{Z}_2$',
                  color='white', fontsize=12, fontweight='bold')
    ax2.axis('off')

    lines = [
        ('💡 Análise Teórica', '', '#FFEAA7', True),
        ('', '', '#0d1117', False),
        ('Espaço total de matrizes 5×5:', f'$26^{{25}} \\approx 2.36\\times10^{{35}}$', '#8b949e', False),
        ('', '', '#0d1117', False),
        ('Com simetria diagonal (9 livres):',f'$26^{{9}}\\approx 5.4\\times10^{{12}}$','#FF6B6B',False),
        ('P(word square):', f'{theory["word_square"]:.2e}', '#FF6B6B', False),
        ('', '', '#0d1117', False),
        ('P(sym. central):', f'{theory["central_sym"]:.2e}', '#FFEAA7', False),
        ('', '', '#0d1117', False),
        ('P(palíndromo central):', f'{theory["palindrome_center"]:.2e}', '#45B7D1', False),
        ('', '', '#0d1117', False),
        ('P(todas as simetrias):', f'$26^{{-16}} \\approx {theory["all_three_approx"]:.2e}$', '#4ECDC4', False),
        ('', '', '#0d1117', False),
        ('', '', '#0d1117', False),
        ('🔴 Ainda falta:', 'restrição lexical (palavras válidas)', '#FF6B6B', True),
        ('→ Raridade real', 'muito menor que $26^{-16}$', '#FF6B6B', False),
    ]

    for k, (label, val, col, bold) in enumerate(lines):
        y = 0.97 - k * 0.058
        fw = 'bold' if bold else 'normal'
        ax2.text(0.02, y, label, transform=ax2.transAxes,
                 color=col, fontsize=10, fontweight=fw, va='top')
        if val:
            ax2.text(0.65, y, val, transform=ax2.transAxes,
                     color=col, fontsize=10, fontweight='bold', va='top')

    plt.suptitle('EXP-03 — Prova de Raridade Estatística do Quadrado de Sator',
                 color='white', fontsize=14, fontweight='bold', y=1.01)
    fig.text(0.5, -0.02,'Programa de Pesquisa Sator | Douglas H. M. Fulber | 2026',
             ha='center', color='#8b949e', fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.close(); print(f"✓ {save_path}")

def plot_compression_curve(save_path):
    """Mostra como a compressão estrutural cresce com o tamanho do alfabeto."""
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#161b22')

    sigma_range = np.arange(2, 100)
    # |Σ|^25 vs |Σ|^9
    total_space = sigma_range ** 25
    free_space  = sigma_range ** 9
    compression = free_space / total_space  # = sigma^(-16)

    ax.semilogy(sigma_range, compression, color='#4ECDC4', lw=2.5, label='$|\\Sigma|^{-16}$')
    ax.axvline(26, color='#FF6B6B', lw=2, ls='--', label='Alfabeto latino ($|\\Sigma|=26$)')
    ax.scatter([26], [26**(-16)], color='#FF6B6B', zorder=5, s=100)
    ax.text(28, 26**(-16)*2, f'$26^{{-16}} \\approx {26**(-16):.2e}$',
            color='#FF6B6B', fontsize=11, fontweight='bold')

    ax.set_xlabel('Tamanho do alfabeto $|\\Sigma|$', color='white', fontsize=12)
    ax.set_ylabel('Compressão estrutural $|\\Sigma|^{-16}$', color='white', fontsize=12)
    ax.set_title('Compressão Estrutural do Grupo de Klein\n'
                 '$|\\Sigma|^{25} \\to |\\Sigma|^9$ (9 órbitas independentes)',
                 color='white', fontsize=13, fontweight='bold')
    ax.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', fontsize=11)
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#30363d')
    ax.spines['top'].set_color('#30363d')
    ax.spines['left'].set_color('#30363d')
    ax.spines['right'].set_color('#30363d')
    ax.set_facecolor('#161b22')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    # Texto explicativo
    ax.text(50, 1e-10, 'Com restrição lexical:\nraridade ancora abaixo desta curva',
            color='#FFEAA7', fontsize=10, style='italic',
            bbox=dict(boxstyle='round', facecolor='#21262d', alpha=0.7, edgecolor='#30363d'))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.close(); print(f"✓ {save_path}")

def save_csv(counts, theory, path):
    N = counts['total']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Filtro', 'Contagem', 'Frequência', 'Prob. Teórica'])
        w.writerow(['Total', N, '100%', '1'])
        w.writerow(['Word Square', counts['word_square'],
                    f"{counts['word_square']/N:.6f}", f"{theory['word_square']:.6e}"])
        w.writerow(['WS + Central Sym', counts['ws_and_cs'],
                    f"{counts['ws_and_cs']/N:.8f}", f"{theory['central_sym']:.6e}"])
        w.writerow(['Todas (3 filtros)', counts['all_three'],
                    f"{counts['all_three']/N:.10f}", f"{theory['all_three_approx']:.6e}"])
    print(f"✓ {path}")

if __name__ == '__main__':
    print("="*55)
    print("EXP-03: PROVA DE RARIDADE (MONTE CARLO)")
    print("="*55)
    print("Rodando simulação (pode demorar ~30s)...")
    counts = monte_carlo_rarity(N=500_000)
    theory = theoretical_probabilities()
    print("\nResultados Monte Carlo:")
    for k,v in counts.items():
        print(f"  {k}: {v:,}")
    print("\nProbabilidades teóricas:")
    for k,v in theory.items():
        print(f"  {k}: {v:.3e}")
    plot_rarity_funnel(counts, theory, os.path.join(FIG_DIR, "rarity_funnel.png"))
    plot_compression_curve(os.path.join(FIG_DIR, "compression_curve.png"))
    save_csv(counts, theory, os.path.join(RES_DIR, "03_rarity_data.csv"))
    print("\nEXP-03 COMPLETO ✓")
