"""Rutas del proyecto. Todos los scripts las importan para no depender de la carpeta desde donde se ejecutan."""
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
CRUDOS = RAIZ / 'datos' / 'crudos'            # archivos originales de NHANES (.xpt), sin modificar
PROCESADOS = RAIZ / 'datos' / 'procesados'    # tabla limpia, una fila por persona
RESUMEN = RAIZ / 'datos' / 'resumen'          # tablas agregadas que alimentan las gráficas
TABLEAU = RAIZ / 'datos' / 'tableau'          # tabla con etiquetas en español para Tableau
FIG_A2 = RAIZ / 'figuras' / 'avance2'
FIG_A3 = RAIZ / 'figuras' / 'avance3'
CSV_LIMPIO = PROCESADOS / 'nhanes_2013_2014_jovenes_clean.csv'
for p in (PROCESADOS, RESUMEN, TABLEAU, FIG_A2, FIG_A3):
    p.mkdir(parents=True, exist_ok=True)
