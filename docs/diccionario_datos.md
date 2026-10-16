# Diccionario de datos

Tabla: `datos/procesados/nhanes_2013_2014_jovenes_clean.csv` · una fila por persona · 1,730 filas (18–35 años con ácido úrico y HDL) · 59 columnas.
La muestra de trabajo son las filas con `tiene_acelerometro = True` (1,143). Los códigos de cuestionario siguen el libro de códigos de NHANES: 1 = Sí, 2 = No, 7 = Se negó, 9 = No sabe.

Las columnas en MAYÚSCULAS vienen tal cual de NHANES; las de minúsculas son derivadas en `codigo/01_preparar_datos.py`, donde cada regla indica su origen.

| Columna | Descripción | Tipo | Archivo de origen | Faltantes en muestra de trabajo |
|---|---|---|---|---|
| `SEQN` | Identificador anónimo del participante (llave de unión) | entero | DEMO_H | 0 |
| `RIAGENDR` | Sexo (1 = hombre, 2 = mujer) | categórica nominal | DEMO_H | 0 |
| `RIDAGEYR` | Edad en años al momento del examen | numérica discreta | DEMO_H | 0 |
| `RIDRETH3` | Raza/etnia (códigos NHANES 1–7) | categórica nominal | DEMO_H | 0 |
| `INDFMPIR` | Razón ingreso familiar / línea de pobreza (0–5) | numérica continua | DEMO_H | 77 |
| `WTMEC2YR` | Ponderador del examen MEC a 2 años (no se usa: proporciones sin ponderar) | numérica continua | DEMO_H | 0 |
| `LBXSUA` | Ácido úrico en suero (mg/dL) | numérica continua | BIOPRO_H | 0 |
| `LBXSGL` | Glucosa en suero sin ayuno (mg/dL) | numérica continua | BIOPRO_H | 0 |
| `LBXSTR` | Triglicéridos en suero (mg/dL) | numérica continua | BIOPRO_H | 0 |
| `LBXGLU` | Glucosa en ayunas (mg/dL); solo submuestra matutina | numérica continua | GLU_H | 614 |
| `LBXGH` | Hemoglobina glucosilada HbA1c (%) | numérica continua | GHB_H | 2 |
| `LBDHDD` | Colesterol HDL (mg/dL) | numérica continua | HDL_H | 0 |
| `LBXTC` | Colesterol total (mg/dL) | numérica continua | TCHOL_H | 0 |
| `BMXBMI` | Índice de masa corporal (kg/m²) | numérica continua | BMX_H | 8 |
| `BMXWAIST` | Circunferencia de cintura (cm) | numérica continua | BMX_H | 20 |
| `PAS` | Presión sistólica, promedio de hasta 3 lecturas (mmHg) | numérica continua | BPX_H (derivada) | 20 |
| `PAD` | Presión diastólica, promedio de hasta 3 lecturas; 0 = faltante (mmHg) | numérica continua | BPX_H (derivada) | 20 |
| `SLD010H` | Horas de sueño reportadas en días laborales | numérica | SLQ_H | 0 |
| `DIQ010` | ¿Un médico le dijo que tiene diabetes? (1 sí, 2 no, 3 limítrofe, 7/9 sin respuesta) | categórica | DIQ_H | 0 |
| `DIQ160` | ¿Le dijeron que tiene prediabetes? | categórica | DIQ_H | 29 |
| `DIQ050` | ¿Usa insulina actualmente? | categórica | DIQ_H | 0 |
| `DIQ070` | ¿Toma pastillas para bajar la glucosa? | categórica | DIQ_H | 1082 |
| `BPQ020` | ¿Le dijeron que tiene presión alta? | categórica | BPQ_H | 0 |
| `BPQ050A` | ¿Toma medicamento para la presión alta? | categórica | BPQ_H | 1094 |
| `BPQ060` | ¿Alguna vez le midieron el colesterol? (2 = nunca) | categórica | BPQ_H | 113 |
| `BPQ080` | ¿Le dijeron que tiene colesterol alto? | categórica | BPQ_H | 0 |
| `BPQ100D` | ¿Toma medicamento para el colesterol? | categórica | BPQ_H | 1120 |
| `MCQ160N` | ¿Le dijeron que tiene gota? (solo se pregunta a 20+ años) | categórica | MCQ_H | 198 |
| `MCQ080` | ¿Le dijeron que tiene sobrepeso? | categórica | MCQ_H | 0 |
| `HUQ010` | Salud autopercibida (1 excelente … 5 mala) | categórica ordinal | HUQ_H | 0 |
| `HUQ030` | ¿Tiene un lugar habitual de atención médica? (1 sí, 2 no, 3 más de uno) | categórica | HUQ_H | 0 |
| `HIQ011` | ¿Tiene seguro médico? | categórica | HIQ_H | 0 |
| `dias_validos` | Días válidos de acelerómetro (≥ 4 para entrar a la muestra) | numérica discreta | PAXDAY_H (derivada) | 0 |
| `actividad_mims` | Actividad diaria promedio en MIMS (días válidos) | numérica continua | PAXDAY_H (derivada) | 0 |
| `sueno_min` | Minutos de sueño detectados por día (promedio de días válidos) | numérica continua | PAXDAY_H (derivada) | 0 |
| `tiene_acelerometro` | True si tiene ≥ 4 días válidos (muestra de trabajo) | booleana | derivada | 0 |
| `sexo` | Hombre / Mujer | categórica nominal | derivada de RIAGENDR | 0 |
| `grupo_edad` | 18-24, 25-29, 30-35 | categórica ordinal | derivada de RIDAGEYR | 0 |
| `cat_imc` | Normal (<25), Sobrepeso (25–29.9), Obesidad (≥30) | categórica ordinal | derivada de BMXBMI | 8 |
| `c_cintura` | Componente cintura alterada (1/0; vacío si falta) | binaria | derivada | 20 |
| `c_trigliceridos` | Componente triglicéridos ≥ 150 mg/dL (1/0) | binaria | derivada | 0 |
| `c_hdl` | Componente HDL bajo (1/0) | binaria | derivada | 0 |
| `c_presion` | Componente presión ≥ 130/85 o tratamiento (1/0) | binaria | derivada | 16 |
| `glucosa_fuente` | Ayunas o HbA1c: qué medición se usó para la glucosa | categórica | derivada | 0 |
| `c_glucosa` | Componente glucosa alterada o tratamiento (1/0) | binaria | derivada | 0 |
| `n_componentes` | Número de componentes alterados (0–5; vacío si alguno no es evaluable) | numérica discreta (ordinal) | derivada | 33 |
| `sindrome_metabolico` | 1 si n_componentes ≥ 3 | binaria | derivada | 33 |
| `acido_urico_alto` | Hiperuricemia: > 7.0 mg/dL H / > 5.7 mg/dL M | binaria | derivada | 0 |
| `colesterol_alto` | Colesterol total ≥ 200 mg/dL | binaria | derivada | 0 |
| `dx_glucosa` | Diagnóstico previo de diabetes o prediabetes | binaria | derivada | 0 |
| `dx_presion` | Diagnóstico previo de presión alta | binaria | derivada | 0 |
| `dx_colesterol` | Diagnóstico previo de colesterol alto | binaria | derivada | 0 |
| `dx_sobrepeso` | Le dijeron que tiene sobrepeso | binaria | derivada | 0 |
| `dx_gota` | Diagnóstico previo de gota (vacío en 18–19 años) | binaria | derivada | 198 |
| `dx_alguno` | Algún diagnóstico previo: glucosa, presión o colesterol | binaria | derivada | 0 |
| `nunca_colesterol_medido` | Nunca le han medido el colesterol | binaria | derivada | 0 |
| `salud_autopercibida` | Excelente, Muy buena, Buena, Regular, Mala | categórica ordinal | derivada de HUQ010 | 1 |
| `tiene_seguro` | Tiene seguro médico | binaria | derivada | 0 |
| `tiene_medico_habitual` | Tiene lugar habitual de atención | binaria | derivada | 0 |

