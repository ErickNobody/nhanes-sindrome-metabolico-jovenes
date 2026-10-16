"""
Paso 5 · Avance 3 · Visualización ESTÁTICA mejorada (matplotlib).
Reconstruye la figura 5 del Avance 2 ("¿qué tanto pasa desapercibido cada componente?") para un
documento PDF: agrupa por cómo se detecta cada alteración, resalta con contraste el hallazgo
principal, anota la conclusión y agrega una ficha de contexto (fuente, n, método, limitaciones).
Entrada: datos/resumen/eda_no_lo_sabe.csv · Salida: figuras/avance3/estatica_no_lo_sabe.png
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import RESUMEN, FIG_A3

NAR = '#eb6834'; GR = '#a3a29b'; T1 = '#0b0b0b'; T2 = '#52514e'; T3 = '#8a8984'; GRID = '#e6e5e0'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10.5, 'axes.edgecolor': T3,
                     'xtick.color': T2, 'ytick.color': T2, 'figure.facecolor': 'white'})

nl = pd.read_csv(RESUMEN / 'eda_no_lo_sabe.csv').set_index('comp')
grupos = [('Requieren análisis de sangre', ['Glucosa alterada', 'HDL bajo', 'Triglicéridos altos'], NAR),
          ('Se miden en una consulta', ['Presión elevada', 'Cintura elevada'], GR),
          ('Diagnóstico combinado', ['Síndrome metabólico'], GR)]

fig, ax = plt.subplots(figsize=(10, 6.2))
fig.subplots_adjust(top=.80, bottom=.21, left=.27, right=.74)
YT = None
y = 0; yt, yl, cabeceras = [], [], []
for nombre, filas, col in grupos:
    cabeceras.append((y - .55, nombre))
    for f in filas:
        r = nl.loc[f]
        ax.hlines(y, r.lo*100, r.hi*100, color=col, lw=3, zorder=2)
        ax.plot(r.p*100, y, 'o', ms=10, color=col, markeredgecolor='white', markeredgewidth=1, zorder=3)
        tr = ax.get_yaxis_transform()
        ax.text(1.03, y, f'{r.p:.0%}'.replace('%', ' %'), va='center', fontsize=11.5, fontweight='bold',
                color=NAR if col == NAR else T2, clip_on=False, transform=tr)
        ax.text(1.22, y, f'{int(r.k)} de {int(r.n)}', va='center', fontsize=9.5, color=T3, clip_on=False, transform=tr)
        yt.append(y); yl.append(f); y += 1
    y += .9                                   # separación entre grupos (proximidad, Gestalt)
for yy, nombre in cabeceras:
    ax.text(-0.52, yy, nombre.upper(), ha='left', va='center', fontsize=8.5, color=T3, fontweight='bold',
            transform=ax.get_yaxis_transform(), clip_on=False)
ax.set_yticks(yt); ax.set_yticklabels(yl, fontsize=11, color=T1)
ax.set_ylim(y - .6, -1.1)
ax.set_xlim(0, 100); ax.set_xticks(range(0, 101, 25)); ax.set_xticklabels([f'{v} %' for v in range(0, 101, 25)])
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
ax.tick_params(axis='y', length=0)
ax.axvline(50, color=T3, ls='--', lw=1, zorder=1)
ax.text(50.8, y - .75, 'la mitad', fontsize=8.5, color=T3)
ax.set_xlabel('Personas con el valor alterado que nunca recibieron diagnóstico (%, proporción con IC 95 %)', color=T2)
ax.text(1.03, -1.0, 'NO LO SABE', fontsize=8, color=T3, fontweight='bold', clip_on=False, transform=ax.get_yaxis_transform())
ax.text(1.22, -1.0, 'CASOS', fontsize=8, color=T3, fontweight='bold', clip_on=False, transform=ax.get_yaxis_transform())
# Anotación del hallazgo
ax.annotate('Lo que solo revela un análisis de sangre\nes lo que más pasa desapercibido',
            xy=(82, 1), xytext=(4, 1), fontsize=10, color=NAR, va='center',
            bbox=dict(fc='white', ec='none', pad=2),
            arrowprops=dict(arrowstyle='->', color=NAR, lw=1.3))
fig.text(.015, .965, '9 de cada 10 jóvenes con glucosa alterada no lo saben', fontsize=15, fontweight='bold', color=T1, va='top')
fig.text(.015, .905, 'Porcentaje de jóvenes de 18 a 35 años con cada valor alterado que nunca recibió un diagnóstico.\n'
         'Punto = estimación; línea = intervalo de confianza del 95 %.', fontsize=10.5, color=T2, va='top')
fig.text(.015, .015, 'Fuente: NHANES 2013–2014 (CDC/NCHS), extraído el 1 de octubre de 2026. Muestra: 1,143 jóvenes con laboratorios y acelerómetro válido.\n'
         'IC de Wilson (1927); proporciones sin ponderar. Diagnóstico previo autorreportado. Criterios: Alberti et al. (2009).',
         fontsize=8.3, color=T3, va='bottom')
fig.savefig(FIG_A3 / 'estatica_no_lo_sabe.png', dpi=200)
print('ok')
