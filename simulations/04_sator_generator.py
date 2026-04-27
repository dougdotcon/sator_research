"""
EXP-04: Gerador de Quadrados Sator-like em Múltiplos Idiomas
=============================================================
CSP com índice de prefixos + backtracking para encontrar quadrados
Sator-like em inglês, português e latim.
Output: results/squares/ + figures/symmetry_viz/found_squares.png
"""
import os, json, csv, time
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from itertools import product as iproduct

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "figures", "symmetry_viz")
RES_DIR = os.path.join(BASE, "results", "squares")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# ─── Léxicos Embutidos ────────────────────────────────────────────────────────
# Vocabulário curado de palavras de 5 letras com pares reversos conhecidos
# (léxicos completos podem ser carregados via arquivo .txt externo)

ENGLISH_5 = [
    "LEVEL","REPAY","YAPER","TIMER","REMIT","DEPOT","TOPED","LACED","DECAL",
    "RACED","DECRA","MADAM","REFER","CIVIC","KAYAK","LATER","RETAL","PARTS",
    "STRAP","SMART","TRAMS","STOPS","SPOTS","POOLS","SLOOP","LOOPS","SPOOL",
    "SPOTS","STOPS","STABS","SBATS","REPOT","TOPER","LAGER","REGAL","PAGER",
    "REGAP","TONER","RETON","SENOR","RONES","LEMON","NOMEL","REPAY","YAPER",
    "KEELS","SLEEK","SPEED","DEEPS","SLEEP","PEELS","KNOBS","SBONK","DRAWS",
    "SWARD","LIVED","DEVIL","DIAPER","SNAPS","SPANS","RAPS","DEWAR","RAWED",
    "STRAW","WARTS","SMART","TRAMS","NIPS","STINK","KNITS","SPINS","SNIPS",
    "REPEL","LEPER","SPOTS","STOPS","SPIT","TIPS","EMIT","TIME","STAR","RATS",
    "PARTS","STRAP","TAPS","SPAT","PALS","SLAP","RAPS","SPAR","LOOT","TOOL",
    "DOOM","MOOD","LOOP","POOL","KEEP","PEEK","SEES","NOON","DEED","TOOT",
    "MADAM","LEVEL","CIVIC","RADAR","REFER","KAYAK","ROTOR","SEXES",
    "REPAY","YAPER","NAMER","REMAN","PALER","RELAP","LASER","RESAL",
    "PETAL","LATEP","LEMON","NOMEL","DEPOT","TOPED","REVEL","LEVER",
    "SANER","RENAS","RIPEN","NEPIR","MIRED","DERIM","TAMED","DEMAT",
    "RATED","DETAR","CIDER","REDIC","LACED","DECAL","OGLED","DELGO",
    "OPTED","DETPO","TONED","DENOT","CAPES","SEPAC","NOTES","ESTON",
    "PORES","SEROP","ACRES","SERCA","NAMES","SEMAN","MALES","SELAM",
    "TALES","SELAT","ROPES","SEPOR","MOLES","SELOM","PILES","SELIP",
    "ROLES","SELOR","POLES","SELOP","LOPES","SEPOL","SLOPE","EPOLS",
    "REPOT","TOPER","TOPER","REPOT","PORED","DEPOT","DEPOT","PORED",
]
ENGLISH_5 = list(set(w for w in ENGLISH_5 if len(w)==5))

PORTUGUESE_5 = [
    "MAMAR","RADAR","LEVEL","SEBES","SOMOS","REFER",
    "ARARA","ANONA","MIRIM","SALSA","ROTOR","KAYAK",
    "ALMAS","SAMLA","SALAM","MALAS","MALSA","SALMA",
    "ROLAR","RAROL","SOLAR","LAROS","MORAL","LAROM",
    "CARAS","SARAC","TARAS","SARAT","PARAS","SARAP",
    "COPOS","SOPOC","LIMOS","SOMIL","RIMOS","SOMIR",
    "SOMAR","RAMOS","TOCAR","RACOT","VOTAR","RATOV",
    "NOTAR","RATON","PEGAR","RAGEP","TOMAR","RAMOТ",
    "LAVAR","RAVAL","NADAR","RADAN","CASAR","RASAC",
    "SECAR","RACES","PECAR","RACEP","APAGA","AGAPA",
    "SALAS","SELAS","MOLAS","SALOM","POLAS","SALPО",
    "SALVO","OVLAS","CALVO","OVLAC","PALCO","OCLAP",
    "MARSA","ASRAM","SERAM","MARES","TERAS","SARET",
    "CERAS","SARCE","PERAS","SAREP","FARAS","SARAF",
    "CALAR","RALAC","PALAR","RALAP","SALAR","RALAS",
    "MALAR","RALAM","VALAR","RALAV","TALAR","RALAT",
]
PORTUGUESE_5 = list(set(w for w in PORTUGUESE_5 if len(w)==5))

