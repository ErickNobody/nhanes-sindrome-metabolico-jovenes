# Síndrome metabólico silencioso e hiperuricemia en adultos jóvenes (NHANES 2013–2014)

Proyecto de la materia **Visualización de datos** · Maestría en Inteligencia Artificial, TecNM campus Aguascalientes.
Autor: Erick Israel Rodríguez Zavala.

**Pregunta:** ¿qué tan frecuente es que un adulto joven (18 a 35 años) tenga alterados los componentes del síndrome metabólico, o el ácido úrico, sin haber recibido un diagnóstico?

**Hallazgo principal:** en esta muestra, 9 de cada 10 jóvenes con glucosa alterada, HDL bajo o triglicéridos altos no lo sabían; lo que solo revela un análisis de sangre es lo que más pasa desapercibido.

---

## Visualizaciones

| Avance | Visualización | Archivo |
|---|---|---|
| 2 · EDA | 5 gráficas (univariada, bivariada, multivariada, temporal, proporciones) | `figuras/avance2/` |
| 3 · Estática | Porcentaje que no lo sabe por componente, con IC 95 % | `figuras/avance3/estatica_no_lo_sabe.png` |
| 3 · Interactiva | Cintura vs. ácido úrico por sexo, con ficha al pasar el cursor, filtro por edad y leyenda clicable | `figuras/avance3/interactiva_cintura_acido_urico.html` |
| 3 · BI | Tablero en Tableau Public con KPI, filtros y tooltips | [Ver tablero](https://public.tableau.com/app/profile/erick.israel.rodriguez.zavala/viz/SindromemetabolicosilenciosojovenesNHANES_/Dashboard1) |
| 4 · Final | Dashboard final: indicadores con IC 95 %, qué se escapa, por qué no lo saben y dónde se concentra; filtros por sexo e IMC | `figuras/avance4/dashboard_final.html` |

**Dashboard final en línea:** [https://ericknobody.github.io/nhanes-sindrome-metabolico-jovenes/](https://ericknobody.github.io/nhanes-sindrome-metabolico-jovenes/)

**Ver la gráfica interactiva en línea:** [https://ericknobody.github.io/nhanes-sindrome-metabolico-jovenes/figuras/avance3/interactiva_cintura_acido_urico.html](https://ericknobody.github.io/nhanes-sindrome-metabolico-jovenes/figuras/avance3/interactiva_cintura_acido_urico.html)
Para verla en local, descarga el archivo `.html` y ábrelo con cualquier navegador (no requiere instalar nada).

**Recorrido completo, con explicaciones:** [`notebooks/proyecto_nhanes_sindrome_metabolico.ipynb`](notebooks/proyecto_nhanes_sindrome_metabolico.ipynb) (carga → limpieza → EDA → visualizaciones finales).

---

## Datos

- **Fuente:** National Health and Nutrition Examination Survey (NHANES) 2013–2014, CDC / National Center for Health Statistics.
  https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013
- **Fecha de extracción:** 1 de octubre de 2026.
- **Archivos usados (17):** DEMO_H, BIOPRO_H, GLU_H, GHB_H, HDL_H, TCHOL_H, BMX_H, BPX_H, SLQ_H, DIQ_H, BPQ_H, MCQ_H, HUQ_H, HIQ_H, PAXDAY_H, PAXHD_H, PAXHR_H. Se unen por `SEQN`.
- **Tabla limpia:** `datos/procesados/nhanes_2013_2014_jovenes_clean.csv` (1,730 jóvenes con laboratorios; 1,143 con acelerómetro válido = muestra de trabajo).
- **Diccionario de datos:** [`docs/diccionario_datos.md`](docs/diccionario_datos.md).

> `PAXHR_H.xpt` (≈145 MB) supera el límite de 100 MB por archivo de GitHub y no está en el repositorio. Solo lo necesita el paso 3; su resultado ya está en `datos/resumen/eda_actividad_por_hora.csv`, así que todas las gráficas se regeneran sin él. Para rehacer el paso 3, ejecuta el paso 0 y se descargará.

---

## Estructura

```
├── codigo/                     scripts numerados, se ejecutan en orden
│   ├── config.py               rutas del proyecto (todos los scripts las importan)
│   ├── 00_descargar_nhanes.py  descarga los .xpt que falten desde el CDC
│   ├── 01_preparar_datos.py    unión, filtros y variables derivadas → tabla limpia
│   ├── 02_calculos_eda.py      prevalencias e IC de Wilson → datos/resumen/eda_no_lo_sabe.csv
│   ├── 03_actividad_por_hora.py acelerómetro por hora → datos/resumen/eda_actividad_por_hora.csv
│   ├── 04_graficas_avance2.py  5 gráficas del EDA
│   ├── 05_estatica_avance3.py  visualización estática mejorada
│   ├── 06_interactiva_avance3.py visualización interactiva (HTML)
│   ├── 07_datos_tableau.py     Excel con etiquetas en español para Tableau
│   └── 08_dashboard_final.py   dashboard final (Avance 4) en una página HTML
├── datos/
│   ├── crudos/                 archivos originales de NHANES, sin modificar
│   ├── procesados/             tabla limpia (una fila por persona)
│   ├── resumen/                tablas agregadas que alimentan las gráficas
│   └── tableau/                datos para el tablero (xlsx + csv)
├── figuras/avance2/ · figuras/avance3/ · figuras/avance4/
├── index.html                  página de inicio de GitHub Pages: abre el dashboard final
├── notebooks/                  cuaderno con todo el flujo documentado
└── docs/diccionario_datos.md
```

Principios: los datos crudos no se modifican; la lógica vive solo en los scripts (el cuaderno los llama, no copia código); cada decisión de limpieza lleva en el código su origen (**[GUÍA]**, **[NHANES]**, **[CONVENCIÓN]** o **[PROPIA]**); ningún paso es manual.

---

## Cómo reproducirlo

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
cd codigo
python 00_descargar_nhanes.py      # opcional: solo descarga lo que falte (PAXHR_H)
python 01_preparar_datos.py
python 02_calculos_eda.py
python 03_actividad_por_hora.py    # opcional: requiere PAXHR_H.xpt
python 04_graficas_avance2.py
python 05_estatica_avance3.py
python 06_interactiva_avance3.py
python 07_datos_tableau.py
python 08_dashboard_final.py
```

O abre el cuaderno y ejecuta todas las celdas: `jupyter notebook notebooks/proyecto_nhanes_sindrome_metabolico.ipynb`.

Validación: `07_datos_tableau.py` imprime los valores que debe mostrar el tablero sin filtros (n = 1,143; síndrome 18.6 %; de ellos, 57.8 % sin diagnóstico; hiperuricemia 16.5 %).

---

## Criterios clínicos

| Variable | Corte | Referencia |
|---|---|---|
| Síndrome metabólico | ≥ 3 de 5 componentes | Alberti et al. (2009) |
| Cintura | ≥ 102 cm H / ≥ 88 cm M | Alberti et al. (2009) |
| Triglicéridos | ≥ 150 mg/dL | Alberti et al. (2009) |
| HDL | < 40 mg/dL H / < 50 mg/dL M | Alberti et al. (2009) |
| Presión | ≥ 130/85 mmHg o tratamiento | Alberti et al. (2009) |
| Glucosa | ayunas ≥ 100 mg/dL (o HbA1c ≥ 5.7 %) o tratamiento | Alberti et al. (2009); ADA (2024) |
| Hiperuricemia | > 7.0 mg/dL H / > 5.7 mg/dL M | Chen-Xu et al. (2019) |
| Día válido de acelerómetro | ≥ 10 h de uso en vigilia; persona con ≥ 4 días | Troiano et al. (2008) |

## Limitaciones

Proporciones sin ponderar (describen la muestra, no a la población de EE. UU.); diagnóstico previo autorreportado; glucosa en ayunas solo en una submuestra (HbA1c como sustituto); diseño transversal (asociación, no causalidad).

## Licencia

Código bajo licencia MIT. Los datos de NHANES son de dominio público (CDC/NCHS).
