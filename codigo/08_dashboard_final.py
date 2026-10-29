"""
Paso 8 · Avance 4 (entrega final) · Dashboard final en una sola página HTML.

Pregunta que responde: ¿cuántos jóvenes de 18 a 35 años tienen síndrome metabólico sin saberlo,
qué se les escapa y por qué?

Jerarquía (de lo que se ve primero a lo que se consulta después):
  1. Título con el hallazgo y dos indicadores grandes en naranja (prevalencia y "no lo sabe").
  2. Gráfica principal: % que no lo sabe por componente, con IC 95 % (lo que requiere análisis de sangre).
  3. Gráficas de apoyo: ¿por qué no lo saben? y ¿dónde se concentra? (edad).
Filtros: sexo y categoría de IMC. Todas las cifras se recalculan en Python para cada combinación
(3 × 4 = 12 estados) y la página solo cambia entre estados ya calculados: no hay cálculos en el navegador.

Entrada: datos/procesados/nhanes_2013_2014_jovenes_clean.csv
Salida:  figuras/avance4/dashboard_final.html (autónomo: abre sin internet)
"""
import json
import numpy as np, pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import get_plotlyjs
from config import CSV_LIMPIO, RAIZ

FIG_A4 = RAIZ / 'figuras' / 'avance4'
FIG_A4.mkdir(parents=True, exist_ok=True)

# Paleta (misma que los avances 2 y 3): naranja = hallazgo, gris = contexto, tinta para el texto
NAR, NAR_CLARO, GR, GR_OSC = '#eb6834', '#f6c3ad', '#b4b3ad', '#8a8984'
T1, T2, T3, LINEA = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
FUENTE = 'Segoe UI, Inter, Arial, sans-serif'


def wilson(k, n, z=1.96):
    """Proporción e intervalo de confianza del 95 % de Wilson (1927)."""
    if n == 0:
        return dict(k=0, n=0, p=np.nan, lo=np.nan, hi=np.nan)
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return dict(k=int(k), n=int(n), p=p, lo=c - h, hi=c + h)


pct1 = lambda x: f'{x * 100:.1f} %' if x == x else '—'

d = pd.read_csv(CSV_LIMPIO)
a = d[d.tiene_acelerometro].copy()   # muestra de trabajo: 1,143

COMPONENTES = [  # mismas parejas componente–diagnóstico que el paso 2
    ('Glucosa alterada', 'c_glucosa', 'dx_glucosa', 'sangre'),
    ('HDL bajo', 'c_hdl', 'dx_colesterol', 'sangre'),
    ('Triglicéridos altos', 'c_trigliceridos', 'dx_colesterol', 'sangre'),
    ('Presión elevada', 'c_presion', 'dx_presion', 'consulta'),
    ('Cintura elevada', 'c_cintura', 'dx_sobrepeso', 'consulta'),
]


def estadisticas(s):
    """Todas las cifras del dashboard para un subconjunto de la muestra de trabajo."""
    m = s[s.sindrome_metabolico.notna()]
    sm = m[m.sindrome_metabolico == 1]
    sin_dx = sm[~sm.dx_alguno.astype(bool)]
    con_dx = sm[sm.dx_alguno.astype(bool)]
    out = {
        'n_total': len(m),
        'sindrome': wilson(len(sm), len(m)),
        'no_lo_sabe': wilson(len(sin_dx), len(sm)),
        'hiper': wilson(int(s.acido_urico_alto.sum()), len(s)),
        'hiper_sm': wilson(int(sm.acido_urico_alto.sum()), len(sm)),
        'componentes': [], 'porque': [], 'edad': [],
    }
    for etiqueta, c, dx, tipo in COMPONENTES:
        g = s[(s[c] == 1) & s[dx].notna()]
        out['componentes'].append(dict(etiqueta=etiqueta, tipo=tipo, **wilson(int((g[dx] == 0).sum()), len(g))))
    salud = lambda g: wilson(int(g.salud_autopercibida.isin(['Excelente', 'Muy buena', 'Buena']).sum()),
                             int(g.salud_autopercibida.notna().sum()))
    for etiqueta, f in [('Nunca se ha medido<br>el colesterol', lambda g: wilson(int(g.nunca_colesterol_medido.sum()), len(g))),
                        ('No tiene un lugar habitual<br>de atención médica', lambda g: wilson(int((~g.tiene_medico_habitual.astype(bool)).sum()), len(g))),
                        ('Dice tener salud buena,<br>muy buena o excelente', salud)]:
        out['porque'].append(dict(etiqueta=etiqueta, sin_dx=f(sin_dx), con_dx=f(con_dx)))
    for e in ['18-24', '25-29', '30-35']:
        g = m[m.grupo_edad == e]
        out['edad'].append(dict(etiqueta=f'{e} años', **wilson(int(g.sindrome_metabolico.sum()), len(g))))
    return out