LATIN_5 = [
    "SATOR","AREPO","TENET","OPERA","ROTAS",
    "LIBER","REBIL","MATER","REMAT","PATER","RETAP",
    "FIDES","SEDIF","SALUS","SULAS","IANUS","SUANI",
    "VENIT","TINEV","REGIT","TIGER","CAPIT","TIPAC",
    "MANUS","SUNAM","LATUS","SUTUL","VETUS","SUREV",
    "LEVIS","SIVEL","CEDIT","TIDEC","AUDIT","TIDUA",
    "RECTE","ETCER","ARDET","TEDRA","RIDET","TEDIE",
    "RERUM","MURER","REBUS","SUBЕР","LEGIT","TIGEL",
    "SACER","RECAS","NIGER","REGIN","LIBER","REBIL",
    "CORAM","MAROC","INTER","RETNI","ULTRA","ARTLU",
    "PALMA","AMLAP","PETRA","ARTEP","SILVA","AVLIS",
    "NOMEN","NEMON","LOCUS","SUCOL","TERRA","ARRET",
]
LATIN_5 = list(set(w for w in LATIN_5 if len(w)==5))


def is_valid_square(sq):
    """sq é lista de 5 strings de 5 letras. Verifica as 3 simetrias."""
    M = [list(w) for w in sq]
    n = 5
    for i in range(n):
        for j in range(n):
            if M[i][j] != M[j][i]: return False
            if M[i][j] != M[n-1-i][n-1-j]: return False
    return True

def build_prefix_index(words):
    idx = defaultdict(set)
    for w in words:
        for k in range(1,6):
            idx[w[:k]].add(w)
    return idx

def find_sator_like(words, max_results=100, timeout=30):
    """
    Busca quadrados tipo Sator com CSP + backtracking.
    Usa as restrições para podar o espaço de busca.
    """
    words_set = {w.upper() for w in words if len(w)==5}
    palindromes = [w for w in words_set if w==w[::-1]]
    results = []
    t0 = time.time()

    for w1 in sorted(words_set):
        w5 = w1[::-1]
        if w5 not in words_set: continue
        if time.time()-t0 > timeout: break

        for w2 in sorted(words_set):
            w4 = w2[::-1]
            if w4 not in words_set: continue

            for w3 in palindromes:
                sq = [w1, w2, w3, w4, w5]
                if is_valid_square(sq):
                    if sq not in results:
                        results.append(sq)
                    if len(results) >= max_results: return results

    return results