## Datos para Tableau (`datos/tableau/nhanes_tableau.xlsx`)

**Hoja `personas`** (1,143 filas): `ID` (= SEQN), `Sexo`, `Edad`, `Grupo de edad`, `Categoría IMC` (incluye «Sin dato»), `IMC`, `Cintura cm`, `Ácido úrico mg/dL`, `Componentes alterados` (0–5), `Cuáles componentes`, `Síndrome metabólico` (Sí/No/No evaluable), `Hiperuricemia` (Sí/No), `Indicador síndrome` (1/0, vacío si no evaluable), `Indicador síndrome sin diagnóstico` (1/0 solo para quienes tienen síndrome), `Indicador hiperuricemia` (1/0), `Sabía que tenía síndrome`.

**Hoja `componentes`** (1,539 filas): una fila por persona y componente alterado con dato de diagnóstico. `ID`, `Componente`, `Tipo de medición` (Requiere análisis de sangre / Se mide en una consulta), `Orden` (para ordenar las barras), `Indicador sin diagnóstico` (1 = no lo sabía).

Parejas componente → diagnóstico usadas para «no lo sabe»: glucosa → diabetes o prediabetes; HDL y triglicéridos → colesterol alto; presión → presión alta; cintura → sobrepeso; síndrome → cualquiera de glucosa, presión o colesterol.
