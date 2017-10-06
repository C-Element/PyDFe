from collections import OrderedDict

from xmltodict import parse as x2d_parse

from .DFePDF import FontePDF, DFePDF
from .dfe import InfNFe, Endereco
from .formatos import f_dma, f_moeda, f_int_milhar, f_cep, f_fone, f_espaco_a_cada


def construir_endereco(obj_end: Endereco, com_endereco: bool = True, com_cep: bool = False, com_cidade: bool = True, com_fone: bool = False) -> str:
    retorno = ''

    def se_tem():
        if len(retorno) > 0:
            return ' - '
        return ''

    if com_endereco:
        retorno += f'{obj_end.logradouro}, {obj_end.numero} - {obj_end.complemento}, {obj_end.bairro}'
    if com_cep:
        retorno += se_tem() + f'{f_cep(obj_end.cep)}'
    if com_cidade:
        retorno += se_tem() + f'{obj_end.municipio}/{obj_end.uf}'
    if com_fone:
        retorno += se_tem() + f'FONE: {f_fone(obj_end.telefone)}'
    return retorno


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
        destinatario = f'{self.nfe.destinatario.razao_social} - {construir_endereco(self.nfe.destinatario.endereco)}'
        conteudo = f'RECEBEMOS DE {self.nfe.emitente.razao_social} OS PRODUTOS E/OU SERVIÇOS CONSTANTES DA NOTA FISCAL ELETRÔNICA INDICADA AO LADO. ' \
                   f'EMISSÃO: {f_dma(self.nfe.ide.data_emissao)} VALOR TOTAL: {f_moeda(self.nfe.total.icms.valor_nf)} DESTINATÁRIO: {destinatario}'
        fonte = FontePDF(tamanho=7)
        x = largura = round((self.largura_max - self.x) * 0.81)
        y = self.y + 10
        self.caixa_de_texto(self.x, self.y, largura, 10, conteudo, fonte, forcar=False)
        div_d = self.largura_max - (self.x + x)
        fonte.tamanho = 13
        fonte.estilo = 'B'
        self.caixa_de_texto(self.x + x, self.y, div_d, 20, f'NF-e\nNº {f_int_milhar(self.nfe.ide.nf)}\n SÉRIE {self.nfe.ide.serie}', fonte,
                            forcar=False, alinhamento_v='C', alinhamento_h='C')
        fonte.tamanho = 7
        fonte.estilo = ''
        x = round(largura * 0.2)
        self.caixa_de_texto(self.x, y, x, 10, 'DATA DE RECEBIMENTO', fonte, forcar=False)
        self.caixa_de_texto(self.x + x, y, self.largura_max - x - div_d - self.x, 10, 'IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR', fonte, forcar=False)
        y = self.y + 22
        self.dashed_line(self.x, y, self.largura_max, y)
        return y + 2

    def cabecalho(self):
        a_cabecalho = 33
        posicao_y = y = self.canhoto()
        posicao_x = x = round((self.largura_max - self.x) * 0.40)
        x2 = round((self.largura_max - self.x) * 0.20)
        largura_ult_caixa = self.largura_max - x - x2 - self.x
        fonte = FontePDF(tamanho=6)
        self.caixa_de_texto(self.x, y, x, a_cabecalho, fonte=fonte)
        self.caixa_de_texto(self.x + x, y, x2, a_cabecalho)
        self.caixa_de_texto(self.x + x + x2, y, largura_ult_caixa, a_cabecalho)
        tamanho = self.font_size
        posicao_y = posicao_y + self.caixa_de_texto(self.x, y, x, tamanho, "IDENTIFICAÇÃO DO EMITENTE", fonte, 'T', 'C', False) + 2
        fonte.tamanho = 12
        fonte.estilo = 'B'
        posicao_y = posicao_y + self.caixa_de_texto(self.x, posicao_y, x, 12, f'{self.nfe.emitente.razao_social} - {self.nfe.emitente.fantasia}', fonte, 'T',
                                                    'C', False) + 2
        fonte.tamanho = 8
        fonte.estilo = ''
        ender = f'{construir_endereco(self.nfe.emitente.endereco, com_cep=True, com_cidade=False)}\n' \
                f'{construir_endereco(self.nfe.emitente.endereco, False, False, True, True)}'
        self.caixa_de_texto(self.x, posicao_y, x, 12, ender, fonte, 'T', 'C', False)
        fonte.tamanho = 12
        fonte.estilo = 'B'
        posicao_x += self.x
        posicao_y = y + self.caixa_de_texto(posicao_x, y, x2, 12, 'DANFE', fonte, 'T', 'C', False)
        fonte.tamanho = 10
        fonte.estilo = ''
        entrada = '1 - ENTRADA'
        posicao_y = posicao_y + self.caixa_de_texto(posicao_x, posicao_y, x2, 12, 'Documento Auxiliar da Nota Fiscal Eletrônica', fonte, 'T', 'C', False) + 2
        a_quad = self.caixa_de_texto(posicao_x + 2, posicao_y, x2, 12, f'{entrada}\n2 - SAÍDA', fonte, 'T', 'L', False)
        fonte.tamanho = 12
        fonte.estilo = 'B'
        posicao_y = posicao_y + self.caixa_de_texto(posicao_x + self.get_string_width(entrada) + 7, posicao_y , self.get_string_width('0000'), a_quad,
                                                    str(self.nfe.ide.tipo_nf), fonte, 'C', 'C') + 2
        fonte.tamanho = 10
        fonte.estilo = 'B'
        posicao_y = posicao_y + self.caixa_de_texto(posicao_x, posicao_y, x2, 12, f'{f_int_milhar(self.nfe.ide.nf)}', fonte, 'T', 'C', False)
        posicao_y = posicao_y + self.caixa_de_texto(posicao_x, posicao_y, x2, 12, f'SÉRIE {self.nfe.ide.serie}', fonte, 'T', 'C', False)
        self.caixa_de_texto(posicao_x + 2, posicao_y, x2, 12, f'FOLHA {self.page_no()}/{{nb}}', fonte, 'T', 'C', False)
        posicao_x += x2
        b_largura = largura_ult_caixa - 4
        b_altura = 12
        chave_nfe = self.nfe.id.replace('NFe', '')
        self.codigo_barras_128(posicao_x + 2, y + 2, chave_nfe, b_largura, b_altura)
        fonte.tamanho = 6
        fonte.estilo = ''
        posicao_y = y + 16
        self.caixa_de_texto(posicao_x, posicao_y, largura_ult_caixa, 8, '', fonte, 'T', 'L')
        posicao_y = posicao_y + self.caixa_de_texto(posicao_x, posicao_y, largura_ult_caixa, 8, f'CHAVE DE ACESSO', fonte, 'T', 'L', False) + 1
        fonte.tamanho = 9
        fonte.estilo = 'B'
        posicao_y = posicao_y + self.caixa_de_texto(posicao_x, posicao_y, largura_ult_caixa, 8, f_espaco_a_cada(chave_nfe, 4), fonte, 'T', 'L', False) + 3
        fonte.tamanho = 8
        fonte.estilo = ''
        posicao_y = posicao_y + self.caixa_de_texto(posicao_x, posicao_y, largura_ult_caixa, 8,
                                                    'Consulta de autenticidade no portal nacional da NF-e \nwww.nfe.fazenda.gov.br/portal ou no site da Sefaz '
                                                    'Autorizadora', fonte, 'T', 'C', False)
