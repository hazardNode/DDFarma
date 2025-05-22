# yourapp/templatetags/date_filters.py

from django import template
from datetime import datetime

register = template.Library()

@register.filter
def spanish_date(value):
    if not value:
        return ''

    months = {
        1: 'Enero',
        2: 'Febrero',
        3: 'Marzo',
        4: 'Abril',
        5: 'Mayo',
        6: 'Junio',
        7: 'Julio',
        8: 'Agosto',
        9: 'Septiembre',
        10: 'Octubre',
        11: 'Noviembre',
        12: 'Diciembre'
    }

    try:
        day = value.day
        month = months[value.month]
        year = value.year
        return f'{day} de {month}, {year}'
    except AttributeError:
        return value  # In case value isn't a date/datetime object