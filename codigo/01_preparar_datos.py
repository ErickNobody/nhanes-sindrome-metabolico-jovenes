"""
Preparación de datos – Proyecto de visualización: síndrome metabólico silencioso en adultos jóvenes
=====================================================================================================
Fuente: NHANES 2013-2014 (CDC/NCHS).
        https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013
Paso 1 · Carga y limpieza.
Uso:    desde la carpeta codigo/:  python 01_preparar_datos.py
Entrada: datos/crudos/*.xpt (archivos originales, no se modifican)
Salida:  datos/procesados/nhanes_2013_2014_jovenes_clean.csv (una fila por persona, 1,730 de 18-35 años;
         la muestra de trabajo son las 1,143 con tiene_acelerometro = True)

Cómo leer los comentarios:
  [GUÍA]       valor tomado de una guía clínica o estudio publicado (referencia indicada)
  [NHANES]     significado tomado del libro de códigos de NHANES (enlace "Doc" de cada archivo)
  [CONVENCIÓN] criterio de uso habitual en estudios con estos datos
  [PROPIA]     decisión del proyecto, sin guía específica: debe declararse como limitación

Referencias:
  Alberti et al. (2009). Harmonizing the metabolic syndrome. Circulation, 120(16), 1640-1645.
  American Diabetes Association (2024). Standards of Care in Diabetes, cap. 2.
  Chen-Xu et al. (2019). Arthritis & Rheumatology, 71(6), 991-999.
  NCEP ATP III (2002). Circulation, 106(25), 3143-3421.
  CDC (2024). Adult BMI categories.
  Troiano et al. (2008). Med Sci Sports Exerc, 40(1), 181-188.
"""
import numpy as np, pandas as pd
from config import CRUDOS, CSV_LIMPIO
r = lambda f: pd.read_sas(CRUDOS / f'{f}.xpt', format='xport')

# 1. Carga de tablas ------------------------------------------------------
# Todos los archivos comparten SEQN (identificador anónimo de participante) [NHANES]
demo = r('DEMO_H')[['SEQN','RIAGENDR','RIDAGEYR','RIDRETH3','INDFMPIR','WTMEC2YR']]  # demografía y ponderador del examen
bio  = r('BIOPRO_H')[['SEQN','LBXSUA','LBXSGL','LBXSTR']]   # ácido úrico, glucosa (sin ayuno), triglicéridos
glu  = r('GLU_H')[['SEQN','LBXGLU']]                         # glucosa en ayunas (solo submuestra matutina) [NHANES]
ghb  = r('GHB_H')[['SEQN','LBXGH']]                          # HbA1c
hdl  = r('HDL_H')[['SEQN','LBDHDD']]                         # colesterol HDL
tc   = r('TCHOL_H')[['SEQN','LBXTC']]                        # colesterol total
bmx  = r('BMX_H')[['SEQN','BMXBMI','BMXWAIST']]              # IMC y cintura
bpx  = r('BPX_H')
# Presión: NHANES toma hasta 3 lecturas; se promedian para reducir el efecto de una lectura aislada [PROPIA]
bpx['PAS'] = bpx[['BPXSY1','BPXSY2','BPXSY3']].mean(axis=1)
# Una diastólica de 0 indica que no pudo medirse, se trata como faltante [NHANES]
bpx['PAD'] = bpx[['BPXDI1','BPXDI2','BPXDI3']].replace(0, np.nan).mean(axis=1)
bpx = bpx[['SEQN','PAS','PAD']]
slq = r('SLQ_H')[['SEQN','SLD010H']]                         # horas de sueño reportadas
diq = r('DIQ_H')[['SEQN','DIQ010','DIQ160','DIQ050','DIQ070']]   # diabetes / prediabetes / insulina / pastillas
bpq = r('BPQ_H')[['SEQN','BPQ020','BPQ050A','BPQ060','BPQ080','BPQ100D']]  # presión alta, medicamento, colesterol
mcq = r('MCQ_H')[['SEQN','MCQ160N','MCQ080']]                # gota, sobrepeso
huq = r('HUQ_H')[['SEQN','HUQ010','HUQ030']]                 # salud autopercibida, médico habitual
hiq = r('HIQ_H')[['SEQN','HIQ011']]                          # seguro médico

