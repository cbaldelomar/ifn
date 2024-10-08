"""
Modulo para el procesamiento del archivo **Ingresos brutos y flujos netos de IED**.
"""

import pandas as pd
from utils import trimestres_dict


def procesar_datos(file_path: str):
    """
    Procesa el archivo especificado y devuelve un DataFrame con los datos
    del indicador **Inversión Extranjera Directa - Flujos netos**.

    :param file_path: Path absoluto del archivo a procesar (e.g. c:/path/to/file.xls)

    :return: DataFrame procesado.
    :rtype: pandas DataFrame
    """

    # Cargar los datos del reporte en un DataFrame,
    # omitiendo las primeras cuatro filas del encabezado
    df_data = pd.read_excel(file_path, skiprows=4)

    # Eliminar columnas que no contengan valores
    df_data.dropna(axis=1, how="all", inplace=True)

    # Eliminar filas que no contengan valores
    df_data.dropna(how="all", inplace=True)

    # Filtrar solo las filas que contienen valores en la columna 'Trimestre'
    df_data = df_data[~df_data["Trimestre"].isna()]

    # Convertir a valor numérico la columna 'Año', forzando a NaN cuando no es número
    df_data["Año"] = pd.to_numeric(df_data["Año"], errors="coerce")

    # Rellenar los valores NaN de la columna ´Año´
    df_data["Año"] = df_data["Año"].ffill()

    # Convertir a entero la columna 'Año'
    df_data["Año"] = df_data["Año"].astype(int)

    # Reemplazar el valor de la columna Trimestre por el mes del corte
    df_data["Trimestre"] = df_data["Trimestre"].str.replace("Trim", "").str.strip()
    df_data["Trimestre"] = df_data["Trimestre"].map(trimestres_dict)

    # Renombrar columnas 'Año' y 'Trimestre'
    df_data.rename(columns={"Año": "ANIO", "Trimestre": "MES"}, inplace=True)

    # Usar la función melt para hacer unpivot de los valores del indicador
    df_melt = pd.melt(
        df_data,
        # Columnas a conservar sin alterar
        id_vars=["ANIO", "MES"],
        # # Columnas a hacerle unpivot (si no se especifica se toman todas las columnas)
        # value_vars=["Flujos netos"],
        # Nombre de la columna que recibirá los nombres de las columnas especificadas en value_vars
        var_name="INDICADOR",
        # Nombre de la columna que recibirá los valores de las columnas especificadas en value_vars
        value_name="VALOR",
    )

    # Asignarle un nombre al indicador
    df_melt["INDICADOR"] = "Inversión Extranjera Directa - " + df_melt["INDICADOR"]

    # Pasar la columna 'Valor' de millones a valores netos
    df_melt["VALOR"] = df_melt["VALOR"] * 1_000_000

    # Agregar columnas requeridas
    df_melt["ORIGEN"] = "BCN"
    df_melt["INSTITUCION"] = "NICARAGUA"

    # Ordenar las columnas a devolver
    df_melt = df_melt[["ORIGEN", "INSTITUCION", "INDICADOR", "ANIO", "MES", "VALOR"]]

    return df_melt
