from collections import OrderedDict

from xmltodict import parse as x2d_parse

from .dfe import InfNFe


class NFe(object):
    def __init__(self, conteudo_xml: str):
        self.infNFe: InfNFe = None
        self.conteudo_xml: str = conteudo_xml
        self.preencher()

    def preencher(self) -> None:
        dado: OrderedDict = x2d_parse(self.conteudo_xml)
        for chave, valor in dado.items():
            if chave == 'nfeProc':
                self.preencher_nfe_proc(valor)
            elif chave == 'NFe':
                self.preencher_nfe(valor)

    def preencher_nfe_proc(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'NFe':
                self.preencher_nfe(valor)

    def preencher_nfe(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'infNFe':
                self.infNFe = InfNFe(valor)