EJE = dict(showgrid=False, zeroline=False, showline=False, ticks='', tickfont=dict(color=T2, size=12))
eje = lambda **kw: {**EJE, **kw}   # eje base + ajustes de cada gráfica
BASE = dict(template='plotly_white', font=dict(family=FUENTE, color=T2, size=12), paper_bgcolor='white',
            plot_bgcolor='white', showlegend=False, hoverlabel=dict(bgcolor='white', font=dict(family=FUENTE, color=T1)))


def fig_principal(st):
    """Gráfica principal: % que no lo sabe por componente, punto + IC 95 %."""
    comp = list(reversed(st['componentes']))           # Plotly dibuja de abajo hacia arriba
    y = [c['etiqueta'] for c in comp]
    fig = go.Figure()
    fig.add_vline(x=50, line=dict(color=GR, width=1, dash='dot'))
    for tipo, color in [('sangre', NAR), ('consulta', GR_OSC)]:
        cc = [c for c in comp if c['tipo'] == tipo and c['n'] >= 5]
        fig.add_trace(go.Scatter(
            x=[c['p'] * 100 for c in cc], y=[c['etiqueta'] for c in cc], mode='markers',
            marker=dict(size=15, color=color, line=dict(color='white', width=2)),
            error_x=dict(type='data', symmetric=False, array=[(c['hi'] - c['p']) * 100 for c in cc],
                         arrayminus=[(c['p'] - c['lo']) * 100 for c in cc], color=color, thickness=4, width=0),
            customdata=[[c['k'], c['n'], c['lo'] * 100, c['hi'] * 100] for c in cc],
            hovertemplate='<b>%{y}</b><br>%{x:.1f} % no lo sabía<br>%{customdata[0]} de %{customdata[1]} jóvenes con el valor alterado'
                          '<br>IC 95 %: %{customdata[2]:.1f}–%{customdata[3]:.1f} %<extra></extra>'))
        fig.add_trace(go.Scatter(  # valor escrito a la derecha del intervalo, sin taparlo
            x=[c['hi'] * 100 + 1.5 for c in cc], y=[c['etiqueta'] for c in cc], mode='text', hoverinfo='skip',
            text=[f"<b>{c['p'] * 100:.0f} %</b>" for c in cc], textposition='middle right', textfont=dict(size=14, color=T1)))
    poco = [c['etiqueta'] for c in comp if c['n'] < 5]
    glu = st['componentes'][0]
    if glu['n'] >= 5:
        fig.add_annotation(x=glu['p'] * 100, y='Glucosa alterada', yshift=22, xanchor='right', showarrow=False,
                           text=f"<b>{round(glu['p'] * 10)} de cada 10</b> con glucosa alterada no lo sabían",
                           font=dict(color=NAR, size=13), bgcolor='white')
    fig.add_annotation(x=50, y=1.0, yref='paper', yanchor='bottom', showarrow=False, text='la mitad',
                       font=dict(color=T3, size=11), xshift=24)
    # Separadores de grupo (texto en el margen izquierdo)
    fig.add_annotation(x=0, xref='paper', xanchor='left', y=4.55, yanchor='bottom', showarrow=False,
                       text='REQUIEREN ANÁLISIS DE SANGRE', font=dict(color=NAR, size=11))
    fig.add_annotation(x=0, xref='paper', xanchor='left', y=1.55, yanchor='bottom', showarrow=False,
                       text='SE MIDEN EN UNA CONSULTA', font=dict(color=GR_OSC, size=11))
    if poco:
        fig.add_annotation(x=1, xref='paper', xanchor='right', y=1.0, yref='paper', yanchor='bottom', showarrow=False,
                           text='Sin dato suficiente en este filtro (n < 5): ' + ', '.join(poco), font=dict(color=T3, size=11))
    fig.update_layout(**BASE, height=520, margin=dict(l=150, r=30, t=34, b=60),
                      xaxis=eje(range=[0, 110], tickvals=[0, 25, 50, 75, 100], ticktext=['0 %', '25 %', '50 %', '75 %', '100 %'],
                                 title=dict(text='De quienes tienen el valor alterado, % que nunca recibió diagnóstico (punto) e IC 95 % (línea)',
                                            font=dict(size=12, color=T2))),
                      yaxis=eje(categoryorder='array', categoryarray=y, tickfont=dict(size=13, color=T1)))
    return fig


