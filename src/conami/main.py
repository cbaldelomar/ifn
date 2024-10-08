"""
Módulo para obtener datos de la **CONAMI**.\n
- Depende del paquete `xlrd` para leer archivos `.xls`:\n
    pip install xlrd
"""

import os
from typing import Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlrd
import utils

_CONAMI_URL = "http://www.conami.gob.ni/index.php/est-reportes?reportName=/RptEstadisticas/RptEstadoSituacion&tituloreport=Estado de Situación Financiera&cat=Reportes Contables"

_PERIODO_ID_KEY = "periodo_id"
_PERIODO_MONTH_KEY = "month"
_PERIODO_YEAR_KEY = "year"


def _get_periodos() -> list[dict]:
    """
    Devuelve una lista de los periodos disponibles.\n
    Ejemplo:\n
        [
            { "periodo_id": 1, "year": 2018, "month": 1 }
            { "periodo_id": 2, "year": 2018, "month": 2 }
        ]
    """
    periodos = []

    response = requests.get(_CONAMI_URL, timeout=60)

    # Si la respuesta no es satisfactoria devolver el diccionario vacío
    if response.status_code != 200:
        print(
            "Error al consultar periodos en la página de la CONAMI:",
            response.status_code,
        )
        return periodos

    soup = BeautifulSoup(response.content, "html.parser")

    # Obtener los options del select de periodos
    periodo_options = soup.select('form#reportForm select[name="Periodo"] option')

    for option in periodo_options:
        # Obtener el texto de cada opción, remplazando cualquier espacio en el texto
        text = option.text.replace(" ", "")

        # Obtener el mes y año haciendo un split del texto
        month_name, year = text.split("-")

        # Obtener el numero del mes
        month = utils.meses_dict[month_name]

        # Llenar el diccionario, donde la key será el periodo_id y el value será la tuple (año, mes)
        periodos.append(
            {
                _PERIODO_ID_KEY: int(option["value"]),
                _PERIODO_YEAR_KEY: int(year),
                _PERIODO_MONTH_KEY: month,
            }
        )

    return periodos


def _get_ultimo_periodo():
    """
    Devuelve el último periodo disponible.
    """

    periodos = _get_periodos()

    ultimo_periodo = max(periodos, key=lambda x: x[_PERIODO_ID_KEY])

    if not ultimo_periodo:
        return None

    return ultimo_periodo


def _get_periodo_id(year: int, month: int) -> int | None:
    """
    Devuelve el identificador del periodo según el año y mes especificado.
    """

    periodos = _get_periodos()

    for periodo in periodos:
        if periodo[_PERIODO_YEAR_KEY] == year and periodo[_PERIODO_MONTH_KEY] == month:
            return periodo[_PERIODO_ID_KEY]

    return None


def _download_file_by_periodo_id(periodo_id: int):
    """
    Descarga un archivo Excel con los datos de la CONAMI para el periodo especificado
    y devuelve la ruta del archivo.
    """

    current_dir = os.path.dirname(__file__)
    files_dir = os.path.join(current_dir, "files")

    payload = {
        "Periodo": periodo_id,
        "exportSelect": "EXCEL",
        "parameters": "false",
        "exportName": "Reporte",
        "reportName": "/RptEstadisticas/RptEstadoSituacion",
    }

    response = requests.post(_CONAMI_URL, data=payload, timeout=60)

    # Si la respuesta no es satisfactoria devolver un valor vacío
    if response.status_code != 200:
        print("Error al descargar reporte de la CONAMI:", response.status_code)
        return None

    # Crear el directorio para guardar los archivos descargados
    os.makedirs(files_dir, exist_ok=True)

    # Definir el nombre del archivo
    file_path = os.path.join(files_dir, f"EstadoSituacionFinanciera_{periodo_id}.xls")

    # Abrir archivo en modo de escritura binaria
    with open(file_path, "wb") as file:
        # Escribir el contenido de la respuesta al archivo
        file.write(response.content)

    return file_path


def _download_file(year: int, month: int):
    """
    Descarga un archivo Excel con los datos de la CONAMI para el periodo especificado
    y devuelve la ruta del archivo.
    """

    periodo_id = _get_periodo_id(year, month)

    if not periodo_id:
        print("Periodo inválido:", year, month)
        return None

    return _download_file_by_periodo_id(periodo_id)


