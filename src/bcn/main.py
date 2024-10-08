"""
Módulo para obtener datos del **BCN**.\n
- Depende del paquete `openpyxl` para leer archivos `.xlsx`:\n
    pip install openpyxl
"""

import os
import time
import requests
import pandas as pd
from bcn.reportes import reportes_list


def _download_file(url: str, file_name: str):
    """
    Descarga un archivo del BCN dada la url y el nombre que recibirá el archivo
    y devuelve la ruta del archivo.

    :param url: Url del archivo a descargar.
    :file_name: Nombre que recibirá el archivo al ser descargado.

    :return: Ruta del archivo descargado o `None` si ocurre algún error.
    :rtype: str | None
    """

    current_dir = os.path.dirname(__file__)
    files_dir = os.path.join(current_dir, "files")

    # Encabezados necesarios para evitar que el sitio del BCN te detecte como bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        "Referer": "https://www.bcn.gob.ni/publicaciones/sector-externo",
    }

    # Esperar 3 segundos antes de hacer el request
    # para evitar que el sitio bloquee peticiones sospechosas por ser muy rápidas
    time.sleep(3)

    # Se define un timeout para evitar una request infinita
    response = requests.get(url, headers=headers, timeout=60)

    # Si la respuesta no es satisfactoria imprimir error y devolver valor vacío
    if response.status_code != 200:
        print("Error al descargar archivo del BCN", response.status_code)
        return None

    # Crear el directorio para guardar los archivos descargados
    os.makedirs(files_dir, exist_ok=True)

    # Definir el nombre del archivo
    file_path = os.path.join(files_dir, file_name)

    # print(response.content)

    # Abrir archivo en modo de escritura en binario
    with open(file_path, "wb") as file:
        # Escribir el contenido de la respuesta al archivo
        file.write(response.content)

    return file_path


# def _filtrar_periodo(
#     df: pd.DataFrame, year: int, month: int, indicador: Optional[str] = None
# ):
#     """
#     Devuelve el DataFrame filtrado por año y mes, y opcionalmente por indicador.
#     """

#     # Filtrar los datos del año y mes especificado
#     df = df[(df["ANIO"] == year) & (df["MES"] == month)]

#     # Si se especifica el indicador, filtrarlo
#     if indicador:
#         df = df[(df["INDICADOR"] == indicador)]

#     # Resetear índices
#     df = df.reset_index(drop=True)

#     return df


def get_all_periodos():
    """
    Devuelve un DataFrame con los datos del BCN de todos los periodos disponibles.

    :return: pandas DataFrame
    """

    df = pd.DataFrame()

    # Descargar y procesar los archivos de cada reporte
    for reporte in reportes_list:
        name, url, file_name, function = reporte.values()

        print("Procesando archivo:", name)

        file_path = _download_file(url, file_name)

        if file_path:
            # df = _process_file_ied(file_path)
            df_data = function(file_path)

            # Concatenar los DataFrames
            df = pd.concat([df, df_data], ignore_index=True)

    return df


def get_last_periodo():
    """
    Devuelve un DataFrame con los datos del BCN del último periodo disponible para cada indicador.

    :return: pandas DataFrame
    """

    # Obtener DataFrame con los datos
    df_data = get_all_periodos()

    # Obtener el máximo año para cada indicador
    max_years = df_data.groupby("INDICADOR")["ANIO"].max().reset_index()

    # Hacer merge con el DataFrame original para obtener solo las filas del año máximo
    df_max_year = pd.merge(df_data, max_years, on=["INDICADOR", "ANIO"])

    # Obtener la fila del máximo mes para cada indicador
    df = df_max_year.loc[df_max_year.groupby("INDICADOR")["MES"].idxmax()]

    # Resetear índices
    df = df.reset_index(drop=True)

    # df = pd.DataFrame()

    # for _, row in max_years.iterrows():
    #     indicador = row["INDICADOR"]
    #     anio = row["ANIO"]

    #     # Filtrar por el máximo año de cada indicador
    #     df_filtrado = df_data[
    #         (df_data["INDICADOR"] == indicador) & (df_data["ANIO"] == anio)
    #     ]

    #     # Agrupar por indicador para obtener el máximo mes de cada uno
    #     df_mes = df_filtrado.groupby("INDICADOR").agg({"MES": "max"}).reset_index()

    #     mes = df_mes.loc[0, "MES"]

    #     df_filtrado = df_filtrado[df_filtrado["MES"] == mes]

    #     df = pd.concat([df, df_filtrado], ignore_index=True)

    # # Obtener el máximo año y mes por indicador
    # df_filtros = (
    #     df_data.groupby("INDICADOR").agg({"ANIO": "max", "MES": "max"}).reset_index()
    # )

    # df = pd.DataFrame()

    # # Filtrar por indicador y obtener un solo DataFrame de resultado
    # for _, row in df_filtros.iterrows():
    #     indicador, year, month = row

    #     print("Filtrando indicador:", indicador)

    #     df_filtrado = _filtrar_periodo(df_data, year, month, indicador)

    #     # Concatenar los DataFrames
    #     df = pd.concat([df, df_filtrado], ignore_index=True)

    # # # Obtener los máximos valores de las columnas 'Año' y 'Mes'
    # # year, month = df[["ANIO", "MES"]].max()

    # # # Filtrar los datos del año y mes del último periodo
    # # df = _filtrar_periodo(df, year, month)

    return df


def get_periodo(year: int, month: int):
    """
    Devuelve un DataFrame con los datos del BCN para el periodo especificado.

    :param year: Año del periodo.
    :param month: Mes del periodo (1-12).

    :return: pandas DataFrame
    """

    # Obtener DataFrame con los datos
    df = get_all_periodos()

    # Filtrar los datos del año y mes especificado
    df = df[(df["ANIO"] == year) & (df["MES"] == month)]

    # Resetear índices
    df = df.reset_index(drop=True)

    return df