def fig_porque(st):
    """¿Por qué no lo saben? Personas con síndrome: sin diagnóstico (naranja) frente a con diagnóstico (gris)."""
    items = list(reversed(st['porque']))
    fig = go.Figure()
    for clave, nombre, color, desplaz in [('con_dx', 'Ya sabían que tenían algún diagnóstico', GR, -0.19),
                                          ('sin_dx', 'No sabían (sin diagnóstico previo)', NAR, 0.19)]:
        v = [it[clave] for it in items]; y = [i + desplaz for i in range(len(items))]
        fig.add_trace(go.Bar(
            name=nombre, orientation='h', y=y, x=[x['p'] * 100 for x in v], marker=dict(color=color), width=0.34,
            error_x=dict(type='data', symmetric=False, array=[(x['hi'] - x['p']) * 100 for x in v],
                         arrayminus=[(x['p'] - x['lo']) * 100 for x in v], color=T2, thickness=1.2, width=3),
            customdata=[[x['k'], x['n'], x['lo'] * 100, x['hi'] * 100] for x in v],
            hovertemplate=f'<b>{nombre}</b><br>%{{x:.1f}} % (%{{customdata[0]}} de %{{customdata[1]}})'
                          '<br>IC 95 %: %{customdata[2]:.1f}–%{customdata[3]:.1f} %<extra></extra>'))
        fig.add_trace(go.Scatter(x=[(x['hi'] if x['hi'] == x['hi'] else 0) * 100 + 2 for x in v], y=y, mode='text',
                                 hoverinfo='skip', showlegend=False, text=[f"{x['p'] * 100:.0f} %" if x['n'] else '' for x in v],
                                 textposition='middle right', textfont=dict(size=12, color=T1)))
    fig.update_layout(**{**BASE, 'showlegend': True}, barmode='overlay', height=255,
                      margin=dict(l=175, r=20, t=8, b=34),
                      legend=dict(orientation='h', x=0, y=-0.1, font=dict(size=11, color=T2), traceorder='reversed'),
                      xaxis=eje(range=[0, 115], showticklabels=False),
                      yaxis=eje(tickvals=list(range(len(items))), ticktext=[it['etiqueta'] for it in items],
                                range=[-0.6, len(items) - 0.4], tickfont=dict(size=12, color=T1)))
    return fig


def fig_edad(st):
    """¿Dónde se concentra? Prevalencia de síndrome por grupo de edad, con IC 95 %."""
    e = st['edad']
    fig = go.Figure(go.Bar(
        x=[x['etiqueta'] for x in e], y=[x['p'] * 100 for x in e], marker=dict(color=[GR, GR, NAR]), width=0.55,
        error_y=dict(type='data', symmetric=False, array=[(x['hi'] - x['p']) * 100 for x in e],
                     arrayminus=[(x['p'] - x['lo']) * 100 for x in e], color=T2, thickness=1.2, width=4),
        customdata=[[x['k'], x['n'], x['lo'] * 100, x['hi'] * 100] for x in e],
        hovertemplate='<b>%{x}</b><br>%{y:.1f} % con síndrome (%{customdata[0]} de %{customdata[1]})'
                      '<br>IC 95 %: %{customdata[2]:.1f}–%{customdata[3]:.1f} %<extra></extra>'))
    fig.add_trace(go.Scatter(x=[x['etiqueta'] for x in e], y=[(x['hi'] if x['hi'] == x['hi'] else 0) * 100 for x in e],
                             mode='text', hoverinfo='skip', text=[f"<b>{x['p'] * 100:.0f} %</b>" if x['n'] else 's/d' for x in e],
                             textposition='top center', textfont=dict(size=13, color=T1), cliponaxis=False))
    top = max([x['hi'] for x in e if x['hi'] == x['hi']] + [0.3]) * 100
    fig.update_layout(**BASE, height=200, margin=dict(l=10, r=10, t=22, b=28),
                      xaxis=eje(tickfont=dict(size=12, color=T1)),
                      yaxis=eje(range=[0, top * 1.22], showticklabels=False))
    return fig


