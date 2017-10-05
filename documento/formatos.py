from datetime import date
from decimal import Decimal

_data_dma = '%d/%m/%Y'


def f_dma(data: date) -> str:
    return data.strftime(_data_dma)


def f_moeda(valor: Decimal) -> str:
    return f'R$ {valor:,.2f}'.replace('.', '*').replace(',', '.').replace('*', ',')


def f_int_milhar(valor: int) -> str:
    return f'{valor:,}'.replace(',', '.')


def f_fone(texto: str) -> str:
    if len(texto) == 8:
        return f'{texto[0:4]}-{texto[4:]}'
    elif len(texto) == 9:
        return f'{texto[0:5]}-{texto[5:]}'
    elif len(texto) == 10:
        return f'({texto[0:2]}) {texto[2:6]}-{texto[6:]}'
    elif len(texto) == 11:
        return f'({texto[0:2]}) {texto[2:7]}-{texto[7:]}'
    return ''
