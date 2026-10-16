"""
Paso 0 · Descarga de los archivos originales de NHANES 2013-2014 (CDC/NCHS).

El repositorio ya incluye 16 de los 17 archivos en datos/crudos/. El archivo por hora del
acelerómetro (PAXHR_H.xpt, ~138 MB) excede el límite de 100 MB de GitHub, así que este script
lo descarga (y cualquier otro que falte) desde el sitio oficial del CDC.

Fuente: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013
Fecha de extracción usada en el proyecto: 1 de octubre de 2026 (datos históricos: no cambian).
"""
import urllib.request
from config import CRUDOS

BASE = 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/{}.xpt'
ARCHIVOS = ['DEMO_H', 'BIOPRO_H', 'GLU_H', 'GHB_H', 'HDL_H', 'TCHOL_H', 'BMX_H', 'BPX_H',
            'PAXHD_H', 'PAXDAY_H', 'PAXHR_H', 'SLQ_H', 'DIQ_H', 'BPQ_H', 'MCQ_H', 'HUQ_H', 'HIQ_H']

if __name__ == '__main__':
    CRUDOS.mkdir(parents=True, exist_ok=True)
    for a in ARCHIVOS:
        destino = CRUDOS / f'{a}.xpt'
        if destino.exists():
            print(f'{a}: ya existe')
            continue
        print(f'{a}: descargando…')
        urllib.request.urlretrieve(BASE.format(a), destino)
    print('Listo. Archivos en', CRUDOS)
