"""
Modulo para el Procesamiento del Archivo **Exportaciones FOB: mercancías por sector económico**.
"""

import pandas as pd
from utils import meses_dict


def procesar_datos(file_path):
    """
    Función para limpiar los datos de **Exportaciones FOB: mercancías por sector económico** y
    transformarlos en un DataFrame adecuado.

    :param file_path: Ruta del archivo excel descargado.
    :return: DataFrame procesado con las columnas ORIGEN, INSTITUCION, INDICADOR, ANIO, MES y VALOR.
    :rtype: pd.DataFrame
    """

    df_data = pd.read_excel(file_path, skiprows=4)

    # Eliminar columnas que no contengan valores
    df_data.dropna(axis=1, how="all", inplace=True)

    # # Eliminar la primera columna
    # df_data = df_data.drop(df_data.columns[0], axis=1)

    # ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    # Eliminar filas que no contengan valores
    df_data = df_data.dropna(how="all")

    # Resetear indices
    df_data = df_data.reset_index(drop=True)

    # # Filtrar para verificar si la columna contiene valores no nulos (NaN)
    # df_filtrado = df_data[df_data["Unnamed: 4"].notna()]

    df_data = df_data.rename(columns={"Unnamed: 0": "Año y mes"})

    # Seleccionar las columnas que se van a trabajar
    df_data = df_data[["Año y mes", "Agropecuarios"]]

    # Eliminar filas que no contengan valores
    df_data = df_data.dropna(how="all")

    # Crear la columna 'MES' con datos de la columna 'Año y mes'
    df_data["MES"] = df_data["Año y mes"]

    # Actualizar la columna 'MES' con el número del mes mapeando contra el diccionario de meses
    df_data["MES"] = df_data["MES"].map(meses_dict)

    # Eliminar cualquier fila donde el año sea NaN (si existiera)
    df_data = df_data.dropna(subset=["Año y mes"])

    # df_data["MES"] = df_data["MES"].astype(int)

    # # Crear la columna 'Año' extrayendo sólo los años de la columna 'Año y mes'
    # # Asumiendo que el año siempre está en la primera fila de un grupo y que las filas de los meses siguen a la fila del año
    # df_data["Año"] = df_data["Año y mes"].apply(
    #     lambda x: x if isinstance(x, int) else None
    # )

    # df_data["ANIO"] = df_data["Año y mes"].str.strip().str[:4]

    df_data["ANIO"] = df_data["Año y mes"].astype(str)
    df_data["ANIO"] = df_data["ANIO"].str[:4]

    # # Convertir a valor numérico la columna 'Año', forzando a NaN cuando no es número
    df_data["ANIO"] = pd.to_numeric(df_data["ANIO"], errors="coerce")

    # Rellenar los años en las filas de los meses con los valores de la fila superior
    df_data["ANIO"] = df_data["ANIO"].ffill()

    # Reemplazar los valores de 'MES' con 12.0 donde el año es menor a 2006 y 'MES' es NaN
    df_data.loc[(df_data["ANIO"] < 2006) & (df_data["MES"].isna()), "MES"] = 12

    # Eliminar filas donde la columna 'MES' sea NaN
    df_data = df_data.dropna(subset=["MES"])

    # Convertir columnas a filas usando pd.melt
    df_melt = pd.melt(
        df_data,
        id_vars=["ANIO", "MES"],  # Usamos la columna 'Año' y 'MES'
        value_vars=[
            "Agropecuarios"
        ],  # Asegúrate de que 'Bienes de consumo' esté en df_data
        var_name="INDICADOR",  # Nombre de la columna que recibirá los nombres de las columnas especificadas en value_vars
        value_name="VALOR",  # Nombre de la columna que recibirá los valores de las columnas especificadas en value_vars
    )

    # Agregar columnas adicionales
    df_melt["ORIGEN"] = "BCN"
    df_melt["INSTITUCION"] = "NICARAGUA"
    df_melt["INDICADOR"] = "Exportaciones - " + df_melt["INDICADOR"]

    # Convertir las columnas al tipo de datos esperado
    df_melt["ANIO"] = df_melt["ANIO"].astype(int)
    df_melt["MES"] = df_melt["MES"].astype(int)
    df_melt["VALOR"] = df_melt["VALOR"].astype(float)

    # Convertir la columna 'VALOR' a millones de dolares
    df_melt["VALOR"] = df_melt["VALOR"] * 1_000_000

    # Eliminar filas donde la columna 'MES' sea NaN
    df_melt = df_melt.dropna(subset=["MES"])

    # Ordenar las columnas a devolver
    df_melt = df_melt[["ORIGEN", "INSTITUCION", "INDICADOR", "ANIO", "MES", "VALOR"]]

    return df_melt