def _process_file(
    file_path: str, year: int, month: int, institucion: Optional[str] = None
):
    """
    Procesa el archivo especificado y devuelve un DataFrame con los datos de la CONAMI
    """

    columna_origen = "ORIGEN"
    columna_institucion = "INSTITUCION"
    columna_indicador = "INDICADOR"
    columna_anio = "ANIO"
    columna_mes = "MES"
    columna_valor = "VALOR"
    variables_a_devolver = ("ACTIVO", "PASIVO", "PATRIMONIO")

    # Se define un DataFrame vacío para devolverlo en caso de algún problema
    df_empty = pd.DataFrame(
        columns=[
            columna_origen,
            columna_institucion,
            columna_indicador,
            columna_anio,
            columna_mes,
            columna_valor,
        ]
    )

    if not file_path:
        return df_empty

    # Leer el archivo de la CONAMI directamente muestra el warning:
    # WARNING *** file size (81856) not 512 + multiple of sector size (512)
    # Para solucionar esto se lee directamente del WorkBook con xlrd
    # https://github.com/pandas-dev/pandas/issues/16620
    # df_data = pd.read_excel(file_path, skiprows=9)

    # Suppressing XLRD warnings redirecting standard error outputs to null device
    with open(os.devnull, "w", encoding="utf-8") as log:
        wb = xlrd.open_workbook(file_path, logfile=log)

    # Cargar los datos del reporte en un DataFrame, omitiendo las primeras nueve filas
    df_data = pd.read_excel(wb, skiprows=9)

    if df_data.empty:
        return df_empty

    # Eliminar columnas que no contengan valores
    df_data.dropna(axis=1, how="all", inplace=True)

    # Eliminar filas que no contengan valores
    df_data.dropna(how="all", inplace=True)

    # Eliminar columna Total
    df_data.drop("Total", axis=1, inplace=True)

    # Renombrar columna de descripción
    df_data.rename(columns={"Descripcion de Cuenta": columna_indicador}, inplace=True)

    # Limpiar valores de la columna indicador
    # y pasarlos a mayúsculas para generar consistencia en los datos a la hora de filtrar
    df_data[columna_indicador] = df_data[columna_indicador].str.strip().str.upper()

    # Filtro de variables a obtener
    filtro_variables = df_data[columna_indicador].isin(variables_a_devolver)

    # Aplicar filtro de variables
    df_data = df_data[filtro_variables]

    # Usar la función melt para hacer unpivot de las instituciones
    df_data = pd.melt(
        df_data,
        id_vars=[columna_indicador],
        var_name=columna_institucion,
        value_name=columna_valor,
    )

    # Limpiar valores de la columna insitución
    # y pasarlos a mayúsculas para generar consistencia en los datos a la hora de filtrar
    df_data[columna_institucion] = df_data[columna_institucion].str.strip().str.upper()

    # Filtrar la institución si se especifica
    if institucion:
        filtro_institucion = df_data[columna_institucion] == institucion.strip().upper()

        # Aplicar filtro de institución
        df_data = df_data[filtro_institucion]

    # Agregar columnas requeridas
    df_data[columna_origen] = "CONAMI"
    df_data[columna_anio] = year
    df_data[columna_mes] = month

    # Seleccionar columnas a devolver
    df_data = df_data[
        [
            columna_origen,
            columna_institucion,
            columna_indicador,
            columna_anio,
            columna_mes,
            columna_valor,
        ]
    ]

    # Resetear indices
    df_data = df_data.reset_index(drop=True)

    return df_data


def get_all_periodos():
    """
    Devuelve un DataFrame con los datos de la CONAMI de todos los periodos disponibles.

    :return: pandas DataFrame
    """

    df = pd.DataFrame()

    periodos = _get_periodos()

    for periodo in periodos:
        periodo_id, year, month = periodo.values()

        print("Procesando periodo:", year, month)

        file_path = _download_file_by_periodo_id(periodo_id)

        df_data = _process_file(file_path, year, month)

        # Concatenar los DataFrames
        df = pd.concat([df, df_data], ignore_index=True)

    return df


def get_last_periodo():
    """
    Devuelve un DataFrame con los datos de la CONAMI del último periodo disponible.

    :return: pandas DataFrame
    """

    df = pd.DataFrame()

    periodo = _get_ultimo_periodo()

    if not periodo:
        return df

    periodo_id, year, month = periodo.values()

    print("Último periodo:", year, month)

    file_path = _download_file_by_periodo_id(periodo_id)

    df_data = _process_file(file_path, year, month)

    return df_data


def get_periodo(year: int, month: int, institucion: Optional[str] = None):
    """
    Devuelve un DataFrame con los datos de la CONAMI para el periodo especificado,
    filtrado opcionalmente por institución.

    :param year: Año del periodo.
    :param month: Mes del periodo (1-12).
    :param institucion: Nombre de la institución (opcional).

    :return: pandas DataFrame
    """

    # Descargar el archivo
    file_path = _download_file(year, month)

    df_data = _process_file(file_path, year, month, institucion)

    return df_data