# 2. Acelerómetro: días válidos y promedios por persona -------------------
day = r('PAXDAY_H')   # una fila por persona y día
# Día válido:
#   >= 10 h de uso en vigilia (600 min)           [CONVENCIÓN] Troiano et al. (2008)
#   >= 23 h de registro (1380 min) y
#   >= 18 h de uso total vigilia+sueño (1080 min)  [PROPIA] el protocolo 2011-2014 era de 24 h;
#                                                  asegura que también se registró el sueño
day['valido'] = (day.PAXTMD >= 1380) & ((day.PAXWWMD + day.PAXSWMD) >= 1080) & (day.PAXWWMD >= 600)
# Resumen por persona con el promedio de sus días válidos [PROPIA]: los laboratorios son
# una medición por persona, así que el acelerómetro también debe quedar en un valor por persona
pa = (day[day.valido].groupby('SEQN')
      .agg(dias_validos=('valido','size'), actividad_mims=('PAXMTSD','mean'),
           sueno_min=('PAXSWMD','mean'))
      .reset_index())
pa = pa[pa.dias_validos >= 4]   # >= 4 días válidos para representar la semana típica [CONVENCIÓN] Troiano et al. (2008)

# 3. Unión y filtro 18-35 años con análisis de sangre --------------------
# Unión izquierda desde demografía para no perder personas por un dato secundario faltante [PROPIA]
df = demo
for t in [bio, glu, ghb, hdl, tc, bmx, bpx, slq, diq, bpq, mcq, huq, hiq]:
    df = df.merge(t, on='SEQN', how='left')
# Adultos jóvenes de 18 a 35 años, población de la tesis [PROPIA]
# Se exigen ácido úrico y HDL porque son el núcleo de la pregunta
df = df[(df.RIDAGEYR.between(18, 35)) & df.LBXSUA.notna() & df.LBDHDD.notna()]
df = df.merge(pa, on='SEQN', how='left')
df['tiene_acelerometro'] = df.dias_validos.notna()   # la muestra de trabajo son quienes tienen True (1,143)

# 4. Variables derivadas ---------------------------------------------------
hombre = df.RIAGENDR == 1                       # 1 = hombre, 2 = mujer [NHANES]
df['sexo'] = np.where(hombre, 'Hombre', 'Mujer')
# Grupos de edad de tamaño parecido [PROPIA]
df['grupo_edad'] = pd.cut(df.RIDAGEYR, [17, 24, 29, 35], labels=['18-24','25-29','30-35'])
# IMC: 25 sobrepeso, 30 obesidad [GUÍA] CDC (2024)
# "Normal" incluye bajo peso (<18.5) por ser pocos casos [PROPIA, declarar]
df['cat_imc'] = pd.cut(df.BMXBMI, [0, 25, 30, 100], right=False, labels=['Normal','Sobrepeso','Obesidad'])
si = lambda s: s == 1   # en los cuestionarios 1 = Sí, 2 = No, 7 = Se negó, 9 = No sabe [NHANES]

