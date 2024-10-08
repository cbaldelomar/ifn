"""
Modulo para el procesamiento del archivo **Balanza de pagos**.
"""

import calendar
import pandas as pd
from utils import trimestres_dict


def procesar_datos(file_path):
    """
    Función para limpiar los datos de **Balanza de Pagos - Cuenta corriente** y
    transformarlos en un DataFrame adecuado.

    :param file_path: Ruta del archivo excel descargado.
    :return: DataFrame procesado.
    """

    # Leer el archivo de Excel
    df_data = pd.read_excel(file_path, skiprows=5)

    # Asegurarse de que todos los nombres de las columnas sean cadenas
    df_data.columns = df_data.columns.astype(str)

    # Expresiones regulares para identificar columnas
    expresion_regular_años = r"^(?:20\d{2}|21\d{2}|22\d{2}|23\d{2}|24\d{2}|25\d{2}|26\d{2}|27\d{2}|28\d{2}|29\d{2})$"
    expresion_regular_concep = r"^Concep(?!to)"

    # Filtrar las columnas que contienen años o comienzan con 'Concep'
    mask_años = df_data.columns.str.contains(expresion_regular_años, regex=True)
    mask_concep = df_data.columns.str.contains(expresion_regular_concep, regex=True)
    mask = mask_años | mask_concep

    # Filtrar el DataFrame
    df_data = df_data.loc[:, ~mask]

    # Filtrar el DataFrame para mostrar el concepto especificado
    df_data = df_data[df_data["Conceptos"] == "Cuenta corriente"]

    # Función para obtener el último día del trimestre
    def obtener_ultimo_dia_trimestre(trimestre, sufijo_año):
        if len(sufijo_año) > 2:
            año = int(sufijo_año)
        else:
            año = 2000 + int(sufijo_año)

        mes = trimestres_dict.get(trimestre)
        if mes is None:
            raise ValueError(f"Trimestre {trimestre} no válido")

        ultimo_dia = calendar.monthrange(año, mes)[1]
        return f"{año}-{mes:02d}-{ultimo_dia}"

    # Función para renombrar columnas con fechas
    def renombrar_columnas_con_fechas(df_data):
        nuevas_columnas = {}
        for col in df_data.columns:
            partes = col.split()
            if len(partes) == 3 and partes[1] == "Trim":
                trimestre = partes[0]
                sufijo_año = partes[2]
                ultimo_dia = obtener_ultimo_dia_trimestre(trimestre, sufijo_año)
                nuevas_columnas[col] = ultimo_dia
            else:
                nuevas_columnas[col] = col

        return df_data.rename(columns=nuevas_columnas)

    # Renombrar las columnas
    df_data = renombrar_columnas_con_fechas(df_data)

    # Obtener una lista con todos los valores de la columna del DataFrame
    valores = [col for col in df_data.columns if col != "Conceptos"]

    # Aplicar melt al DataFrame
    df_data = pd.melt(
        df_data,
        id_vars="Conceptos",
        value_vars=valores,
        value_name="Millones de dólares",
    )

    # Cambiar el nombre de la columna 'variable' a 'Fecha'
    df_data = df_data.rename(columns={"variable": "Fecha"})

    # Convertir 'Millones de dólares' a dólares
    df_data["Valor"] = df_data["Millones de dólares"] * 1_000_000

    # Extraer año y mes de la columna 'Fecha'
    df_data["Año"] = pd.to_datetime(df_data["Fecha"]).dt.year
    df_data["Mes"] = pd.to_datetime(df_data["Fecha"]).dt.month

    # Crear el nuevo DataFrame con las columnas deseadas
    df_data = pd.DataFrame(
        {
            "ORIGEN": ["BCN"] * len(df_data),  # Constante
            "INSTITUCION": ["NICARAGUA"] * len(df_data),  # Constante
            "INDICADOR": ["Balanza de pagos - "] * len(df_data) + df_data["Conceptos"],
            "ANIO": df_data["Año"],
            "MES": df_data["Mes"],
            # Asegurarse de que el tipo sea float
            "VALOR": df_data["Valor"].astype(float),
        }
    )

    df_data = df_data[df_data["VALOR"] != 0]

    return df_data
