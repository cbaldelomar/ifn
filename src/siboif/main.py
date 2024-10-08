"""
Modulo para obtener datos de la **SIBOIF**.
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import requests
import pandas as pd
import utils

# Añó mínimo con información disponible en el servicio web de la SIBOIF
_INITIAL_YEAR = 2017


def _fetch_data(year: int, month: int):
    """
    Devuelve un JSON con la información del servicio web de la SIBOIF.

    :param year: Año del periodo.
    :param month: Mes del periodo.

    :return: Arreglo JSON con los datos o `None` si no hay datos.
    :rtype: JSON | None
    """

    fecha_ini = fecha_fin = utils.get_date_str(year, month)

    base_url = "https://www.siboif.gob.ni/rest/estadisticas"
    headers = {"User-Agent": "Python bot 1.0"}

    current_dir = os.path.dirname(__file__)
    cert_path = os.path.join(current_dir, "cert/siboif_chain.crt")

    intendencia = "Bancos"
    tipo_reporte = "Estado de Situación Financiera (ESF)"

    url = rf"{base_url}?intendencia={intendencia}&fecha[min]={fecha_ini}&fecha[max]={fecha_fin}&tipo_reporte={tipo_reporte}"

    # Deshabilitar warnings de SSL
    # urllib3.disable_warnings()

    response = requests.get(url, headers=headers, timeout=60, verify=cert_path)
    # response = requests.get(url, headers=headers, verify="siboif.crt")

    # Restaurar warnings
    # warnings.resetwarnings()

    # Si la respuesta no es satisfactoria devolver vacío
    if response.status_code != 200:
        print("Error al consultar servicio web SIBOIF:", response.status_code)
        return None

    # Devolver datos
    return response.json()


def _process_data(data, institucion: Optional[str] = None):
    """
    Procesa los datos y devuelve el DataFrame filtrado opcionalmente por institución.

    :param data: Arreglo JSON.
    :param institucion: Institución a filtrar (opcional).

    :return: pandas DataFrame.
    """

    class Columna(Enum):
        """
        Enum para los nombres de columnas del DataFrame.
        """

        # Nombre de columnas para trabajar con el df original
        FECHA = "fecha"
        VARIABLE = "variable_1"
        VALOR = "valor_1"
        # Nombre de columnas para el df resultado
        ORIGEN = "ORIGEN"
        INSTITUCION = "INSTITUCION"
        ANIO = "ANIO"
        MES = "MES"

    instituciones_a_omitir = ["SFB", "SF", "SFN"]
    variables_a_devolver = ["ACTIVO", "PASIVO", "PATRIMONIO"]

    # Se define un DataFrame vacío para devolverlo en caso de que el servicio no devuelva datos
    # y también para usar sus columnas de plantilla para el DataFrame final.
    df_empty = pd.DataFrame(
        columns=[
            Columna.ORIGEN.value,
            Columna.INSTITUCION.value,
            "INDICADOR",
            Columna.ANIO.value,
            Columna.MES.value,
            "VALOR",
        ]
    )

    if not data:
        return df_empty

    df_data = pd.DataFrame(data)

    # Renombrar columna 'institucion'
    df_data.rename(columns={"institucion": Columna.INSTITUCION.value}, inplace=True)

    # Filtro por defecto para quitar las instituciones para valores totalizados
    filtro_institucion = (
        ~df_data[Columna.INSTITUCION.value]
        .str.strip()
        .str.upper()
        .isin(instituciones_a_omitir)
    )

    # Filtro de variables a obtener
    filtro_variables = (
        df_data[Columna.VARIABLE.value]
        .str.strip()
        .str.upper()
        .isin(variables_a_devolver)
    )

    # Filtrar la institución si se especifica
    if institucion:
        filtro_institucion = filtro_institucion & (
            df_data[Columna.INSTITUCION.value].str.strip().str.upper()
            == institucion.strip().upper()
        )

    # Aplicar filtros
    df_data = df_data[filtro_institucion & filtro_variables]

    # Convertir institución y variable a mayúsculas
    # Esto para generar consistencia en los datos
    df_data[Columna.INSTITUCION.value] = df_data[Columna.INSTITUCION.value].str.upper()
    df_data[Columna.VARIABLE.value] = df_data[Columna.VARIABLE.value].str.upper()

    # Convertir columna 'fecha' en datetime
    df_data[Columna.FECHA.value] = pd.to_datetime(df_data[Columna.FECHA.value])

    # Convertir la columna valor a float
    df_data[Columna.VALOR.value] = (
        df_data[Columna.VALOR.value].str.replace(",", "").astype(float)
    )

    # Agregar columnas requeridas
    df_data[Columna.ORIGEN.value] = "SIBOIF"
    df_data[Columna.ANIO.value] = df_data[Columna.FECHA.value].dt.year
    df_data[Columna.MES.value] = df_data[Columna.FECHA.value].dt.month

    # Seleccionar columnas a devolver
    df_data = df_data[
        [
            Columna.ORIGEN.value,
            Columna.INSTITUCION.value,
            Columna.VARIABLE.value,
            Columna.ANIO.value,
            Columna.MES.value,
            Columna.VALOR.value,
        ]
    ]

    # Resetear indices
    df_data = df_data.reset_index(drop=True)

    # Renombrar columnas de acuerdo a plantilla
    df_data.columns = df_empty.columns

    return df_data


def get_periodo(year: int, month: int, institucion: Optional[str] = None):
    """
    Devuelve un DataFrame con los datos de la SIBOIF para el periodo especificado,
    filtrado opcionalmente por institución.

    :param year: Año del periodo.
    :param month: Mes del periodo (1-12).
    :param institucion: Nombre de la institución (opcional).

    :return: pandas DataFrame.
    """

    # Obtener los datos
    data = _fetch_data(year, month)

    # Procesar los datos
    df = _process_data(data, institucion)

    return df


def get_all_periodos():
    """
    Devuelve un DataFrame con los datos de la SIBOIF de todos los periodos disponibles.

    :return: pandas DataFrame
    """

    current_year = datetime.now().year

    df = pd.DataFrame()

    # Ciclo para recorrer todos los años y sus meses hasta el año actual
    for year in range(_INITIAL_YEAR, current_year + 1):
        for month in range(1, 13):
            print("Procesando periodo:", year, month)
            df_data = get_periodo(year, month)

            # Si el DataFrame está vacío quiere decir que ya llegó al último periodo disponible
            if df_data.empty:
                print("No existe información de:", year, month)
                break

            # Concatenar los DataFrames
            df = pd.concat([df, df_data], ignore_index=True)

    return df


def get_last_periodo():
    """
    Devuelve un DataFrame con los datos de la SIBOIF del último periodo disponible.

    :return: pandas DataFrame
    """

    df = pd.DataFrame()

    date = datetime.now().date()

    # Procesar desde la fecha actual hacía atrás hasta encontrar datos del último periodo disponible
    # teniendo como limite el año mínimo de información disponible
    while date.year >= _INITIAL_YEAR:
        # Restar días de la fecha para obtener el mes anterior
        date = date - timedelta(days=date.day)

        df = get_periodo(date.year, date.month)

        # Si se encontró datos, salir del ciclo
        if not df.empty:
            print("Último periodo:", date.year, date.month)
            break

    return df
