"""
Modulo para el procesamiento del archivo **Índices de precios de exportación tipo Fisher**.
"""

import pandas as pd
from utils import meses_dict


def procesar_excel(file_path):
    """
    Procesa el archivo Excel buscando el concepto especificado y devolviendo
    los valores correspondientes a los meses y el concepto.

    Args:
    file_path (str): Ruta al archivo de Excel.
    concepto (str): Concepto a buscar en las hojas (por ejemplo, 'Producción Agropecuaria').

    Returns:
    pd.DataFrame: DataFrame con los datos procesados.
    """
    # Cargar el archivo de Excel
    xls = pd.ExcelFile(file_path)

    # Inicializar una lista para almacenar los datos de cada hoja
    all_data = []
    concepto = "Producción Agropecuaria"

    # Procesar cada hoja
    for sheet_name in xls.sheet_names:
        # Obtener el año desde el nombre de la hoja
        year = int(
            sheet_name
        )  # Asumimos que el nombre de la hoja es el año en formato numérico

        # Leer cada hoja
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        # Buscar la fila que contiene el concepto especificado
        for idx, row in df.iterrows():
            if row.astype(str).str.contains(concepto, case=False, na=False).any():
                # Encontrado el concepto especificado

                # La fila con los nombres de los meses está dos filas arriba
                meses_row = df.iloc[idx - 2]

                # La fila con los valores está justo a la derecha de la fila encontrada
                valores_row = df.iloc[idx]

                # Recorrer las columnas para obtener los meses y valores
                for col in range(
                    1, df.shape[1]
                ):  # Suponiendo que los meses están en las columnas, empezando desde la columna 1
                    # El nombre del mes en la fila dos arriba
                    month_name = meses_row[col]
                    # El valor correspondiente está en la misma fila del concepto encontrado
                    value = valores_row[col]

                    # Convertir el nombre del mes en número si es válido
                    if month_name in meses_dict:
                        month = meses_dict[month_name]

                        # Multiplicar el valor por 1,000,000 para convertirlo a valor real
                        value_in_millions = float(
                            value * 1_000_000
                        )  # Aseguramos que el valor es float

                        # Concatenar el concepto con "Índices de precios de exportación tipo Fisher"
                        concepto_completo = (
                            "Índices de precios de exportación tipo Fisher - "
                            + concepto
                        )

                        # Añadir los datos procesados a la lista
                        all_data.append(
                            {
                                "ORIGEN": "BCN",
                                "INSTITUCION": "NICARAGUA",
                                "INDICADOR": concepto_completo,
                                "ANIO": int(year),  # Aseguramos que Anio sea entero
                                "MES": int(month),  # Aseguramos que Mes sea entero
                                "VALOR": value_in_millions,  # Aseguramos que Valor sea float
                            }
                        )

    # Convertir la lista a un DataFrame
    result_df = pd.DataFrame(all_data)

    # Asegurarse de que los tipos de datos sean correctos
    result_df["ANIO"] = result_df["ANIO"].astype(int)
    result_df["MES"] = result_df["MES"].astype(int)
    result_df["VALOR"] = result_df["VALOR"].astype(float)

    # Devolver el DataFrame
    return result_df
