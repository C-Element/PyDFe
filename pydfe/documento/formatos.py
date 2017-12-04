from datetime import date, datetime
from decimal import Decimal

from pydfe.documento.dfe import Endereco


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


def f_ma(data: date) -> str:
    if not isinstance(data, date):
        return ''
    return data.strftime('%m/%Y')


def f_dmah(data: datetime) -> str:
    if not isinstance(data, datetime):
        return ''
    return data.strftime('%d/%m/%Y %H:%M:%S')


def f_moeda(valor: Decimal) -> str:
    return f'R$ {f_dec_milhar(valor,2)}'


def f_int_milhar(valor: int) -> str:
    return f'{valor:,}'.replace(',', '.')


def f_dec_milhar(valor: Decimal, casas: int = 3) -> str:
    return f'{valor:,.{casas}f}'.replace('.', '*').replace(',', '.').replace('*', ',')


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


def f_cst(cst: int) -> str:
    return f'{cst:03}'


def f_relevante(valor: Decimal) -> str:
    if valor == Decimal():
        return '0'
    return str(Decimal(str(round(valor, 5)).strip('0'))).replace('.', ',')


def construir_endereco(obj_end: Endereco, com_endereco: bool = True, com_cep: bool = False, com_cidade: bool = True, com_fone: bool = False,
                       com_bairro: bool = True) -> str:
    retorno = ''

    def se_tem(texto: str = ' - '):
        if len(retorno) > 0:
            return texto
        return ''

    if com_endereco:
        retorno += f'{obj_end.logradouro}, {obj_end.numero}{" - " if obj_end.complemento else ""}{obj_end.complemento}'
    if com_bairro:
        retorno += se_tem(', ') + f'{obj_end.bairro}'
    if com_cep:
        retorno += se_tem() + f'{f_cep(obj_end.cep)}'
    if com_cidade:
        retorno += se_tem() + f'{obj_end.municipio}/{obj_end.uf}'
    if com_fone:
        retorno += se_tem() + f'FONE: {f_fone(obj_end.telefone)}'
    return retorno
