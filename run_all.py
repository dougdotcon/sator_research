"""
RUN_ALL.py — Executa todas as simulações do Sator Research Program
==================================================================
Roda EXP-01 ao EXP-05 em sequência, salva todos os resultados,
e gera um relatório final consolidado em Markdown.
"""
import subprocess, sys, os, time, json, csv

# Python com numpy/matplotlib instalado
PYTHON = r"C:\Users\DOUGLAS-PC\AppData\Local\Programs\Python\Python311\python.exe"
if not os.path.exists(PYTHON):
    PYTHON = sys.executable  # fallback
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
SIMS = os.path.join(BASE, "simulations")
RES  = os.path.join(BASE, "results")
FIG  = os.path.join(BASE, "figures")

EXPERIMENTS = [
    ("01_sator_validator.py",  "EXP-01: Validador Formal"),
    ("02_entropy_analysis.py", "EXP-02: Análise de Entropia"),
    ("03_rarity_proof.py",     "EXP-03: Prova de Raridade"),
    ("04_sator_generator.py",  "EXP-04: Gerador Multi-Idioma"),
    ("05_tamesis_bridge.py",   "EXP-05: Bridge Tamesis"),
]

def run_experiment(script, name):
    path = os.path.join(SIMS, script)
    print(f"\n{'='*60}")
    print(f"▶ {name}")
    print(f"{'='*60}")
    t0 = time.time()
    result = subprocess.run(
        [PYTHON, path],
        capture_output=False,
        text=True
    )
    dt = time.time() - t0
    status = "✅ OK" if result.returncode == 0 else "❌ ERRO"
    print(f"\n{status} — {name} — {dt:.1f}s")
    return {'name': name, 'script': script, 'status': status,
            'duration': dt, 'returncode': result.returncode}

def collect_figures():
    """Lista todas as figuras geradas."""
    figs = []
    for root, dirs, files in os.walk(FIG):
        for f in files:
            if f.endswith(('.png','.gif')):
                figs.append(os.path.join(root, f))
    return sorted(figs)

def collect_results():
    """Lista todos os arquivos de resultados."""
    rfiles = []
    for root, dirs, files in os.walk(RES):
        for f in files:
            if f.endswith(('.csv','.json')):
                rfiles.append(os.path.join(root, f))
    return sorted(rfiles)

def generate_report(run_results, save_path):
    """Gera relatório Markdown consolidado."""
    now = datetime.now().isoformat(timespec='minutes')
    figs = collect_figures()
    rfiles = collect_results()

    lines = [
        "# 📋 Relatório de Execução — Sator Research Program",
        f"\n**Data:** {now}  ",
        f"**Autor:** Douglas H. M. Fulber  ",
        f"**Status:** {'✅ Todos OK' if all(r['returncode']==0 for r in run_results) else '⚠️ Erros detectados'}",
        "\n---\n",
        "## Resumo de Execução\n",
        "| Experimento | Status | Tempo |",
        "|---|---|---|",
    ]
    for r in run_results:
        lines.append(f"| {r['name']} | {r['status']} | {r['duration']:.1f}s |")

    lines += [
        "\n---\n",
        "## Figuras Geradas\n",
    ]
    for f in figs:
        rel = os.path.relpath(f, BASE).replace('\\','/')
        ext = os.path.splitext(f)[1]
        lines.append(f"- `{rel}` {'(GIF)' if ext=='.gif' else '(PNG)'}")

    lines += [
        "\n---\n",
        "## Arquivos de Dados\n",
    ]
    for r in rfiles:
        rel = os.path.relpath(r, BASE).replace('\\','/')
        lines.append(f"- `{rel}`")

    lines += [
        "\n---\n",
        "## Próximos Passos\n",
        "1. Revisar figuras em `figures/`",
        "2. Analisar CSVs em `results/`",
        "3. Atualizar `checklist.md` com resultados",
        "4. Iniciar redação do Paper (ver `roadmap.md`)",
        "\n---\n",
        "*Gerado automaticamente por `run_all.py` — Sator Research Program*",
    ]

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"✓ Relatório: {save_path}")

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════╗")
    print("║  SATOR RESEARCH PROGRAM — Execução Completa         ║")
    print("║  Douglas H. M. Fulber | 2026                        ║")
    print("╚══════════════════════════════════════════════════════╝")
    t_start = time.time()
    run_results = []
    for script, name in EXPERIMENTS:
        r = run_experiment(script, name)
        run_results.append(r)

    total_time = time.time() - t_start
    report_path = os.path.join(BASE, "EXECUTION_REPORT.md")
    generate_report(run_results, report_path)

    print(f"\n{'='*60}")
    print(f"EXECUÇÃO TOTAL: {total_time:.1f}s")
    ok = sum(1 for r in run_results if r['returncode']==0)
    print(f"Resultados: {ok}/{len(run_results)} experimentos bem-sucedidos")
    print(f"Relatório: {report_path}")
    print(f"{'='*60}")
