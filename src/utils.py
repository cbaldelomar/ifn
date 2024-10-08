"""
Modulo de funciones utilitarias.
"""

import calendar

# from datetime import datetime

meses_dict = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}

trimestres_dict = {"I": 3, "II": 6, "III": 9, "IV": 12}


def last_day_of_month(year: int, month: int):
    """
    Función de utilidad que devuelve el último día de un mes del año especificado.
    """
    # Get the number of days in the month
    _, last_day = calendar.monthrange(year, month)
    return last_day


def get_date_str(year: int, month: int):
    """
    Función de utilidad que devuelve la fecha en formato yyyy-mm-dd
    del último día del mes y año especificado.
    """
    day = last_day_of_month(year, month)

    day = "0" + str(day)
    month = "0" + str(month)

    return f"{year}-{month[-2:]}-{day[-2:]}"


# def get_date_range_up_today(start_year: int) -> list[str]:
#     """
#     Función de utilidad que devuelve un rango de fechas en formato yyyy-mm-dd del último día de cada mes,
#     comenzando en el año especificado hasta llegar a la fecha actual.
#     """
#     current_year = datetime.now().year

#     dates = []

#     for year in range(start_year, current_year + 1):
#         for month in range(1,13):
#             dates.append(get_date_str(year, month))

#     return dates


# def get_dict_key_by_value(d: dict, value):
#     """
#     Devuelve el key de un diccionario dado su valor.
#     """

#     reverse_dict = {v: k for k, v in d.items()}

#     # Return None if value not found
#     return reverse_dict.get(value, None)
