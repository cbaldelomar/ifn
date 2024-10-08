"""
Modulo para el procesamiento del archivo **Deuda Externa Total**.
"""

import pandas as pd
from utils import trimestres_dict


def procesar_datos(file_path: str):
    """
    Procesa el archivo Excel buscando la frase especificada en el parámetro 'concepto'
    en la hoja 'C1' y devolviendo los valores correspondientes a los trimestres y años.
    Además, agrega la frase "deuda externa total" concatenada con el concepto al DataFrame final.

    :file_path: Ruta al archivo de Excel.

    :return: DataFrame con los datos procesados.
    :rtype: pd.DataFrame
    """
    # Cargar el archivo de Excel
    df = pd.read_excel(file_path, sheet_name="C1", header=None)

    # Inicializar una lista para almacenar los datos
    all_data = []
    concepto = "Gobierno General"

    # Buscar la fila que contiene la frase especificada en 'concepto'
    for idx, row in df.iterrows():
        if row.astype(str).str.contains(concepto, case=False, na=False).any():
            # Encontrado el concepto

            # La fila con los trimestres está en la fila 5 (índice 5)
            trimestres_row = df.iloc[5]

            # La fila con los años está tres filas arriba de los trimestres
            anios_row = df.iloc[4]

            # La fila con los valores está justo a la derecha de la fila encontrada
            valores_row = df.iloc[idx]

            # Variable para almacenar el año actual
            anio_actual = None

            # Recorrer las columnas para obtener los trimestres y valores
            for col in range(1, df.shape[1]):  # Empezando desde la columna 1
                trimestre = trimestres_row[col]  # Trimestre (I, II, III, IV)
                anio = anios_row[col]  # Año o NaN

                # Si encontramos un nuevo año, actualizamos el año actual
                if pd.notna(anio):
                    anio_actual = int(anio)  # Convertir el año en entero

                # Si encontramos un trimestre válido, procesamos el valor
                if trimestre in trimestres_dict and anio_actual is not None:
                    mes = int(trimestres_dict[trimestre])  # Convertir el mes en entero
                    value = valores_row[
                        col
                    ]  # Valor correspondiente en la misma fila del concepto encontrado

                    # Multiplicar el valor por 1,000,000 para convertirlo a valor real
                    value_in_millions = float(
                        value * 1_000_000
                    )  # Convertir el valor en float

                    # Crear una variable con la frase "deuda externa total" concatenada con el concepto
                    concepto_concatenado = "Deuda Externa Total - " + concepto

                    # Añadir los datos procesados a la lista
                    all_data.append(
                        {
                            "ORIGEN": "BCN",
                            "INSTITUCION": "NICARAGUA",
                            "INDICADOR": concepto_concatenado,  # Usar la frase concatenada
                            "ANIO": anio_actual,  # Asegurar que el año es entero
                            "MES": mes,  # Asegurar que el mes es entero
                            "VALOR": value_in_millions,  # Asegurar que el valor es float
                        }
                    )

    # Convertir la lista a un DataFrame
    result_df = pd.DataFrame(all_data)

    # Asegurarse de que los tipos de datos son correctos
    result_df["ANIO"] = result_df["ANIO"].astype(int)  # Convertir Anio a entero
    result_df["MES"] = result_df["MES"].astype(int)  # Convertir Mes a entero
    result_df["VALOR"] = result_df["VALOR"].astype(float)  # Convertir Valor a float

    # Devolver el DataFrame
    return result_df
