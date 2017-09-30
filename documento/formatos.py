from datetime import date
from decimal import Decimal

_data_dma = '%d/%m/%Y'


def f_dma(data: date):
    return data.strftime(_data_dma)


def f_moeda(valor: Decimal):
    return f'R$ {valor:,.2f}'.replace('.', '*').replace(',', '.').replace('*', ',')


def f_int_milhar(valor: int):
    return f'{valor:,}'.replace(',', '.')