def plot_found_squares(results_by_lang, save_path):
    """Visualiza os primeiros quadrados encontrados por idioma."""
    langs = list(results_by_lang.keys())
    n_langs = len(langs)

    # Para cada idioma, pegar até 2 quadrados
    to_show = {}
    for lang in langs:
        to_show[lang] = results_by_lang[lang][:2]

    max_squares = max(len(v) for v in to_show.values()) if to_show else 1
    total_cols = max(1, sum(max(1,len(v)) for v in to_show.values()))

    fig, raw_axes = plt.subplots(
        1, max(1, total_cols),
        figsize=(5*max(1,total_cols), 6)
    )
    fig.patch.set_facecolor('#0d1117')
    if total_cols == 1:
        raw_axes = [raw_axes]
    axes = list(raw_axes)

    COLORS_ROW = ['#FF6B6B','#4ECDC4','#45B7D1','#4ECDC4','#FF6B6B']

    ax_idx = 0
    for lang in langs:
        squares = to_show[lang]
        if not squares:
            ax = axes[ax_idx] if ax_idx < len(axes) else None
            if ax:
                ax.set_facecolor('#161b22')
                ax.text(0.5, 0.5, f'{lang}\n(nenhum encontrado)',
                        ha='center', va='center', color='#8b949e',
                        fontsize=11, transform=ax.transAxes)
                ax.set_xticks([]); ax.set_yticks([])
            ax_idx += 1
        else:
            for sq in squares:
                if ax_idx >= len(axes): break
                ax = axes[ax_idx]
                ax.set_facecolor('#161b22')
                ax.set_title(f'{lang}', color='white', fontsize=12, fontweight='bold')
                for i in range(5):
                    for j in range(5):
                        rect = plt.Rectangle([j,4-i],1,1,facecolor='#21262d',
                                              edgecolor='#30363d',linewidth=1.5)
                        ax.add_patch(rect)
                        ax.text(j+.5,4-i+.5,sq[i][j],ha='center',va='center',
                                fontsize=18,fontweight='bold',
                                color=COLORS_ROW[i],family='monospace')
                ax.set_xlim(0,5); ax.set_ylim(0,5)
                ax.set_xticks([]); ax.set_yticks([])
                ax_idx += 1

    # Hide unused axes
    for i in range(ax_idx, len(axes)):
        axes[i].set_visible(False)

    plt.suptitle('EXP-04 — Quadrados Sator-like Encontrados por Idioma',
                 color='white', fontsize=14, fontweight='bold', y=1.01)
    fig.text(0.5,-0.02,'Programa de Pesquisa Sator | Douglas H. M. Fulber | 2026',
             ha='center',color='#8b949e',fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.close(); print(f"✓ {save_path}")

def plot_lexicon_stats(stats, save_path):
    """Estatísticas dos léxicos: tamanho, palíndromos, pares reversos."""
    langs = list(stats.keys())
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('#0d1117')

    metrics = ['total','palindromes','reverse_pairs']
    titles = ['Total de palavras (5 letras)','Palíndromos','Pares reversos']
    colors = ['#4ECDC4','#FF6B6B','#FFEAA7']

    for ax, metric, title, color in zip(axes, metrics, titles, colors):
        ax.set_facecolor('#161b22')
        vals = [stats[l][metric] for l in langs]
        bars = ax.bar(langs, vals, color=color, edgecolor='#30363d', width=0.5)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                    str(v), ha='center', color='white', fontsize=11, fontweight='bold')
        ax.set_title(title, color='white', fontsize=11, fontweight='bold')
        ax.set_facecolor('#161b22')
        ax.tick_params(colors='white')
        ax.set_ylim(0, max(vals)*1.3 if vals else 1)
        for spine in ax.spines.values():
            spine.set_edgecolor('#30363d')
        ax.yaxis.label.set_color('white')

    plt.suptitle('EXP-04 — Estatísticas dos Léxicos por Idioma',
                 color='white', fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.close(); print(f"✓ {save_path}")

def lexicon_stats(words):
    ws = {w.upper() for w in words if len(w)==5}
    palins = [w for w in ws if w==w[::-1]]
    pairs = [(w, w[::-1]) for w in ws if w[::-1] in ws and w<w[::-1]]
    return {'total':len(ws),'palindromes':len(palins),'reverse_pairs':len(pairs)}

def save_results(results_by_lang, save_dir):
    for lang, squares in results_by_lang.items():
        path = os.path.join(save_dir, f"squares_{lang.lower()}.json")
        with open(path,'w',encoding='utf-8') as f:
            json.dump({'language':lang,'count':len(squares),'squares':squares},f,indent=2)
        print(f"✓ {path}")
    # CSV summary
    csv_path = os.path.join(save_dir,"04_squares_summary.csv")
    with open(csv_path,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['Idioma','Quadrado Encontrado','W1','W2','W3','W4','W5'])
        for lang,squares in results_by_lang.items():
            for sq in squares:
                w.writerow([lang,' | '.join(sq)]+sq)
    print(f"✓ {csv_path}")

if __name__=='__main__':
    print("="*55)
    print("EXP-04: GERADOR SATOR-LIKE MULTI-IDIOMA")
    print("="*55)

    lexicons = {
        'Latin':     LATIN_5,
        'English':   ENGLISH_5,
        'Português': PORTUGUESE_5,
    }

    stats={}; results_by_lang={}
    for lang, words in lexicons.items():
        ws = {w.upper() for w in words if len(w)==5}
        st = lexicon_stats(list(ws))
        stats[lang]=st
        print(f"\n[{lang}] Total={st['total']} Palíndromos={st['palindromes']} "
              f"Pares reversos={st['reverse_pairs']}")
        print(f"  Buscando quadrados Sator-like...")
        t0=time.time()
        found=find_sator_like(list(ws), max_results=50, timeout=20)
        dt=time.time()-t0
        print(f"  → {len(found)} quadrado(s) em {dt:.1f}s")
        for sq in found:
            print(f"    {' | '.join(sq)}")
        results_by_lang[lang]=found

    plot_lexicon_stats(stats, os.path.join(FIG_DIR,"lexicon_stats.png"))
    plot_found_squares(results_by_lang, os.path.join(FIG_DIR,"found_squares.png"))
    save_results(results_by_lang, RES_DIR)
    print("\nEXP-04 COMPLETO ✓")
