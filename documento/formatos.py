from datetime import date, datetime
from decimal import Decimal


def encher(texto: str, caractere: str, tamanho: int, na_frente: bool = True) -> str:
    if not isinstance(texto, str):
        texto = str(texto)
    while len(texto) < tamanho:
        if na_frente:
            texto = caractere + texto
        else:
            texto += caractere
    return texto


def f_dma(data: date) -> str:
    if not isinstance(data, date):
        return ''
    return data.strftime('%d/%m/%Y')


def f_dmah(data: datetime) -> str:
    if not isinstance(data, datetime):
        return ''
    return data.strftime('%d/%m/%Y %H:%M:%S')


def f_moeda(valor: Decimal) -> str:
    return f'R$ {valor:,.2f}'.replace('.', '*').replace(',', '.').replace('*', ',')


def f_int_milhar(valor: int) -> str:
    return f'{valor:,}'.replace(',', '.')


def f_fone(texto: str) -> str:
    if not isinstance(texto, str):
        texto = str(texto)
    if len(texto) == 8:
        return f'{texto[0:4]}-{texto[4:]}'
    elif len(texto) == 9:
        return f'{texto[0:5]}-{texto[5:]}'
    elif len(texto) == 10:
        return f'({texto[0:2]}) {texto[2:6]}-{texto[6:]}'
    elif len(texto) == 11:
        return f'({texto[0:2]}) {texto[2:7]}-{texto[7:]}'
    return ''


def f_cep(texto: str) -> str:
    if not isinstance(texto, str):
        texto = str(texto)
    if len(texto) == 8:
        return f'{texto[0:2]}.{texto[2:5]}-{texto[5:]}'
    return ''


def f_espaco_a_cada(texto: str, parada: int) -> str:
    retorno = ''
    contador = 0
    for x in texto:
        retorno += x
        contador += 1
        if contador == parada:
            retorno += ' '
            contador = 0
    return retorno


def f_cnpj(texto: str) -> str:
    texto = encher(texto, '0', 14)
    return f'{texto[0:2]}.{texto[2:5]}.{texto[5:8]}/{texto[8:12]}-{texto[12:14]}'


def f_cpf(texto: str) -> str:
    texto = encher(texto, '0', 11)
    return f'{texto[0:3]}.{texto[3:6]}.{texto[6:9]}-{texto[9:11]}'


def f_hora(data: datetime) -> str:
    if not isinstance(data, datetime):
        return ''
    return data.strftime('%H:%M:%S')