def textos(st, filtro):
    """Cifras y frases que cambian con el filtro. Con pocos casos, el texto lo advierte en lugar de afirmar."""
    s, nl, hi, hs = st['sindrome'], st['no_lo_sabe'], st['hiper'], st['hiper_sm']
    e = st['edad']; nunca, sin_med, salud = st['porque']
    ok = lambda x: x == x
    uno_de = round(1 / s['p']) if ok(s['p']) and s['p'] > 0 else None
    if nl['n'] == 0: mitad = 'ninguno tiene diagnóstico registrado'
    elif nl['lo'] > 0.5: mitad = 'más de la mitad no lo sabe'
    elif nl['hi'] < 0.5: mitad = 'menos de la mitad no lo sabe'
    else: mitad = f"{nl['p'] * 100:.0f} % no lo sabe"
    titulo = (f'Cerca de 1 de cada {uno_de} ' if uno_de else 'Ninguno de los ') + \
             ('jóvenes ya tiene síndrome metabólico' if uno_de else 'jóvenes de este grupo tiene síndrome metabólico') + \
             (f' y {mitad}' if uno_de else '')
    if filtro: titulo = f'{filtro[0].upper() + filtro[1:]}: ' + titulo[0].lower() + titulo[1:]
    pocos = min(nunca['sin_dx']['n'], nunca['con_dx']['n'])
    if pocos >= 20:
        porque_h = f"{nunca['sin_dx']['p'] * 100:.0f} % de quienes no lo sabían nunca se ha medido el colesterol"
        porque_s = (f"Frente a {nunca['con_dx']['p'] * 100:.0f} % de quienes sí lo sabían. Además, "
                    f"{salud['sin_dx']['p'] * 100:.0f} % de quienes no lo sabían dice tener buena salud.")
    else:
        porque_h = 'Muy pocos casos con síndrome en este filtro para comparar'
        porque_s = (f"{nunca['sin_dx']['n']} sin diagnóstico y {nunca['con_dx']['n']} con diagnóstico: "
                    'las proporciones son inestables (observa lo amplio de los intervalos).')
    if min(x['n'] for x in e) >= 30 and all(ok(x['p']) for x in e):
        edad_h = (f"De {e[0]['p'] * 100:.0f} % a los 18–24 años a {e[2]['p'] * 100:.0f} % a los 30–35"
                  if e[2]['p'] > e[0]['p'] else 'En este filtro no aumenta con la edad')
        edad_s = ('Aparece desde los 18 años; ' if e[0]['k'] > 0 else '') + \
                 (f"en el grupo de 30–35 la proporción es {e[2]['p'] / e[0]['p']:.1f} veces la de 18–24".replace('.', ',')
                  if e[0]['p'] > 0 and e[2]['lo'] > e[0]['hi'] else 'los intervalos se traslapan: la diferencia no es concluyente')
    else:
        edad_h = 'Pocos casos por grupo de edad en este filtro'
        edad_s = 'Las proporciones por edad son inestables; observa lo amplio de los intervalos.'
    return {
        'titulo': titulo,
        'kpi_sm': pct1(s['p']), 'kpi_sm_sub': (f'≈ 1 de cada {uno_de} · ' if uno_de else '') +
                                            f"IC 95 %: {pct1(s['lo'])}–{pct1(s['hi'])} · {s['k']:,} de {s['n']:,}",
        'kpi_nl': pct1(nl['p']), 'kpi_nl_sub': f"IC 95 %: {pct1(nl['lo'])}–{pct1(nl['hi'])} · {nl['k']:,} de {nl['n']:,}",
        'kpi_hi': pct1(hi['p']), 'kpi_hi_sub': f"Entre quienes tienen síndrome: {pct1(hs['p'])} ({hs['k']} de {hs['n']})",
        'porque_h': porque_h, 'porque_sub': porque_s, 'edad_h': edad_h, 'edad_sub': edad_s,
    }


