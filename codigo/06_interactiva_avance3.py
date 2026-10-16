"""
Paso 6 · Avance 3 · Visualización INTERACTIVA (Plotly).
Reconstruye la figura 3 del Avance 2 (cintura vs. ácido úrico, color = síndrome, un panel por sexo)
como página web interactiva:
  - Hover: ficha de cada persona (edad, IMC, componentes alterados, hiperuricemia, si ya tenía diagnóstico).
  - Botones por grupo de edad: ¿el patrón aparece desde los 18 años?
  - Clic en la leyenda: aislar a quienes tienen o no tienen síndrome.
  - Zoom y desplazamiento (barra de herramientas de Plotly) para examinar la zona de los cortes clínicos.
Entrada: tabla limpia · Salida: figuras/avance3/interactiva_cintura_acido_urico.html
"""
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import CSV_LIMPIO, FIG_A3

NAR = '#eb6834'; GR = '#a3a29b'; T1 = '#0b0b0b'; T2 = '#52514e'; T3 = '#8a8984'
d = pd.read_csv(CSV_LIMPIO)
m = d[d.tiene_acelerometro & d.sindrome_metabolico.notna() & d.BMXWAIST.notna()].copy()

nombres = {'c_cintura': 'cintura', 'c_trigliceridos': 'triglicéridos', 'c_hdl': 'HDL bajo',
           'c_presion': 'presión', 'c_glucosa': 'glucosa'}
m['cuales'] = m.apply(lambda r: ', '.join(v for k, v in nombres.items() if r[k] == 1) or 'ninguno', axis=1)
m['sabia'] = np.where(m.sindrome_metabolico == 1, np.where(m.dx_alguno, 'Sí, tenía algún diagnóstico', 'No, sin diagnóstico previo'), '—')
m['hiper'] = np.where(m.acido_urico_alto, 'Sí', 'No')
m['n_comp'] = m.n_componentes.astype(int)

fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=.06,
                    subplot_titles=('Mujeres · corte de cintura 88 cm · hiperuricemia > 5.7 mg/dL',
                                    'Hombres · corte de cintura 102 cm · hiperuricemia > 7.0 mg/dL'))
edades = ['18-24', '25-29', '30-35']
trazas = []   # (edad, sexo, síndrome) para construir la visibilidad de los botones
hover = ('<b>%{customdata[0]}, %{customdata[1]} años</b><br>'
         'Cintura: %{x:.1f} cm · Ácido úrico: %{y:.1f} mg/dL<br>'
         'IMC: %{customdata[2]:.1f} kg/m²<br>'
         'Componentes alterados: %{customdata[3]} de 5 (%{customdata[4]})<br>'
         'Hiperuricemia: %{customdata[5]}<br>'
         '¿Sabía que tenía síndrome?: %{customdata[6]}<extra></extra>')
for col, sexo in [(1, 'Mujer'), (2, 'Hombre')]:
    for sm, color, etiqueta in [(0, GR, 'Sin síndrome metabólico'), (1, NAR, 'Con síndrome metabólico')]:
        for e in edades:
            s = m[(m.sexo == sexo) & (m.sindrome_metabolico == sm) & (m.grupo_edad == e)]
            fig.add_trace(go.Scatter(
                x=s.BMXWAIST, y=s.LBXSUA, mode='markers', name=etiqueta, legendgroup=etiqueta,
                showlegend=(col == 1 and e == '18-24'),
                marker=dict(color=color, size=7 if sm else 6, opacity=.9 if sm else .55, line=dict(width=0)),
                customdata=np.stack([s.sexo, s.RIDAGEYR.astype(int), s.BMXBMI, s.n_comp, s.cuales, s.hiper, s.sabia], axis=-1),
                hovertemplate=hover), row=1, col=col)
            trazas.append((e, sexo, sm))

# Cortes clínicos por sexo (Alberti et al., 2009; Chen-Xu et al., 2019)
for col, wc, ua in [(1, 88, 5.7), (2, 102, 7.0)]:
    fig.add_vline(x=wc, line=dict(color=T2, dash='dash', width=1), row=1, col=col)
    fig.add_hline(y=ua, line=dict(color=T2, dash='dash', width=1), row=1, col=col)

def titulo(sub):
    k = int(sub.sindrome_metabolico.sum()); n = len(sub)
    return (f'<b>El síndrome metabólico se concentra donde cintura y ácido úrico están altos</b>'
            f'<br><span style="font-size:13px;color:{T2}">{n:,} jóvenes; {k} con síndrome ({k/n:.1%}). '
            f'Pasa el cursor sobre un punto para ver la ficha de la persona.</span>').replace(',', ' ')
botones = [dict(label='Todas las edades', method='update',
                args=[{'visible': [True]*len(trazas)}, {'title.text': titulo(m)}])]
for e in edades:
    botones.append(dict(label=f'{e} años', method='update',
                        args=[{'visible': [t[0] == e for t in trazas]}, {'title.text': titulo(m[m.grupo_edad == e])}]))
fig.update_layout(
    title=dict(text=titulo(m), x=.01, y=.97, font=dict(size=18, color=T1)),
    template='plotly_white', height=660, margin=dict(t=150, l=70, r=30, b=130),
    font=dict(family='Arial', color=T2),
    legend=dict(orientation='h', x=1, xanchor='right', y=1.13, title_text='Clic para mostrar u ocultar: '),
    updatemenus=[dict(type='buttons', direction='right', x=0, xanchor='left', y=1.14, buttons=botones,
                      showactive=True, bgcolor='white', bordercolor=GR, font=dict(size=12))],
    hoverlabel=dict(bgcolor='white', font=dict(color=T1)))
fig.update_xaxes(title_text='Circunferencia de cintura (cm)', range=[55, 165])
fig.update_yaxes(title_text='Ácido úrico en sangre (mg/dL)', range=[1, 11], row=1, col=1)
fig.add_annotation(text='Fuente: NHANES 2013–2014 (CDC/NCHS), extraído el 1 de octubre de 2026. Adultos de 18 a 35 años con los cinco componentes evaluables.<br>'
                        'Líneas punteadas: cortes clínicos por sexo (Alberti et al., 2009; Chen-Xu et al., 2019). Asociación, no causalidad.',
                   xref='paper', yref='paper', x=0, y=-.22, showarrow=False, xanchor='left', align='left',
                   font=dict(size=11, color=T3))
fig.write_html(FIG_A3 / 'interactiva_cintura_acido_urico.html', include_plotlyjs=True, full_html=True,
               config={'displaylogo': False, 'showTips': False, 'locale': 'es', 'toImageButtonOptions': {'format': 'png', 'scale': 2,
                       'filename': 'cintura_acido_urico_vista_filtrada'}})
print('ok', len(m), 'personas,', len(trazas), 'trazas')
