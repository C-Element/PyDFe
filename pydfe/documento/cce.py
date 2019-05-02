from collections import OrderedDict

from xmltodict import parse as x2d_parse

from pydfe.documento.dfe import InfEvento


class CCe(object):
    def __init__(self, conteudo_xml: str):
        self.infEvento: InfEvento = None
        self.data_recebimento = None
        self.protocolo = None
        self.conteudo_xml: str = conteudo_xml
        self.preencher()

    def preencher(self) -> None:
        dado: OrderedDict = x2d_parse(self.conteudo_xml)
        for chave, valor in dado.items():
            if chave == 'procEventoNFe':
                self.preencher_proc_evento(valor)
            elif chave == 'evento':
                self.preencher_evento(valor)

    def preencher_proc_evento(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'evento':
                self.preencher_evento(valor)

    def preencher_evento(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'infEvento':
                self.infEvento = InfEvento(valor)