SEXOS = ['Todos', 'Mujer', 'Hombre']
IMCS = ['Todas', 'Normal', 'Sobrepeso', 'Obesidad']
estados = {}
for sx in SEXOS:
    for imc in IMCS:
        s = a.copy()
        if sx != 'Todos': s = s[s.sexo == sx]
        if imc != 'Todas': s = s[s.cat_imc == imc]
        st = estadisticas(s)
        estados[f'{sx}|{imc}'] = {
            'principal': json.loads(pio.to_json(fig_principal(st))),
            'porque': json.loads(pio.to_json(fig_porque(st))),
            'edad': json.loads(pio.to_json(fig_edad(st))),
            'textos': textos(st, ' '.join(([{'Mujer': 'Mujeres', 'Hombre': 'Hombres'}[sx]] if sx != 'Todos' else []) +
                                              ([{'Normal': 'con IMC normal', 'Sobrepeso': 'con sobrepeso', 'Obesidad': 'con obesidad'}[imc]] if imc != 'Todas' else []))),
            'n': st['n_total'],
        }

t0 = estados['Todos|Todas']['textos']
HTML = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Síndrome metabólico silencioso en jóvenes · Dashboard final</title>
<style>
:root{{--t1:{T1};--t2:{T2};--t3:{T3};--nar:{NAR};--linea:{LINEA}}}
*{{box-sizing:border-box}} body{{margin:0;background:#fff;font-family:{FUENTE};color:var(--t1)}}
.wrap{{max-width:1320px;margin:0 auto;padding:18px 28px 10px}}
header{{display:flex;justify-content:space-between;align-items:flex-start;gap:24px}}
h1{{font-size:27px;line-height:1.2;margin:0 0 4px;font-weight:700;max-width:900px}}
.sub{{color:var(--t2);font-size:14px;margin:0}}
.filtros{{display:flex;gap:14px;align-items:flex-end;flex-shrink:0}}
.filtros label{{display:block;font-size:11px;color:var(--t3);text-transform:uppercase;letter-spacing:.04em;margin-bottom:3px}}
.filtros select{{font:inherit;font-size:14px;padding:5px 8px;border:1px solid #cfcec8;border-radius:6px;background:#fff;color:var(--t1);min-width:120px}}
.kpis{{display:grid;grid-template-columns:1.2fr 1.2fr 1fr;gap:18px;margin:16px 0 8px}}
.kpi{{border-top:3px solid var(--linea);padding:8px 0 4px}}
.kpi.acento{{border-top-color:var(--nar)}}
.kpi .v{{font-size:44px;font-weight:700;line-height:1;color:var(--nar)}}
.kpi.neutro .v{{font-size:30px;color:var(--t1)}}
.kpi .l{{font-size:15px;color:var(--t1);margin-top:4px;font-weight:600}}
.kpi .d{{font-size:12.5px;color:var(--t2);margin-top:2px}}
.grid{{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(0,1fr);gap:28px;margin-top:6px}}
.panel{{min-width:0}} .panel > div[id^=g_]{{width:100%}} #g_principal{{height:520px}} #g_porque{{height:255px}} #g_edad{{height:200px}}
.panel h2{{font-size:17px;margin:6px 0 2px;font-weight:700}}
.panel h3{{font-size:15px;margin:2px 0 0;font-weight:700}}
.panel p.q{{font-size:12px;color:var(--t3);margin:0;text-transform:uppercase;letter-spacing:.04em}}
.panel p.s{{font-size:13px;color:var(--t2);margin:2px 0 0}}
footer{{border-top:1px solid var(--linea);margin-top:6px;padding-top:7px;font-size:11.5px;color:var(--t3);line-height:1.45}}
footer a{{color:var(--t2)}}
</style></head><body><div class="wrap">
<header>
  <div><h1 id="titulo">{t0['titulo']}</h1>
  <p class="sub">Adultos de 18 a 35 años en EE. UU. · NHANES 2013–2014 · <span id="ntxt">n = {estados['Todos|Todas']['n']:,}</span> con los cinco componentes evaluables</p></div>
  <div class="filtros">
    <div><label for="f_sexo">Sexo</label><select id="f_sexo" autocomplete="off">{''.join(f'<option>{x}</option>' for x in SEXOS)}</select></div>
    <div><label for="f_imc">Categoría de IMC</label><select id="f_imc" autocomplete="off">{''.join(f'<option>{x}</option>' for x in IMCS)}</select></div>
  </div>
</header>
<section class="kpis">
  <div class="kpi acento"><div class="v" id="kpi_sm">{t0['kpi_sm']}</div><div class="l">tiene síndrome metabólico</div><div class="d" id="kpi_sm_sub">{t0['kpi_sm_sub']}</div></div>
  <div class="kpi acento"><div class="v" id="kpi_nl">{t0['kpi_nl']}</div><div class="l">de ellos no lo sabía (sin diagnóstico previo)</div><div class="d" id="kpi_nl_sub">{t0['kpi_nl_sub']}</div></div>
  <div class="kpi neutro"><div class="v" id="kpi_hi">{t0['kpi_hi']}</div><div class="l">tiene ácido úrico alto (hiperuricemia)</div><div class="d" id="kpi_hi_sub">{t0['kpi_hi_sub']}</div></div>
</section>
<section class="grid">
  <div class="panel"><p class="q">¿Qué se les escapa?</p>
    <h2>Lo que solo revela un análisis de sangre es lo que más pasa desapercibido</h2>
    <p class="s">Glucosa, HDL y triglicéridos no se ven ni se sienten; la cintura y la presión se detectan en una consulta.</p>
    <div id="g_principal"></div></div>
  <div class="panel"><p class="q">¿Por qué no lo saben? · jóvenes con síndrome</p>
    <h3 id="porque_h">{t0['porque_h']}</h3>
    <p class="s" id="porque_sub">{t0['porque_sub']}</p>
    <div id="g_porque"></div>
    <p class="q" style="margin-top:6px">¿Dónde se concentra? · % con síndrome por edad</p>
    <h3 id="edad_h">{t0['edad_h']}</h3>
    <p class="s" id="edad_sub">{t0['edad_sub']}</p>
    <div id="g_edad"></div></div>
</section>
<footer>Fuente: National Health and Nutrition Examination Survey 2013–2014 (CDC/NCHS), extraído el 1 de octubre de 2026. Criterios: síndrome metabólico de Alberti et al. (2009);
hiperuricemia &gt; 7.0 mg/dL en hombres y &gt; 5.7 mg/dL en mujeres. Proporciones sin ponderar con IC 95 % de Wilson. Diagnóstico previo autorreportado.
Diseño transversal: las diferencias son <b>asociaciones, no causas</b>. Código y datos: <a href="https://github.com/ErickNobody/nhanes-sindrome-metabolico-jovenes">github.com/ErickNobody/nhanes-sindrome-metabolico-jovenes</a></footer>
</div>
<script>{get_plotlyjs()}</script>
<script>
const E = {json.dumps(estados, ensure_ascii=False)};
const CFG = {{displaylogo:false, responsive:true, modeBarButtonsToRemove:['lasso2d','select2d','autoScale2d'], locale:'es'}};
const G = ['g_principal','g_porque','g_edad'];
function pinta(primera){{
  const k = document.getElementById('f_sexo').value + '|' + document.getElementById('f_imc').value, s = E[k];
  for (const g of G) (primera === true ? Plotly.newPlot : Plotly.react)('g_'+g.slice(2), s[g.slice(2)].data, s[g.slice(2)].layout, CFG);
  for (const [id,v] of Object.entries(s.textos)) document.getElementById(id).innerHTML = v;
  document.getElementById('ntxt').textContent = 'n = ' + s.n.toLocaleString('en-US');
  ajusta();
}}
// Vuelve a medir el ancho real de cada gráfica (algunos navegadores lo calculan antes de acomodar la cuadrícula)
function ajusta(){{ requestAnimationFrame(() => G.forEach(id => {{ const el = document.getElementById(id); if (el && el.data) Plotly.Plots.resize(el); }})); }}
document.getElementById('f_sexo').onchange = pinta; document.getElementById('f_imc').onchange = pinta;
// Si el navegador recuerda la selección anterior al recargar, se vuelve a la vista inicial
document.getElementById('f_sexo').value = 'Todos'; document.getElementById('f_imc').value = 'Todas';
pinta(true);
window.addEventListener('load', () => {{ ajusta(); setTimeout(ajusta, 400); }});
window.addEventListener('resize', ajusta);
</script></body></html>"""
(FIG_A4 / 'dashboard_final.html').write_text(HTML, encoding='utf-8')

# Validación: las cifras sin filtro deben coincidir con los pasos 2 y 7
st = estadisticas(a)
print('Síndrome:', pct1(st['sindrome']['p']), '| no lo sabe:', pct1(st['no_lo_sabe']['p']), '| hiperuricemia:', pct1(st['hiper']['p']))
print('No lo sabe por componente:', {c['etiqueta']: f"{c['k']}/{c['n']}" for c in st['componentes']})
print('ok: figuras/avance4/dashboard_final.html ·', len(estados), 'estados de filtro')
