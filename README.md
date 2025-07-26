# Reto de Ingeniería de Datos

## 🚀 Descripción

Este proyecto implementa un **pipeline de datos por micro batches** que simula un entorno de carga progresiva de archivos CSV en una base de datos relacional, con cálculo incremental de estadísticas y control de memoria.

El objetivo es demostrar habilidades en:

- Procesamiento de datos en micro batches.
- Ingesta controlada a base de datos.
- Cálculo incremental de estadísticas sin usar agregaciones SQL en tiempo real.
- Consulta directa a base de datos para validación.
- Persistencia de estadísticas en archivos y/o base de datos.

## 🏗️ Estructura del proyecto

```
Pragma/
├── data/                      # Archivos CSV fuente (2012-1.csv a 2012-5.csv + validation.csv)
├── pipeline/
│   ├── main.py                # Pipeline principal
│   ├── db_utils.py            # Conexión a PostgreSQL
│   └── stats_tracker.py       # Clase para estadísticas incrementales
├── estadisticas.json          # Archivo de salida con estadísticas acumuladas
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

## ⚙️ Requisitos

- Python 3.12
- PostgreSQL (local o remoto)
- Conda o entorno virtual

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

## 🧪 Preparación de la base de datos

1. Crear base de datos (ejemplo: `pragma`):

```sql
CREATE DATABASE pragma;
```

2. Crear tabla principal de transacciones:

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    timestamp DATE,
    price NUMERIC,
    user_id INTEGER
);
```

3. (Opcional) Crear tabla para guardar estadísticas:

```sql
CREATE TABLE estadisticas (
    id SERIAL PRIMARY KEY,
    etapa TEXT,
    total_registros INT,
    promedio NUMERIC,
    minimo NUMERIC,
    maximo NUMERIC,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧠 Lógica del pipeline

El archivo `main.py` ejecuta los siguientes pasos:

1. Recorre todos los archivos `*.csv` excepto `validation.csv`.
2. Carga cada archivo en **micro batches de 20 filas** usando `pandas.read_csv(..., chunksize=20)`.
3. Cada chunk:
   - Limpia y convierte `timestamp` y `price`.
   - Inserta el batch en PostgreSQL usando `SQLAlchemy`.
   - Actualiza estadísticas incrementales (count, promedio, min, max).
   - Muestra progreso con `tqdm`.

4. Después de los 5 archivos:
   - Se imprime y guarda un snapshot final de las estadísticas acumuladas.
   - Se ejecuta una consulta SQL para validar conteo y agregados desde la base de datos.
5. Se repite el mismo proceso para `validation.csv`.

## 📊 Estadísticas generadas

Estadísticas calculadas y almacenadas:

| Campo     | Descripción                          |
|-----------|--------------------------------------|
| `count`   | Total de registros procesados        |
| `mean`    | Promedio incremental del `price`     |
| `min`     | Valor mínimo de `price`              |
| `max`     | Valor máximo de `price`              |

Se almacenan en:
- Consola (durante ejecución)
- `estadisticas.json`
- (Opcional) Tabla `estadisticas` en la base de datos

## 📡 Consulta directa en PostgreSQL

Para validar resultados:

```sql
SELECT 
    COUNT(price) AS total,
    AVG(price) AS promedio,
    MIN(price) AS minimo,
    MAX(price) AS maximo
FROM transactions;
```

## 📦 ¿Cómo ejecutar?

Con entorno activado y archivos CSV en la carpeta `data/`:

```bash
python pipeline/main.py
```

## ✅ Consideraciones técnicas

- La columna `price` se convierte a número.
- Los valores nulos se descartan (`dropna`) antes de insertarlos o calcular estadísticas.
- Se evita cargar todos los datos en memoria usando `chunksize`.
- El pipeline es tolerante a errores y puede ampliarse fácilmente con logging o interfaz.

## 🔚 Créditos

Desarrollado por Jimmy Ricardo Sánchez Romero como parte de un reto de ingeniería de datos para PRAGMA.
