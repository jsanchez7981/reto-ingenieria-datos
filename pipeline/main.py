import os
import pandas as pd
import json
from tqdm import tqdm
from sqlalchemy import text
from db_utils import get_engine
from stats_tracker import StatsTracker
from datetime import datetime

# Carpeta de data
DATA_FOLDER = 'data'
CHUNK_SIZE = 20 # tamaño de bacth

# Definimos función para procesar archivos
def process_file(file_path, engine, stats_tracker):
    print(f"Procesando archivo: {file_path}")

    total_rows = sum(1 for _ in open(file_path)) - 1
    total_chunks = total_rows // CHUNK_SIZE + (1 if total_rows % CHUNK_SIZE > 0 else 0)

    # Ciclo para cargar data
    for chunk in tqdm(pd.read_csv(file_path, chunksize=CHUNK_SIZE), total=total_chunks, desc=f"Cargando {os.path.basename(file_path)}"):

        # Convertir la fecha en un formato que pueda reconocer PSQL
        chunk['timestamp']=pd.to_datetime(chunk['timestamp'],format='%m/%d/%Y')
        chunk['price'] = pd.to_numeric(chunk['price'], errors='coerce')
        chunk = chunk.dropna(subset=['price'])

        # Insertar en la db
        chunk.to_sql('transactions',con=engine, if_exists='append',index=False)

        # Actualizar estadisticas
        for price in (chunk['price']):
            stats_tracker.update(price)

        print(f"Estadística actuales: {stats_tracker.snapshot()}")

def show_db(engine):
    print("\n Consultando la base de datos")
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                COUNT(price) AS total,
                AVG(price) AS promedio,
                MIN(price) AS minimo,
                MAX(price) as maximo
            FROM transactions;
    """))
    row = result.fetchone()
    print(f"Filas totales: {row.total}")
    print(f"Promedio: {round(row.promedio,2)}")
    print(f"Mínimo: {row.minimo}")
    print(f"Máximo: {row.maximo}")

def save_stats(stact: dict,etapa='final', filename='estadisticas.json'):
    registros = {
        'etapa': etapa,
        'timestamp': datetime.now().isoformat(),
        **stact
    }

    # Leer archivo si existe
    if os.path.exists(filename):
        with open(filename,'r') as file:
            data = json.load(file)
    else:
        data=[]

    # Agregar las estadisticas a data
    data.append(registros)

    # Escribimos los datos en el archivo
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


# función main
def main():
    engine= get_engine()
    stats_tracker= StatsTracker()

    # Obtener lista de archivos (excepto validation.csv)
    files = sorted([
        f for f in os.listdir(DATA_FOLDER)
        if f.endswith('.csv') and 'validation' not in f
    ])

    for filename in files:
        full_path= os.path.join(DATA_FOLDER,filename)
        process_file(full_path,engine,stats_tracker)

    print("\n Estadísticas después de cargar los 5 archivos:")
    print(stats_tracker.snapshot())
    save_stats(stats_tracker.snapshot(),etapa="Post-lote")

    # Cargar archivo de validación
    validation_file= os.path.join(DATA_FOLDER,'validation.csv')
    if os.path.exists(validation_file):
        print("\n Procesando archivo de validación...")
        process_file(validation_file,engine,stats_tracker)

        print("\n Estadísticas después del archivo de validación...")
        print(stats_tracker.snapshot())
        show_db(engine)
        save_stats(stats_tracker.snapshot(),etapa="Post-validation")

    else:
        print("\n Archivo de validación no encontrado.")


if __name__ == '__main__':
    main()
