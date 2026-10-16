"""
Paso 7 · Avance 3 · Datos para el tablero de Tableau.
Tableau trabaja mejor con campos ya etiquetados (texto en español en lugar de códigos 1/2) y con
indicadores 1/0, porque el PROMEDIO de un indicador 1/0 es directamente un porcentaje.

Entrada: datos/procesados/nhanes_2013_2014_jovenes_clean.csv
Salida:  datos/tableau/nhanes_tableau.xlsx  (dos hojas que se relacionan por ID)
           - personas:     una fila por joven (1,143)
           - componentes:  una fila por componente alterado con dato de diagnóstico (formato largo)
         datos/tableau/personas.csv y componentes.csv (mismo contenido, para consulta en GitHub)

Regla clave: los indicadores quedan VACÍOS cuando no aplican (p. ej. "síndrome sin diagnóstico" en
alguien sin síndrome). Tableau ignora los vacíos al promediar, así que PROM([indicador]) da el mismo
porcentaje y el mismo denominador que el EDA del paso 2 (se verifica al final).
"""
import numpy as np, pandas as pd
from config import CSV_LIMPIO, TABLEAU

d = pd.read_csv(CSV_LIMPIO)
a = d[d.tiene_acelerometro].copy()            # muestra de trabajo: 1,143

def texto(s, si='Sí', no='No', vacio='No evaluable'):
    return np.where(s.isna(), vacio, np.where(s == 1, si, no))

nombres = {'c_cintura': 'cintura', 'c_trigliceridos': 'triglicéridos', 'c_hdl': 'HDL bajo',
           'c_presion': 'presión', 'c_glucosa': 'glucosa'}

# ---- Hoja 1: personas ------------------------------------------------------------------
p = pd.DataFrame({
    'ID': a.SEQN.astype(int),
    'Sexo': a.sexo,
    'Edad': a.RIDAGEYR.astype(int),
    'Grupo de edad': a.grupo_edad.astype(str) + ' años',
    'Categoría IMC': a.cat_imc.astype(object).fillna('Sin dato'),
    'IMC': a.BMXBMI.round(1),
    'Cintura cm': a.BMXWAIST.round(1),
    'Ácido úrico mg/dL': a.LBXSUA.round(1),
    'Componentes alterados': a.n_componentes,          # 0–5; vacío si no hay los 5 evaluables
    'Cuáles componentes': a.apply(lambda r: ', '.join(v for k, v in nombres.items() if r[k] == 1) or 'ninguno', axis=1),
    'Síndrome metabólico': texto(a.sindrome_metabolico),
    'Hiperuricemia': texto(a.acido_urico_alto.astype(float)),
})
p['Indicador síndrome'] = a.sindrome_metabolico                                   # 1/0, vacío si no evaluable
p['Indicador síndrome sin diagnóstico'] = np.where(a.sindrome_metabolico == 1,
                                                   (~a.dx_alguno.astype(bool)).astype(float), np.nan)
p['Indicador hiperuricemia'] = a.acido_urico_alto.astype(float)
p['Sabía que tenía síndrome'] = np.where(a.sindrome_metabolico == 1,
                                         np.where(a.dx_alguno, 'Sí, tenía algún diagnóstico', 'No, sin diagnóstico previo'),
                                         'No aplica')
p = p.sort_values('ID')

# ---- Hoja 2: componentes (formato largo) ------------------------------------------------
# Mismas parejas componente–diagnóstico que el paso 2
filas = [('Glucosa alterada', 'c_glucosa', 'dx_glucosa', 'Requiere análisis de sangre', 1),
         ('HDL bajo', 'c_hdl', 'dx_colesterol', 'Requiere análisis de sangre', 2),
         ('Triglicéridos altos', 'c_trigliceridos', 'dx_colesterol', 'Requiere análisis de sangre', 3),
         ('Presión elevada', 'c_presion', 'dx_presion', 'Se mide en una consulta', 4),
         ('Cintura elevada', 'c_cintura', 'dx_sobrepeso', 'Se mide en una consulta', 5)]
largo = []
for etiqueta, c, dx, tipo, orden in filas:
    s = a[(a[c] == 1) & a[dx].notna()]
    largo.append(pd.DataFrame({'ID': s.SEQN.astype(int), 'Componente': etiqueta, 'Tipo de medición': tipo,
                               'Orden': orden, 'Indicador sin diagnóstico': (s[dx] == 0).astype(int)}))
comp = pd.concat(largo, ignore_index=True)

# ---- Guardar --------------------------------------------------------------------------------
with pd.ExcelWriter(TABLEAU / 'nhanes_tableau.xlsx') as w:
    p.to_excel(w, sheet_name='personas', index=False)
    comp.to_excel(w, sheet_name='componentes', index=False)
p.to_csv(TABLEAU / 'personas.csv', index=False, encoding='utf-8-sig')
comp.to_csv(TABLEAU / 'componentes.csv', index=False, encoding='utf-8-sig')

# ---- Validación: los números que debe mostrar Tableau sin filtros --------------------------
print('Jóvenes:', len(p))
print(f"% síndrome: {p['Indicador síndrome'].mean():.1%} (n = {p['Indicador síndrome'].notna().sum()})")
print(f"% con síndrome que no lo sabe: {p['Indicador síndrome sin diagnóstico'].mean():.1%} "
      f"(n = {p['Indicador síndrome sin diagnóstico'].notna().sum()})")
print(f"% hiperuricemia: {p['Indicador hiperuricemia'].mean():.1%}")
print(comp.groupby(['Orden', 'Componente'])['Indicador sin diagnóstico'].agg(['sum', 'count', 'mean']).round(3))
print(p['Componentes alterados'].value_counts().sort_index().to_dict())
