"""
Paso 4 · Las 5 visualizaciones del Avance 2 (EDA), versión documentada.
Entrada: tabla limpia y datos/resumen/*.csv · Salida: figuras/avance2/fig1…fig5.png
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
NAR='#eb6834'; AZ='#2a78d6'; GR='#b4b3ad'; T1='#0b0b0b'; T2='#52514e'; T3='#8a8984'; GRID='#e6e5e0'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.edgecolor':T3,'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,
  'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.color':GRID,'grid.linewidth':.8,'axes.axisbelow':True,'figure.facecolor':'white'})
FUENTE='Fuente: NHANES 2013–2014 (CDC/NCHS), adultos de 18 a 35 años. Elaboración propia.'
def encabezado(fig,t,s):
    fig.text(.012,.975,t,fontsize=13.5,fontweight='bold',color=T1,va='top')
    fig.text(.012,.915,s,fontsize=10,color=T2,va='top')
def pie(fig,t): fig.text(.012,.015,t,fontsize=8.5,color=T3,va='bottom')
from config import CSV_LIMPIO, RESUMEN, FIG_A2
d=pd.read_csv(CSV_LIMPIO); a=d[d.tiene_acelerometro].copy(); m=a[a.sindrome_metabolico.notna()].copy()

# 1 Univariada -----------------------------------------------------------
c=m.n_componentes.value_counts().sort_index(); n=len(m)
fig,ax=plt.subplots(figsize=(8,4.8)); fig.subplots_adjust(top=.80,bottom=.2,left=.1,right=.97)
cols=[GR if k<3 else NAR for k in c.index]
b=ax.bar(c.index,c.values,color=cols,width=.72,zorder=2)
for k,v in c.items(): ax.text(k,v+6,f'{v}\n({v/n:.1%})'.replace('.',','),ha='center',va='bottom',fontsize=9,color=T2)
ax.set_xticks(range(6)); ax.set_xlabel('Número de componentes del síndrome metabólico alterados (variable ordinal, 0 a 5)')
ax.set_ylabel('Personas (frecuencia)'); ax.set_ylim(0,max(c)*1.25); ax.grid(axis='x',visible=False)
ax.axvline(2.5,color=T3,ls='--',lw=1); ax.text(2.55,max(c)*1.17,'3 o más = síndrome metabólico',fontsize=9,color=T2)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=GR,label='Sin síndrome (0–2 componentes)'),Patch(color=NAR,label='Con síndrome (3–5 componentes)')],frameon=False,loc='upper right',bbox_to_anchor=(1,.9),fontsize=9)
sm=int(m.sindrome_metabolico.sum())
encabezado(fig,f'1 de cada 5 jóvenes ya tiene síndrome metabólico ({sm/n:.1%})'.replace('.',','),
  'Distribución del número de componentes alterados (cintura, triglicéridos, HDL, presión, glucosa). n = '+f'{n:,}'.replace(',',' '))
pie(fig,FUENTE+' Criterios: Alberti et al. (2009).')
fig.savefig(FIG_A2/'fig1_componentes.png',dpi=200); plt.close()

# 2 Bivariada ------------------------------------------------------------
sc=a[a.BMXWAIST.notna()]; n2=len(sc); rho=sc[['BMXWAIST','LBXSUA']].corr('spearman').iloc[0,1]
fig,ax=plt.subplots(figsize=(8,5)); fig.subplots_adjust(top=.81,bottom=.17,left=.1,right=.97)
ax.scatter(sc.BMXWAIST,sc.LBXSUA,s=14,color=AZ,alpha=.35,linewidths=0,zorder=2,label=f'Una persona (n = {n2:,})'.replace(',',' '))
co=np.polyfit(sc.BMXWAIST,sc.LBXSUA,1); xs=np.linspace(sc.BMXWAIST.min(),sc.BMXWAIST.max(),50)
ax.plot(xs,np.polyval(co,xs),color=T1,lw=2,zorder=3,label='Tendencia lineal (solo describe, no implica causa)')
ax.set_xlabel('Circunferencia de cintura (cm, variable continua)'); ax.set_ylabel('Ácido úrico en sangre (mg/dL, variable continua)')
ax.set_xlim(55,165); ax.set_ylim(1,11); ax.legend(frameon=False,loc='upper left',fontsize=9)
ax.text(162,1.4,f'Correlación de Spearman ρ = {rho:.2f}'.replace('.',','),ha='right',fontsize=9.5,color=T2)
encabezado(fig,'A mayor cintura, mayor ácido úrico','Relación entre circunferencia de cintura y ácido úrico; cada punto es una persona')
pie(fig,FUENTE)
fig.savefig(FIG_A2/'fig2_cintura_acido_urico.png',dpi=200); plt.close()

# 3 Multivariada ---------------------------------------------------------
sm3=m[m.BMXWAIST.notna()]
fig,axs=plt.subplots(1,2,figsize=(9,5),sharey=True); fig.subplots_adjust(top=.78,bottom=.17,left=.08,right=.98,wspace=.08)
for ax,sexo,wc,ua in zip(axs,['Mujer','Hombre'],[88,102],[5.7,7.0]):
    s=sm3[sm3.sexo==sexo]; no=s[s.sindrome_metabolico==0]; si=s[s.sindrome_metabolico==1]
    ax.scatter(no.BMXWAIST,no.LBXSUA,s=13,color=GR,alpha=.55,linewidths=0,zorder=2,label='Sin síndrome')
    ax.scatter(si.BMXWAIST,si.LBXSUA,s=16,color=NAR,alpha=.85,linewidths=0,zorder=3,label='Con síndrome')
    ax.axvline(wc,color=T2,ls='--',lw=1); ax.axhline(ua,color=T2,ls='--',lw=1)
    ax.text(wc+1.5,10.6,f'cintura ≥ {wc} cm',fontsize=8.5,color=T2,bbox=dict(fc='white',ec='none',pad=1))
    ax.text(57,ua+.2,f'hiperuricemia > {ua} mg/dL'.replace('.',','),fontsize=8.5,color=T2,zorder=5,bbox=dict(fc='white',ec='none',pad=1,alpha=.85))
    ax.set_title(f'{"Mujeres" if sexo=="Mujer" else "Hombres"} (n = {len(s)}; con síndrome: {len(si)})',fontsize=10.5,color=T1,loc='left')
    ax.set_xlim(55,165); ax.set_ylim(1,11.2); ax.set_xlabel('Circunferencia de cintura (cm)')
axs[0].set_ylabel('Ácido úrico en sangre (mg/dL)')
axs[1].legend(frameon=False,loc='lower right',fontsize=9,markerscale=1.6)
encabezado(fig,'El síndrome se concentra donde cintura y ácido úrico están altos',
  'Cintura vs. ácido úrico, color según síndrome metabólico y un panel por sexo (4 variables). Líneas: cortes clínicos por sexo')
pie(fig,FUENTE+' Cortes: Alberti et al. (2009); Chen-Xu et al. (2019).')
fig.savefig(FIG_A2/'fig3_multivariada.png',dpi=200); plt.close()

# 4 Temporal -------------------------------------------------------------
g=pd.read_csv(RESUMEN/'eda_actividad_por_hora.csv')
fig,ax=plt.subplots(figsize=(8.5,4.8)); fig.subplots_adjust(top=.80,bottom=.2,left=.09,right=.97)
for v,col,lab in [(0,AZ,'Sin síndrome (n = 904)'),(1,NAR,'Con síndrome (n = 206)')]:
    s=g[g.sindrome_metabolico==v]
    ax.fill_between(s.hora,s.lo,s.hi,color=col,alpha=.18,linewidth=0)
    ax.plot(s.hora,s['mean'],color=col,lw=2,label=lab,marker='o',ms=3.5)
ax.set_xticks(range(0,24,2)); ax.set_xticklabels([f'{h}:00' for h in range(0,24,2)],fontsize=9)
ax.set_xlim(0,23); ax.set_ylim(0,18); ax.set_xlabel('Hora del día (variable temporal, reloj de 24 h)')
ax.set_ylabel('Actividad promedio (MIMS por minuto)')
ax.legend(frameon=False,loc='upper left',fontsize=9,title='Línea = promedio · banda = IC 95 %',title_fontsize=8.5)
encabezado(fig,'El reloj casi no distingue a quien tiene síndrome metabólico',
  'Perfil promedio de actividad por hora registrado por el acelerómetro de muñeca (días válidos)')
pie(fig,FUENTE+'\nMIMS: unidad de movimiento del acelerómetro, independiente del dispositivo (John et al., 2019).')
fig.savefig(FIG_A2/'fig4_temporal.png',dpi=200); plt.close()

# 5 Incertidumbre --------------------------------------------------------
nl=pd.read_csv(RESUMEN/'eda_no_lo_sabe.csv').sort_values('p')
fig,ax=plt.subplots(figsize=(8.5,4.8)); fig.subplots_adjust(top=.78,bottom=.17,left=.22,right=.78)
y=np.arange(len(nl))
ax.hlines(y,nl.lo*100,nl.hi*100,color=NAR,lw=2.5,zorder=2)
ax.plot(nl.p*100,y,'o',color=NAR,ms=8,zorder=3,markeredgecolor='white',markeredgewidth=.8)
for yi,r in zip(y,nl.itertuples()):
    ax.text(101.5,yi,f'{r.p:.0%}  ({r.k} de {r.n})'.replace('.',','),va='center',fontsize=9,color=T2,clip_on=False)
ax.set_yticks(y); ax.set_yticklabels(nl.comp,fontsize=10,color=T1)
ax.set_xlim(0,100); ax.set_xticks(range(0,101,25)); ax.set_xticklabels([f'{v}%' for v in range(0,101,25)])
ax.axvline(50,color=T3,ls='--',lw=1); ax.text(50.8,len(nl)-.45,'la mitad',fontsize=8.5,color=T3)
ax.set_xlabel('% con el valor alterado que nunca recibió diagnóstico (proporción)'); ax.grid(axis='y',visible=False)
ax.set_ylim(-.6,len(nl)-.3)
encabezado(fig,'La mayoría de quienes tienen glucosa o lípidos alterados no lo sabe',
  'Punto = porcentaje estimado; línea = intervalo de confianza del 95 % (Wilson).\nA la derecha: personas sin diagnóstico de cada total con el valor alterado')
pie(fig,FUENTE+' Diagnóstico previo autorreportado.')
fig.savefig(FIG_A2/'fig5_no_lo_sabe.png',dpi=200); plt.close()
print('ok')
