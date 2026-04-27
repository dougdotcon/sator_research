"""
EXP-05: Bridge Sator ↔ TAMESIS (TRI/TDTR)
==========================================
Simula degradação (Isfet) e recuperação (Ma'at) da informação no Sator.
Conecta com a tese TDTR: reversibilidade simbólica local vs irreversibilidade física.
Output: figures/tamesis_bridge/ + results/entropy/05_bridge_data.csv
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, PillowWriter
import csv, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures", "tamesis_bridge")
RES_DIR = os.path.join(BASE, "results", "entropy")
ANI_DIR = os.path.join(BASE, "figures", "animations")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)
os.makedirs(ANI_DIR, exist_ok=True)

SATOR = ["SATOR","AREPO","TENET","OPERA","ROTAS"]
ALPHA = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
N = 5

def words_to_matrix(words):
    return [list(w.upper()) for w in words]

def matrix_to_words(M):
    return [''.join(r) for r in M]

# ─── Operador de Degradação (Isfet / Ruído) ───────────────────────────────────

def isfet_degrade(M, n_errors, rng):
    """
    Aplica n_errors erros aleatórios à matriz.
    模拟 Isfet: corrupção, ruído, degradação de informação.
    """
    Mc = [r[:] for r in M]
    positions = list((i,j) for i in range(N) for j in range(N))
    chosen = rng.choice(len(positions), size=min(n_errors, 25), replace=False)
    error_positions = [positions[k] for k in chosen]
    for (i,j) in error_positions:
        orig = Mc[i][j]
        new = rng.choice([c for c in ALPHA if c!=orig])
        Mc[i][j] = new
    return Mc, error_positions

# ─── Operador de Recuperação (Ma'at / Reconstrução) ──────────────────────────

def maat_recover(M_degraded, M_original):
    """
    Tenta recuperar a matriz usando as 4 simetrias do Sator:
    1. word_square: M[i][j] = M[j][i]
    2. central: M[i][j] = M[4-i][4-j]
    3. palindrome center: M[2][k] = M[2][4-k]
    4. word_square + central combinados

    Retorna a matriz recuperada e o número de posições corretamente restauradas.
    """
    Mr = [r[:] for r in M_degraded]
    recovered = 0
    # Aplicar simetria: para cada posição, verificar se o espelho é mais provável
    for i in range(N):
        for j in range(N):
            candidates = [Mr[i][j]]
            # Simetria diagonal
            candidates.append(Mr[j][i])
            # Simetria central
            candidates.append(Mr[N-1-i][N-1-j])
            # Simetria central + diagonal
            candidates.append(Mr[N-1-j][N-1-i])
            # Votação por maioria
            from collections import Counter
            vote = Counter(candidates).most_common(1)[0][0]
            if vote != Mr[i][j] and vote == M_original[i][j]:
                recovered += 1
            Mr[i][j] = vote
    return Mr, recovered

def recovery_rate(M_original, M_recovered):
    """Porcentagem de posições corretamente recuperadas."""
    total = N * N
    correct = sum(1 for i in range(N) for j in range(N) if M_recovered[i][j]==M_original[i][j])
    return correct / total

def run_recovery_experiment(n_trials=200, seed=42):
    """Para cada número de erros (0-25), mede a taxa de recuperação."""
    rng = np.random.RandomState(seed)
    M_orig = words_to_matrix(SATOR)
    results = {}
    for n_errors in range(0, 26):
        rates = []
        for _ in range(n_trials):
            Md, _ = isfet_degrade(M_orig, n_errors, rng)
            Mr, _ = maat_recover(Md, M_orig)
            rate = recovery_rate(M_orig, Mr)
            rates.append(rate)
        results[n_errors] = {
            'mean': float(np.mean(rates)),
            'std': float(np.std(rates)),
            'min': float(np.min(rates)),
            'max': float(np.max(rates)),
        }
    return results

# ─── Visualizações ────────────────────────────────────────────────────────────

def plot_recovery_curve(recovery_results, save_path):
    """Curva de recuperação Ma'at vs erros Isfet."""
    errors = sorted(recovery_results.keys())
    means = [recovery_results[e]['mean'] for e in errors]
    stds = [recovery_results[e]['std'] for e in errors]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#0d1117')

    # ── Curva principal ──────────────────────────────────────────────────────
    ax = axes[0]
    ax.set_facecolor('#161b22')
    err_arr = np.array(errors)
    mean_arr = np.array(means)
    std_arr = np.array(stds)

    ax.fill_between(err_arr, mean_arr-std_arr, mean_arr+std_arr,
                    alpha=0.3, color='#4ECDC4', label='±1σ')
    ax.plot(err_arr, mean_arr, color='#4ECDC4', lw=2.5, label='Recuperação média (Ma\'at)')
    ax.axhline(1.0, color='#96CEB4', lw=1.5, ls='--', label='Perfeito (100%)')
    ax.axhline(0.64, color='#8b949e', lw=1.5, ls=':', label='Chance aleatória (64%)')

    # Região de recuperação quase-perfeita
    perfect_threshold = [e for e in errors if means[errors.index(e)] >= 0.99]
    if perfect_threshold:
        ax.axvspan(0, max(perfect_threshold), alpha=0.15, color='#4ECDC4',
                   label=f'Recuperação ≥99% (≤{max(perfect_threshold)} erros)')

    # Ponto de colapso (~50%)
    half_idx = next((i for i,m in enumerate(means) if m < 0.5), len(means)-1)
    ax.scatter([errors[half_idx]], [means[half_idx]], color='#FF6B6B', zorder=5, s=100)
    ax.text(errors[half_idx]+0.3, means[half_idx], f'Colapso\n(~{means[half_idx]*100:.0f}%)',
            color='#FF6B6B', fontsize=9)

    ax.set_xlabel('Número de Erros (Isfet / Ruído)', color='white', fontsize=11)
    ax.set_ylabel('Taxa de Recuperação (Ma\'at)', color='white', fontsize=11)
    ax.set_title('Capacidade de Recuperação do Sator\n'
                 'Simulação: Degradação (Isfet) → Recuperação por Simetria (Ma\'at)',
                 color='white', fontsize=11, fontweight='bold')
    ax.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', fontsize=9)
    ax.tick_params(colors='white')
    ax.set_xlim(0, 25); ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.0f}%'))
    for spine in ax.spines.values():
        spine.set_edgecolor('#30363d')

    # ── Mapa de conceitos TDTR/Tamesis ──────────────────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor('#161b22')
    ax2.axis('off')
    ax2.set_title('Bridge: Sator ↔ TDTR ↔ Ma\'at/Isfet',
                  color='white', fontsize=12, fontweight='bold')

    concepts = [
        ('🌌 TDTR', 'Irreversibilidade dos regimes\nfísicos. O tempo flui de\nalta→baixa entropia.', '#FF6B6B', 0.85),
        ('🔲 Sator', 'Reversibilidade simbólica local.\nA matriz preserva informação\nem 4 direções.', '#4ECDC4', 0.60),
        ('⚖️ Ma\'at', 'Recuperação por simetria.\nBaixa entropia, ordem,\ncoerência estrutural.', '#96CEB4', 0.35),
        ('🔥 Isfet', 'Ruído, corrupção, degradação.\nLetras apagadas, erros,\ndistorção do símbolo.', '#FFEAA7', 0.10),
    ]

    for name, desc, col, y in concepts:
        ax2.text(0.05, y, name, transform=ax2.transAxes,
                 color=col, fontsize=13, fontweight='bold', va='center')
        ax2.text(0.30, y, desc, transform=ax2.transAxes,
                 color='white', fontsize=9, va='center', alpha=0.9)

    # Fórmula central
    ax2.text(0.5, -0.05,
             '$H(M_{ij}|\\text{simetrias}) \\approx 0 \\Rightarrow$ Isfet não vence Ma\'at',
             transform=ax2.transAxes, ha='center', color='#FFEAA7', fontsize=10,
             fontweight='bold', style='italic')

    plt.suptitle('EXP-05 — Bridge Sator–TDTR–Tamesis: Reversibilidade vs Irreversibilidade',
                 color='white', fontsize=13, fontweight='bold', y=1.01)
    fig.text(0.5,-0.02,'Programa Tamesis | Douglas H. M. Fulber | 2026',
             ha='center',color='#8b949e',fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.close(); print(f"✓ {save_path}")

def plot_degradation_gallery(save_path):
    """Gallery: Sator em vários estágios de degradação (0, 3, 7, 12, 20 erros)."""
    rng = np.random.RandomState(999)
    M_orig = words_to_matrix(SATOR)
    error_counts = [0, 3, 7, 12, 20]

    fig, axes = plt.subplots(2, len(error_counts), figsize=(18, 8))
    fig.patch.set_facecolor('#0d1117')

    COLORS_ROW = ['#FF6B6B','#4ECDC4','#45B7D1','#4ECDC4','#FF6B6B']

    for col, ne in enumerate(error_counts):
        Md, err_pos = isfet_degrade(M_orig, ne, rng)
        Mr, recovered = maat_recover(Md, M_orig)
        rec_rate = recovery_rate(M_orig, Mr)

        err_set = set(map(tuple, err_pos))

        for row, (M_plot, title) in enumerate([
            (Md, f'Isfet: {ne} erros'),
            (Mr, f'Ma\'at: {rec_rate*100:.0f}% recuperado')
        ]):
            ax = axes[row][col]
            ax.set_facecolor('#161b22')
            ax.set_title(title, color='white', fontsize=9, fontweight='bold')

            for i in range(N):
                for j in range(N):
                    is_err = (i,j) in err_set
                    is_correct = M_plot[i][j] == M_orig[i][j]
                    if row == 0:  # degradado
                        fc = '#7f1d1d' if is_err else '#21262d'
                    else:  # recuperado
                        fc = '#1a472a' if is_correct else '#7f1d1d'
                    rect = plt.Rectangle([j,N-1-i],1,1,facecolor=fc,
                                          edgecolor='#30363d',linewidth=1.3)
                    ax.add_patch(rect)
                    ax.text(j+.5,N-1-i+.5,M_plot[i][j],ha='center',va='center',
                            fontsize=14,fontweight='bold',
                            color='#FF6B6B' if not is_correct and row==0 else 'white',
                            family='monospace')
            ax.set_xlim(0,N); ax.set_ylim(0,N)
            ax.set_xticks([]); ax.set_yticks([])

    plt.suptitle('EXP-05 — Galeria de Degradação Isfet → Recuperação Ma\'at',
                 color='white', fontsize=13, fontweight='bold', y=1.01)
    fig.text(0.5,-0.01,'Vermelho=erro | Verde=recuperado | Linha superior=degradado | Inferior=recuperado',
             ha='center',color='#8b949e',fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.close(); print(f"✓ {save_path}")

def create_degradation_gif(save_path):
    """GIF: degradação progressiva e recuperação do Sator."""
    rng = np.random.RandomState(12345)
    M_orig = words_to_matrix(SATOR)
    FRAMES = 24

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor('#0d1117')
    for ax in axes:
        ax.set_facecolor('#161b22')
        ax.set_xticks([]); ax.set_yticks([])

    cell_patches = [[[None]*N for _ in range(N)] for _ in range(2)]
    cell_texts   = [[[None]*N for _ in range(N)] for _ in range(2)]
    titles_ax = [
        axes[0].set_title('Isfet (Degradação)', color='#FF6B6B', fontsize=13, fontweight='bold'),
        axes[1].set_title("Ma'at (Recuperação)", color='#4ECDC4', fontsize=13, fontweight='bold'),
    ]

    for side in range(2):
        ax = axes[side]
        for i in range(N):
            for j in range(N):
                r = plt.Rectangle([j,N-1-i],1,1,facecolor='#21262d',
                                   edgecolor='#30363d',linewidth=1.5)
                ax.add_patch(r)
                t = ax.text(j+.5,N-1-i+.5,'',ha='center',va='center',
                            fontsize=18,fontweight='bold',color='white',family='monospace')
                cell_patches[side][i][j]=r
                cell_texts[side][i][j]=t
        ax.set_xlim(0,N); ax.set_ylim(-0.4,N)

    info1 = axes[0].text(2.5,-0.3,'',ha='center',color='#FF6B6B',fontsize=11)
    info2 = axes[1].text(2.5,-0.3,'',ha='center',color='#4ECDC4',fontsize=11)

    def update(frame):
        n_err = int(frame * 25 / (FRAMES//2)) if frame < FRAMES//2 else int((FRAMES-frame) * 25 / (FRAMES//2))
        n_err = min(n_err, 25)
        Md, err_pos = isfet_degrade(M_orig, n_err, rng)
        Mr, _ = maat_recover(Md, M_orig)
        err_set = set(map(tuple, err_pos))
        rec_rate = recovery_rate(M_orig, Mr)
        for i in range(N):
            for j in range(N):
                # Esquerda: degradado
                is_err = (i,j) in err_set
                cell_patches[0][i][j].set_facecolor('#7f1d1d' if is_err else '#21262d')
                cell_texts[0][i][j].set_text(Md[i][j])
                cell_texts[0][i][j].set_color('#FF6B6B' if is_err else 'white')
                # Direita: recuperado
                ok = Mr[i][j] == M_orig[i][j]
                cell_patches[1][i][j].set_facecolor('#1a472a' if ok else '#7f1d1d')
                cell_texts[1][i][j].set_text(Mr[i][j])
                cell_texts[1][i][j].set_color('white')
        info1.set_text(f'{n_err} erros (Isfet)')
        info2.set_text(f'{rec_rate*100:.0f}% recuperado (Ma\'at)')
        return []

    anim = FuncAnimation(fig, update, frames=FRAMES, interval=200, blit=False)
    plt.suptitle("EXP-05 — Isfet vs Ma'at: Ciclo de Degradação e Recuperação",
                 color='white', fontsize=12, fontweight='bold')
    writer = PillowWriter(fps=5)
    anim.save(save_path, writer=writer, dpi=100)
    plt.close(); print(f"✓ GIF: {save_path}")

def save_csv(results, path):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['n_errors','recovery_mean','recovery_std','recovery_min','recovery_max'])
        for n_err, d in sorted(results.items()):
            w.writerow([n_err, f"{d['mean']:.4f}", f"{d['std']:.4f}",
                        f"{d['min']:.4f}", f"{d['max']:.4f}"])
    print(f"✓ {path}")

if __name__ == '__main__':
    print("="*55)
    print("EXP-05: BRIDGE SATOR ↔ TAMESIS (TRI/TDTR)")
    print("="*55)
    print("Rodando experimento de recuperação (200 trials × 26 níveis)...")
    results = run_recovery_experiment(n_trials=200)

    # Resumo
    for n_err in [0,1,3,5,7,10,15,20,25]:
        d = results[n_err]
        print(f"  {n_err:2d} erros → Recuperação: {d['mean']*100:.1f}% ± {d['std']*100:.1f}%")

    plot_recovery_curve(results, os.path.join(FIG_DIR,"recovery_curve.png"))
    plot_degradation_gallery(os.path.join(FIG_DIR,"degradation_gallery.png"))
    create_degradation_gif(os.path.join(ANI_DIR,"isfet_maat_cycle.gif"))
    save_csv(results, os.path.join(RES_DIR,"05_bridge_data.csv"))
    print("\nEXP-05 COMPLETO ✓")
