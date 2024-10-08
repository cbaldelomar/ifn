"""
Modulo para el procesamiento del archivo **Remesas Mensuales**.
"""

import pandas as pd


def procesar_datos(file_path: str):
    """
    Función para limpiar los datos de remesas del archivo Excel de **Remesas Mensuales**
    del Banco Central de Nicaragua (BCN) y transformarlos en un DataFrame adecuado para análisis.

    El proceso incluye la limpieza de datos, la conversión de columnas de meses en filas, el mapeo de meses
    a valores numéricos y la adición de columnas adicionales para enriquecer el DataFrame final.

    :param file_path: Ruta del archivo Excel descargado.
    :return: DataFrame procesado con las columnas ORIGEN, INSTITUCION, INDICADOR, ANIO, MES y VALOR.
    :rtype: pd.DataFrame
    """

    # 1. Leer el archivo de Excel, omitiendo las primeras cuatro filas que contienen metadatos
    df_data = pd.read_excel(file_path, skiprows=4)

    # 2. Limpiar los nombres de las columnas, eliminando espacios en blanco adicionales
    df_data.columns = df_data.columns.str.strip()

    # 3. Eliminar columnas que no contienen ningún valor (completamente vacías)
    df_data.dropna(axis=1, how="all", inplace=True)

    # 4. Eliminar filas que no contienen ningún valor (completamente vacías)
    df_data = df_data.dropna(how="all")

    # 5. Eliminar columna Total
    df_data = df_data.drop("Total", axis=1)

    # 6. Renombrar la columna 'Año' a 'ANIO' para mantener consistencia en los nombres
    df_data.rename(columns={"Año": "ANIO"}, inplace=True)

    # 7. Usar pd.melt para convertir las columnas de meses en filas:
    # - 'ANIO' se mantiene como columna fija (id_vars)
    # - Los nombres de los meses se transforman en la columna 'MES' (var_name)
    # - Los valores de cada mes se transforman en la columna 'VALOR' (value_name)
    df_melted = pd.melt(df_data, id_vars=["ANIO"], var_name="MES", value_name="VALOR")

    # 8. Eliminar filas donde 'ANIO' o 'MES' sean NaN (valores nulos)
    df_melted = df_melted.dropna(subset=["ANIO", "MES"])

    # 9. Eliminar filas donde 'VALOR' sea NaN
    df_melted = df_melted.dropna(subset=["VALOR"])

    # 10. Multiplicar los valores de la columna 'VALOR' por 1,000,000 para convertirlos a millones
    df_melted["VALOR"] = df_melted["VALOR"] * 1_000_000

    # 11. Definir el diccionario para mapear los nombres de los meses a sus valores numéricos
    meses_dict = {
        "Ene": 1,
        "Feb": 2,
        "Mar": 3,
        "Abr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Ago": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dic": 12,
    }

    # 12. Convertir la columna 'MES' (meses en texto) a números usando el diccionario 'meses_dict'
    df_melted["MES"] = df_melted["MES"].map(meses_dict)

    # # Verificar si después del mapeo existen valores NaN en la columna 'MES'
    # # Esto ocurre si algunos nombres de meses no se mapean correctamente
    # if df_melted["MES"].isnull().any():
    #     print(
    #         "Advertencia: Hay meses que no se pudieron mapear. Revise los nombres de los meses."
    #     )

    # 13. Ordenar el DataFrame resultante por 'ANIO' (Año) y 'MES' (Mes)
    df_final = df_melted.sort_values(by=["ANIO", "MES"]).reset_index(drop=True)

    # 14. Crear las columnas adicionales que son constantes en todo el DataFrame
    df_final["ORIGEN"] = "BCN"  # Origen: Banco Central de Nicaragua
    df_final["INSTITUCION"] = "NICARAGUA"  # Institución: Nicaragua
    df_final["INDICADOR"] = "Remesas mensuales"  # Indicador: Remesas mensuales

    # 15. Filtrar solo las filas que no contengan valores vacíos
    df_final = df_final[~df_final["VALOR"].isna()]

    # 16. Asegurar el tipo de datos para la columna 'ANIO'
    df_final["ANIO"] = df_final["ANIO"].astype(int)

    # 17. Reordenar las columnas del DataFrame en el siguiente orden:
    # ORIGEN, INSTITUCION, INDICADOR, ANIO, MES, VALOR
    df_final = df_final[["ORIGEN", "INSTITUCION", "INDICADOR", "ANIO", "MES", "VALOR"]]

    return df_final
