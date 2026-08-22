import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def S_amdahl(N, p):
    return 1.0/((1-p)+p/N)

N = np.linspace(1, 8, 400)
ps = [0.0, 0.25, 0.5, 0.75, 1.0]
labels = ["p=0.00 (0% paralelizable)", "p=0.25", "p=0.50", "p=0.75", "p=1.00 (100% paralelizable)"]
styles = ["-", "--", "-.", ":", "-"]

fig, ax = plt.subplots(figsize=(6.3, 4.4), dpi=300)

for p, lab, st in zip(ps, labels, styles):
    ax.plot(N, S_amdahl(N, p), st, lw=1.6, label=lab, color="0.25" if p not in (0.0,1.0) else ("black" if p==0.0 else "0.5"))

# Sombrear la región factible de Amdahl para N in [1,8]: S in [1, N]
ax.fill_between(N, 1, N, color="tab:blue", alpha=0.08, label="Región factible de Amdahl (S∈[1,N])")

# Punto medido T1 (N=4, S=0.1711), commit d9ce0e6
N_T1, S_T1 = 4, 0.1711384544085274
ax.plot([N_T1], [S_T1], marker="o", markersize=8, color="tab:red", zorder=5,
        label=f"T1 medido (N=4, S={S_T1:.3f})")
ax.annotate("T1 — Filtrado\n(medido, fuera de la\nregión factible)",
            xy=(N_T1, S_T1), xytext=(4.5, 0.55),
            arrowprops=dict(arrowstyle="->", color="tab:red", lw=1.2),
            fontsize=8.5, color="tab:red")

ax.axhline(1.0, color="black", lw=0.8, alpha=0.5)
ax.set_xlim(1, 8)
ax.set_ylim(0, 8)
ax.set_xlabel("N (unidades de procesamiento / executors)")
ax.set_ylabel("Speedup S(N)")
ax.set_title("Curva teórica de Amdahl vs. speedup medido de T1 (Filtrado)")
ax.legend(fontsize=7, loc="upper left", framealpha=0.9)
ax.grid(alpha=0.25)

fig.tight_layout()
fig.savefig("fig_speedup_T1.png", dpi=300)
print("ok")
