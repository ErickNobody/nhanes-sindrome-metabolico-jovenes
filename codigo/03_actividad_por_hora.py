"""
Paso 3 · Perfil de actividad por hora del día (acelerómetro), con y sin síndrome metabólico.
Entrada: datos/crudos/PAXHR_H.xpt (descargar con 00_descargar_nhanes.py), PAXDAY_H.xpt, PAXHD_H.xpt
         y la tabla limpia.
Salida:  datos/resumen/eda_actividad_por_hora.csv (promedio e IC 95 % por hora y grupo)
Nota: el repositorio ya incluye esta salida, así que las gráficas pueden regenerarse sin descargar PAXHR_H.
"""
import numpy as np, pandas as pd
from config import CRUDOS, CSV_LIMPIO, RESUMEN

d = pd.read_csv(CSV_LIMPIO)
m = d[d.tiene_acelerometro & d.sindrome_metabolico.notna()][['SEQN', 'sindrome_metabolico']]
ids = set(m.SEQN)

# Días válidos (mismo criterio que en el paso 1)
day = pd.read_sas(CRUDOS / 'PAXDAY_H.xpt', format='xport')
day['valido'] = (day.PAXTMD >= 1380) & ((day.PAXWWMD + day.PAXSWMD) >= 1080) & (day.PAXWWMD >= 600)
day['dia'] = day.PAXDAYD.str.decode('ascii').astype(int) if day.PAXDAYD.dtype == object else day.PAXDAYD.astype(int)
validos = set(zip(day.SEQN[day.valido], day.dia[day.valido]))

# Hora de inicio del registro de cada persona (PAXFTIME, hh:mm:ss)
hd = pd.read_sas(CRUDOS / 'PAXHD_H.xpt', format='xport'); hd = hd[hd.SEQN.isin(ids)]
hd['t0'] = hd.PAXFTIME.str.decode('ascii').apply(lambda s: int(s[:2])*3600 + int(s[3:5])*60 + int(s[6:8]))
t0 = dict(zip(hd.SEQN, hd.t0))

partes = []
for ch in pd.read_sas(CRUDOS / 'PAXHR_H.xpt', format='xport', chunksize=200000):
    ch = ch[ch.SEQN.isin(ids)]
    if ch.empty:
        continue
    ch = ch.assign(dia=ch.PAXDAYH.str.decode('ascii').astype(int))
    ch = ch[[(s, dd) in validos for s, dd in zip(ch.SEQN, ch.dia)]]
    ch = ch[(ch.PAXTMH == 60) & ((ch.PAXWWMH + ch.PAXSWMH) >= 45)]          # hora completa y >= 45 min de uso
    # Hora del día = inicio del registro + muestras a 80 Hz transcurridas (PAXSSNHP)
    ch['hora'] = ((ch.SEQN.map(t0) + ch.PAXSSNHP/80)//3600).astype(int) % 24
    partes.append(ch[['SEQN', 'hora', 'PAXMTSH']])
h = pd.concat(partes)
pp = h.groupby(['SEQN', 'hora']).PAXMTSH.mean().div(60).rename('mims_min').reset_index()   # MIMS por minuto
pp = pp.merge(m, on='SEQN')
g = pp.groupby(['sindrome_metabolico', 'hora']).mims_min.agg(['mean', 'std', 'count']).reset_index()
g['lo'] = g['mean'] - 1.96*g['std']/np.sqrt(g['count']); g['hi'] = g['mean'] + 1.96*g['std']/np.sqrt(g['count'])
g.to_csv(RESUMEN / 'eda_actividad_por_hora.csv', index=False)
print('Personas por grupo:', pp.groupby('sindrome_metabolico').SEQN.nunique().to_dict())
