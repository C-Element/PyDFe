from collections import OrderedDict

from xmltodict import parse as x2d_parse

from documento.DFePDF import FontePDF
from .DFePDF import DFePDF
from .dfe import InfNFe
from .formatos import f_dma, f_moeda, f_int_milhar


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

    def gerar_pdf(self, caminho: str):
        danfe = DANFe(self)
        danfe.output(caminho, 'F')


class DANFe(DFePDF):
    def __init__(self, nfe: NFe):
        super().__init__()
        self.nfe = nfe.infNFe

    def canhoto(self) -> int:
        destinatario = f'{self.nfe.destinatario.razao_social} - {self.nfe.destinatario.endereco.logradouro}, {self.nfe.destinatario.endereco.numero} - ' \
                       f'{self.nfe.destinatario.endereco.complemento},  {self.nfe.destinatario.endereco.bairro} - {self.nfe.destinatario.endereco.municipio}/' \
                       f' {self.nfe.destinatario.endereco.uf}'
        conteudo = f'RECEBEMOS DE {self.nfe.emitente.razao_social} OS PRODUTOS E/OU SERVIÇOS CONSTANTES DA NOTA FISCAL ELETRÔNICA INDICADA AO LADO. ' \
                   f'EMISSÃO: {f_dma(self.nfe.ide.data_emissao)} VALOR TOTAL: {f_moeda(self.nfe.total.icms.valor_nf)} DESTINATÁRIO: {destinatario}'
        fonte = FontePDF(tamanho=7)
        largura = round(self.max_largura * 0.81)
        x = self.x + largura
        y = self.y + 10
        self.caixa_de_texto(self.x, self.y, largura, 10, conteudo, fonte, forcar=False)
        div_e = self.max_largura - x
        fonte.tamanho = 13
        fonte.estilo = 'B'
        self.caixa_de_texto(x, self.y, self.max_largura - x, 20, f'NF-e\nNº {f_int_milhar(self.nfe.ide.nf)}\n Série  {self.nfe.ide.serie}', fonte, forcar=False,
                            alinhamento_v='C', alinhamento_h='C')
        fonte.tamanho = 7
        fonte.estilo = ''
        self.caixa_de_texto(self.x, y, largura * 0.2, 10, 'DATA DE RECEBIMENTO', fonte, forcar=False)
        x = self.x + (largura * 0.2)
        self.caixa_de_texto(x, y, self.max_largura - x - div_e, 10, 'IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR', fonte, forcar=False)
        y = self.y + 22
        self.dashed_line(self.x, y, self.max_largura, y)
        return y + 2

    def header(self):
        self.canhoto()
