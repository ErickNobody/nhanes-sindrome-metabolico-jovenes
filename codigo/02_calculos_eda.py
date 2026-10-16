"""
Paso 2 · Cálculos del EDA (Avance 2).
Entrada: datos/procesados/nhanes_2013_2014_jovenes_clean.csv
Salida:  datos/resumen/eda_no_lo_sabe.csv  (% con valor alterado y sin diagnóstico previo, IC 95 % de Wilson)
         Imprime la distribución de componentes, la prevalencia de síndrome y las correlaciones.
"""
import numpy as np, pandas as pd
from config import CSV_LIMPIO, RESUMEN

def wilson(k, n, z=1.96):
    """Intervalo de confianza de Wilson (1927) para una proporción k/n."""
    p = k / n; den = 1 + z*z/n; c = (p + z*z/(2*n)) / den
    h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return p, c - h, c + h

d = pd.read_csv(CSV_LIMPIO)
a = d[d.tiene_acelerometro].copy()            # muestra de trabajo: 1,143
m = a[a.sindrome_metabolico.notna()].copy()   # 1,110 con los 5 componentes evaluables

comp = m.n_componentes.value_counts().sort_index()
print('Personas por número de componentes:', comp.to_dict())
k = int(m.sindrome_metabolico.sum()); p, lo, hi = wilson(k, len(m))
print(f'Síndrome metabólico: {k} de {len(m)} = {p:.1%} (IC 95 %: {lo:.1%}–{hi:.1%})')

# "No lo sabe": valor alterado medido y sin diagnóstico previo autorreportado
filas = [('Glucosa alterada', 'c_glucosa', 'dx_glucosa'), ('HDL bajo', 'c_hdl', 'dx_colesterol'),
         ('Triglicéridos altos', 'c_trigliceridos', 'dx_colesterol'), ('Cintura elevada', 'c_cintura', 'dx_sobrepeso'),
         ('Presión elevada', 'c_presion', 'dx_presion'), ('Síndrome metabólico', 'sindrome_metabolico', 'dx_alguno')]
out = []
for etiqueta, c, dx in filas:
    s = a[(a[c] == 1) & a[dx].notna()]
    k = int((s[dx] == 0).sum()); n = len(s); p, lo, hi = wilson(k, n)
    out.append((etiqueta, k, n, p, lo, hi))
nl = pd.DataFrame(out, columns=['comp', 'k', 'n', 'p', 'lo', 'hi'])
nl.to_csv(RESUMEN / 'eda_no_lo_sabe.csv', index=False)
print(nl.round(3))

sc = a[a.BMXWAIST.notna()]
print('Spearman cintura–ácido úrico:', round(sc[['BMXWAIST', 'LBXSUA']].corr('spearman').iloc[0, 1], 2), '(n =', len(sc), ')')
print('Hiperuricemia sin / con síndrome (%):', (m.groupby('sindrome_metabolico').acido_urico_alto.mean()*100).round(1).to_dict())
