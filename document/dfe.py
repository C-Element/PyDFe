from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

from xmltodict import parse as x2d_parse

from enum import IntEnum


# Exceções
class ErroDeInicializacao(Exception):
    pass


class DocumentoInvalido(Exception):
    pass


# classes DFe
class IDe(object):
    cnf: int = int()  # Código numérico que compõe a Chave de Acesso. Número aleatório gerado pelo emitente :: <cNF>
    data_emissao: datetime = None  # Data/Hora da emissão <dhEmi>
    data_saida_entrada: datetime = None  # Data/Hora da saída/entrada <dhSaiEnt >
    dv: int = int()  # DV da chave de acesso :: <cDV>
    id_dest: int = int()  # Identificador de local de destino. 1=Op. interna; 2=Op. interestadual; 3=Op. com exterior :: <idDest>
    ind_pag: int = int()  # Indicador da forma de pagamento. 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros. :: <indPag>
    modelo: int = 55  # Código do Modelo do DFe. 55=NFe; 65=NFCe <mod>
    municipio: int = int()  # Código do Município de Ocorrência <cMunFG>
    nat_operacao: str = str()  # Descrição da Natureza da Operação :: <natOp>
    nf: int = int()  # Número do DFe <nNF>
    serie: int = int()  # Série do DFe <serie>
    tipo_nf: int = int()  # Tipo de operação. 0=Entrada; 1=Saída :: <tpNF>
    tipo_emissao: int = 1  # Tipo de Emissão do DFe  <tpEmis>
    tipo_impressao: int = 1  # Formato de Impressão do DANFE  <tpImp>
    uf: str = str()  # Código da UF do emitente do DFe :: <cUF>


class InfNFe(object):
    cobr
    dest
    det
    emit
    entrega
    ide: IDe = IDe()  # Identificação da NFe :: <ide>
    id: str = str()  # Cheve NFe precedida da literal 'NFe' :: @Id
    infAdic
    total
    transp
    versao: str = str()  # Versão do layout NFe :: @versao


class Signature(object):
    pass


class DestinatarioEmitente(object):
    cnpj: str = ''
    nome: str = ''
    uf: str = ''

    def __str__(self):
        return f'Nome: "{self.nome}" CNPJ: "{self.cnpj}" UF: "{self.uf}"'

    def __repr__(self):
        return f'DestinatarioEmitente: <{self.__str__()}>'