# Componentes del síndrome metabólico: definición armonizada [GUÍA] Alberti et al. (2009)
# Cintura >= 102 cm hombres / >= 88 cm mujeres: umbral AHA/NHLBI recomendado para EE. UU.
df['c_cintura'] = np.where(df.BMXWAIST.isna(), np.nan, (hombre & (df.BMXWAIST >= 102)) | (~hombre & (df.BMXWAIST >= 88)))
# Triglicéridos >= 150 mg/dL
# No se cuentan medicamentos para colesterol (BPQ100D): Alberti cuenta fármacos específicos para
# triglicéridos/HDL y NHANES solo pregunta por medicamento para colesterol en general [PROPIA]
df['c_trigliceridos'] = df.LBXSTR >= 150
# HDL < 40 mg/dL hombres / < 50 mg/dL mujeres
df['c_hdl'] = (hombre & (df.LBDHDD < 40)) | (~hombre & (df.LBDHDD < 50))
# Presión >= 130 sistólica o >= 85 diastólica, o tratamiento antihipertensivo (BPQ050A)
df['c_presion'] = np.where(df.PAS.isna() & ~si(df.BPQ050A), np.nan,
                           (df.PAS >= 130) | (df.PAD >= 85) | si(df.BPQ050A))
# Glucosa en ayunas >= 100 mg/dL, o tratamiento con insulina (DIQ050) o pastillas (DIQ070)
# Sin glucosa en ayunas se usa HbA1c >= 5.7% como sustituto [PROPIA, declarar];
# el punto de corte de HbA1c es el de prediabetes [GUÍA] American Diabetes Association (2024)
df['glucosa_fuente'] = np.where(df.LBXGLU.notna(), 'Ayunas', 'HbA1c')
df['c_glucosa'] = np.where(df.LBXGLU.notna(), df.LBXGLU >= 100, df.LBXGH >= 5.7) | si(df.DIQ050) | si(df.DIQ070)
comp = ['c_cintura','c_trigliceridos','c_hdl','c_presion','c_glucosa']
df[comp] = df[comp].astype(float)
# Solo se clasifica a quien tiene los 5 componentes evaluables (min_count=5)
df['n_componentes'] = df[comp].sum(axis=1, min_count=5)
df['sindrome_metabolico'] = np.where(df.n_componentes.isna(), np.nan, df.n_componentes >= 3)   # 3 o más de 5

# Otros marcadores
# Hiperuricemia > 7.0 mg/dL hombres / > 5.7 mg/dL mujeres [GUÍA] Chen-Xu et al. (2019)
df['acido_urico_alto'] = (hombre & (df.LBXSUA > 7)) | (~hombre & (df.LBXSUA > 5.7))
# Colesterol total >= 200 mg/dL, "limítrofe alto" [GUÍA] NCEP ATP III (2002)
df['colesterol_alto'] = df.LBXTC >= 200

# Conciencia: ¿un médico se lo había dicho? (respuesta 1 = Sí) [NHANES]
# "No lo sabe" = valor alterado medido y sin este diagnóstico [PROPIA]
df['dx_glucosa'] = si(df.DIQ010) | si(df.DIQ160)       # diabetes o prediabetes
df['dx_presion'] = si(df.BPQ020)                         # presión alta
df['dx_colesterol'] = si(df.BPQ080)                      # colesterol alto
df['dx_sobrepeso'] = si(df.MCQ080)                       # sobrepeso
df['dx_gota'] = np.where(df.MCQ160N.isna(), np.nan, si(df.MCQ160N))   # gota; solo se pregunta a 20+ años: 18-19 quedan como faltante [NHANES]
df['dx_alguno'] = df[['dx_glucosa','dx_presion','dx_colesterol']].any(axis=1)
df['nunca_colesterol_medido'] = df.BPQ060 == 2           # 2 = nunca le han medido el colesterol [NHANES]
df['salud_autopercibida'] = df.HUQ010.map({1:'Excelente',2:'Muy buena',3:'Buena',4:'Regular',5:'Mala'})  # [NHANES]
df['tiene_seguro'] = si(df.HIQ011)
df['tiene_medico_habitual'] = df.HUQ030.isin([1, 3])    # 1 = sí, 3 = más de un lugar [NHANES]

df.to_csv(CSV_LIMPIO, index=False)
print('Personas 18-35 con laboratorios:', len(df), '| con acelerómetro válido:', int(df.tiene_acelerometro.sum()))
