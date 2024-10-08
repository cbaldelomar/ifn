"""
Modulo para procesamiento de indicadores nacionales.\n
- Ejecución desde línea de comandos:\n
    - Todos los periodos
        py procesar.py todos
    - Último periodo
        py procesar.py ultimo
    - Periodo especifico (yyyymm)
        py procesar.py 202403
"""

import sys
import pandas as pd
import bcn
import siboif
import conami
import bd


def _get_functions(periodo):
    """
    Devuelve las funciones apropiadas basado en el periodo especificado.
    """

    if periodo == "todos":
        return bcn.get_all_periodos, siboif.get_all_periodos, conami.get_all_periodos

    if periodo == "ultimo":
        return bcn.get_last_periodo, siboif.get_last_periodo, conami.get_last_periodo

    return bcn.get_periodo, siboif.get_periodo, conami.get_periodo


def _process_data(periodo, origen):
    """
    Procesa la información basado en el periodo y origen especificado.
    """
    year, month = None, None
    especifico = False
    df_bcn = df_siboif = df_conami = pd.DataFrame()

    if periodo == "todos":
        print("Procesando todos los periodos")
    elif periodo == "ultimo":
        print("Procesando el último periodo")
    else:
        try:
            year, month = int(periodo[:4]), int(periodo[-2:])
        except ValueError:
            print("Se especificó un periodo inválido.")
            return

        print(f"Procesando periodo: {year} - {month}")
        especifico = True

    if origen not in ("BCN", "SIBOIF", "CONAMI", None):
        print("Se especificó un origen inválido.")
        return

    procesar_bcn, procesar_siboif, procesar_conami = _get_functions(periodo)

    if origen in ("BCN", None):
        print("-" * 50)
        print("Procesando BCN...")
        df_bcn = procesar_bcn(year, month) if especifico else procesar_bcn()

    if origen in ("SIBOF", None):
        print("-" * 50)
        print("Procesando SIBOIF...")
        df_siboif = procesar_siboif(year, month) if especifico else procesar_siboif()

    if origen in ("CONAMI", None):
        print("-" * 50)
        print("Procesando CONAMI...")
        df_conami = procesar_conami(year, month) if especifico else procesar_conami()

    # Combine DataFrames
    df = pd.concat([df_bcn, df_siboif, df_conami], ignore_index=True)

    # Update database
    print("-" * 50)
    print("Procesando base de datos...")
    bd.actualizar(df)

    print("Fin!")


def main():
    """
    Main
    """

    periodo = "ultimo"
    origen = None

    if len(sys.argv) > 1:
        periodo = sys.argv[1]

    if len(sys.argv) > 2:
        origen = sys.argv[2]

    _process_data(periodo, origen)


if __name__ == "__main__":
    main()
