"""
Modulo para guardar indicadoes en la base de datos\n
- Depende del paquete `python-dotenv` para cargar variables de entorno
necesarias para conectarse a SQL:\n
    pip install python-dotenv
"""

import os
from dotenv import load_dotenv
import pyodbc
import pandas as pd

# Cargar las variables desde el archivo .env
load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

driver = "{ODBC Driver 17 for SQL Server}"

# Conectarse a sql server
conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={database};
UID={username};
PWD={password}"""


def _cargar_data(df: pd.DataFrame):
    """
    Carga la información del DataFrame en la tabla Staging.Datos

    :param df: DataFrame con los datos a insertar
    """

    table = "Staging.Datos"

    # Insertar en la tabla
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Limpiando la tabla
        print("Limpiando tabla de carga")
        cursor.execute(f"TRUNCATE TABLE {table}")

        conn.commit()

        if df.empty:
            print("El DataFrame está vacío!")
            print("No se insertaron registros en la base de datos.")
            return False

        print("Cargando registros")
        # Convertir elk data frame en una lista de tuplas
        values = [tuple(x) for x in df.to_numpy()]

        insert_query = f"""
            INSERT INTO {table}(Origen, Institucion, Indicador, Anio, Mes, Valor)
            VALUES(?, ?, ?, ?, ?, ?)"""

        cursor.executemany(insert_query, values)

        conn.commit()

        # print("Registros insertados:", cursor.rowcount)
        print("Registros cargados:", df.shape[0])

        return True
    except Exception as e:
        print("Error al cargar datos:", e)
        return False
    finally:
        # Cerrar la conexión
        if conn:
            conn.close()


def _actualizar_dw():
    """
    Actualiza los datos del DW
    """

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print("Actualizando dimensiones")
        cursor.execute("EXEC dbo.uspFill_DimOrigen")
        cursor.execute("EXEC dbo.uspFill_DimInstitucion")
        cursor.execute("EXEC dbo.uspFill_DimIndicador")
        cursor.execute("EXEC dbo.uspFill_DimPeriodo")

        conn.commit()

        print("Actualizando FT")
        cursor.execute("EXEC dbo.uspFill_FTValor")

        conn.commit()
    except Exception as e:
        print("Error al actualizar DW:", e)
    finally:
        # Cerrar la conexión
        if conn:
            conn.close()


def actualizar(df: pd.DataFrame):
    """
    Actualiza la BD con la información del DataFrame.

    :param df: DataFrame con los datos a cargar
    """

    cargar = _cargar_data(df)

    if not cargar:
        return

    _actualizar_dw()
