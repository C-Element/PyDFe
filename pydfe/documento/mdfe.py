from collections import OrderedDict

from xmltodict import parse as x2d_parse

from pydfe.documento.dfe import InfMDFe
from .dfe import ler_data_hora


class MDFe(object):
    def __init__(self, conteudo_xml: str):
        self.infMDFe: InfMDFe = None
        self.data_recebimento = None
        self.protocolo = None
        self.conteudo_xml: str = conteudo_xml
        self.preencher()

    def preencher(self) -> None:
        dado: OrderedDict = x2d_parse(self.conteudo_xml)
        for chave, valor in dado.items():
            if chave == 'nfeProc':
                self.preencher_nfe_proc(valor)
            elif chave == 'MDFe':
                self.preencher_mdfe(valor)

    def preencher_nfe_proc(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'MDFe':
                self.preencher_mdfe(valor)
            if chave == 'protNFe':
                self.preencher_prot_nfe(valor)

    def preencher_mdfe(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'infMDFe':
                self.infMDFe = InfMDFe(valor)

    def preencher_prot_nfe(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'infProt':
                self.preencher_inf_prot(valor)

    def preencher_inf_prot(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'nProt':
                self.protocolo = valor
            elif chave == 'dhRecbto':
                self.data_recebimento = ler_data_hora(valor)
