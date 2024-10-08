"""
Modulo con la lista de reportes del BCN a procesar.
"""

from bcn import (
    ied,
    balanza_pagos,
    pii,
    remesas,
    deuda_externa,
    indice_precios,
    importaciones,
    exportaciones,
    balanza_comercial,
)


# Lista de reportes a procesar
reportes_list = [
    {
        "name": "Ingresos brutos y flujos netos de IED",
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_real/IED/IBIED.xlsx",
        "file_name": "IED.xlsx",
        "function": ied.procesar_datos,
    },
    {
        # Nombre del reporte
        "name": "Balanza de pagos",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_externo/balanza_pagos/MBP6_(2006).xls",
        "file_name": "BPCC.xls",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": balanza_pagos.procesar_datos,
    },
    {
        # Nombre del reporte
        "name": "Posición de Inversión Internacional",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_externo/posicion_inversion/PII_(referencia_2006).xls",
        "file_name": "PIIN.xls",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": pii.procesar_datos,
    },
    {
        # Nombre del reporte
        "name": "Remesas Mensuales",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/siec/datos/remesas.xls",
        "file_name": "REMESAS.xls",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": remesas.procesar_datos,
    },
    {
        # Nombre del reporte
        "name": "Deuda Externa Total",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_externo/deuda_externa/cuadros_DET.xlsx",
        "file_name": "DET.xlsx",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": deuda_externa.procesar_datos,  # type: ignore
    },
    {
        # Nombre del reporte
        "name": "Índices de precios de exportación tipo Fisher",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_externo/comercio_exterior/indices_comercio/6-25.xls",
        "file_name": "IPE.xls",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": indice_precios.procesar_excel,
    },
    {
        # Nombre del reporte
        "name": "Importaciones CIF: mercancías",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_externo/comercio_exterior/importaciones/6-10.xls",
        "file_name": "Importaciones.xls",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": importaciones.procesar_datos,
    },
    {
        # Nombre del reporte
        "name": "Exportaciones FOB: mercancías por sector económico",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_externo/comercio_exterior/exportaciones/6-3b.xls",
        "file_name": "Exportaciones.xls",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": exportaciones.procesar_datos,
    },
    {
        # Nombre del reporte
        "name": "Balanza comercial: mercancías generales",
        # URL de descarga
        "url": "https://www.bcn.gob.ni/sites/default/files/estadisticas/sector_externo/comercio_exterior/balanza_comercial/6-3a.xls",
        "file_name": "Balanza Comercial.xls",  # Nombre que recibirá el archivo descargado
        # Nombre de la función que procesará el archivo y devuelve el DataFrame
        "function": balanza_comercial.procesar_datos,
    },
]
