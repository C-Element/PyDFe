from collections import OrderedDict
from datetime import datetime

from xmltodict import parse as x2d_parse

from .DFePDF import FontePDF, DFePDF
from .dfe import ler_data_hora, InfNFe, Endereco
from .formatos import f_dma, f_dmah, f_moeda, f_int_milhar, f_cep, f_fone, f_espaco_a_cada, f_cnpj, f_cpf, f_hora, f_dec_milhar, f_cst, f_relevante, f_ma


def construir_endereco(obj_end: Endereco, com_endereco: bool = True, com_cep: bool = False, com_cidade: bool = True, com_fone: bool = False,
                       com_bairro: bool = True) -> str:
    retorno = ''

    def se_tem(texto: str = ' - '):
        if len(retorno) > 0:
            return texto
        return ''

    if com_endereco:
        retorno += f'{obj_end.logradouro}, {obj_end.numero} - {obj_end.complemento}'
    if com_bairro:
        retorno += se_tem(', ') + f'{obj_end.bairro}'
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
        self.protocolo = ''
        self.data_recebimento = None
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
            if chave == 'protNFe':
                self.preencher_prot_nfe(valor)

    def preencher_nfe(self, dado: OrderedDict) -> None:
        for chave, valor in dado.items():
            if chave == 'infNFe':
                self.infNFe = InfNFe(valor)

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

    def gerar_pdf(self, caminho: str):
        danfe = DANFe(self)
        danfe.add_page()
        danfe.inserir_produtos()
        danfe.output(caminho, 'F')


class DANFe(DFePDF):
    def __init__(self, nfe: NFe):
        super().__init__()
        self.nfe = nfe.infNFe
        self.protocolo = nfe.protocolo
        self.data_recebimento = nfe.data_recebimento
        self.debugNFe = nfe
        self.y_agora = 0
        fonte = FontePDF()
        self.configurar_fonte(fonte)
        self.largura_codigo = self.get_string_width('0000000000')
        self.largura_barras = self.get_string_width('00000000000000')
        self.largura_ncm = self.get_string_width('000000000')
        self.largura_cst_un = self.get_string_width('0000')
        self.largura_cfop_aliq = self.get_string_width('00000')
        self.largura_qt = self.get_string_width('000000')
        self.largura_tributos = self.get_string_width('TRIBUTOS')
        self.largura_descricao = self.largura_max - self.x - self.largura_codigo - self.largura_barras - self.largura_ncm - self.largura_cst_un * 3 - \
                                 self.largura_cfop_aliq - self.largura_qt * 5 - self.largura_tributos

    def construir_documentos_referenciados(self) -> str:
        retorno = ''
        for refs in self.nfe.ide.documentos_referenciados:
            for doc in refs.chave_nfe_ref:
                retorno += f'\nNFe Ref.: série:{doc[22:25]} número:{doc[25:34]} emit:{f_cnpj(doc[6:20])} em {doc[4:6]}/20{doc[2:4]} [{f_espaco_a_cada(doc, 4)}]'
            for doc in refs.chave_cte_ref:
                retorno += f'\nCTe Ref.: série:{doc[22:25]} número:{doc[25:34]} emit:{f_cnpj(doc[6:20])} em {doc[4:6]}/20{doc[2:4]} [{f_espaco_a_cada(doc, 4)}]'
            for doc in refs.informacao_ecf_ref:
                retorno += f'\nECF Ref.: modelo: {doc.modelo} ECF:{doc.numero_ecf} COO:{doc.numero_coo}'
            for doc in refs.informacao_nfe_pr_ref:
                retorno += f'\nNFP Ref.: série:{doc.serie} número:{doc.nf} emit:{f_cnpj(doc.cnpj) if doc.cnpj else f_cpf(doc.cpf)} em {f_ma(doc.emissao)} ' \
                           f'modelo: {doc.modelo} IE:{doc.inscricao_estadual}'
            for doc in refs.informacao_nf_ref:
                retorno += f'\nNF  Ref.: série:{doc.serie} número:{doc.nf} emit:{f_cnpj(doc.cnpj)} em {f_ma(doc.emissao)} modelo: {doc.modelo}'
        return retorno if retorno == '' else (retorno + '\n')

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
        if self.page_no() == 1:
            posicao_y = y = self.canhoto()
        else:
            posicao_y = y = self.y
        posicao_x = x = round((self.largura_max - self.x) * 0.40)
        x2 = round((self.largura_max - self.x) * 0.20)
        largura_ult_caixa = self.largura_max - x - x2 - self.x
        fonte = FontePDF(tamanho=6)
        self.caixa_de_texto(self.x, y, x, a_cabecalho, fonte=fonte)
        self.caixa_de_texto(self.x + x, y, x2, a_cabecalho)
        self.caixa_de_texto(self.x + x + x2, y, largura_ult_caixa, a_cabecalho)
        tamanho = self.font_size
        posicao_y += self.caixa_de_texto(self.x, y, x, tamanho, "IDENTIFICAÇÃO DO EMITENTE", fonte, 'T', 'C', False) + 2
        fonte.tamanho = 12
        fonte.estilo = 'B'
        posicao_y += self.caixa_de_texto(self.x, posicao_y, x, 12, f'{self.nfe.emitente.razao_social} - {self.nfe.emitente.fantasia}', fonte, 'T',
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
        posicao_y += self.caixa_de_texto(posicao_x, posicao_y, x2, 12, 'Documento Auxiliar da Nota Fiscal Eletrônica', fonte, 'T', 'C', False) + 2
        a_quad = self.caixa_de_texto(posicao_x + 2, posicao_y, x2, 12, f'{entrada}\n2 - SAÍDA', fonte, 'T', 'L', False)
        fonte.tamanho = 12
        fonte.estilo = 'B'
        posicao_y += self.caixa_de_texto(posicao_x + self.get_string_width(entrada) + 7, posicao_y, self.get_string_width('0000'), a_quad,
                                         str(self.nfe.ide.tipo_nf), fonte, 'B', 'C') + 2
        fonte.tamanho = 10
        fonte.estilo = 'B'
        posicao_y += self.caixa_de_texto(posicao_x, posicao_y, x2, 12, f'{f_int_milhar(self.nfe.ide.nf)}', fonte, 'T', 'C', False)
        posicao_y += self.caixa_de_texto(posicao_x, posicao_y, x2, 12, f'SÉRIE {self.nfe.ide.serie}', fonte, 'T', 'C', False)
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
        posicao_y += self.caixa_de_texto(posicao_x, posicao_y, largura_ult_caixa, 8, f'CHAVE DE ACESSO', fonte, 'T', 'L', False) + 1
        fonte.tamanho = 9
        fonte.estilo = 'B'
        posicao_y += self.caixa_de_texto(posicao_x, posicao_y, largura_ult_caixa, 8, f_espaco_a_cada(chave_nfe, 4), fonte, 'T', 'L', False) + 3
        fonte.tamanho = 8
        fonte.estilo = ''
        self.caixa_de_texto(posicao_x, posicao_y, largura_ult_caixa, 8,
                            'Consulta de autenticidade no portal nacional da NF-e \nwww.nfe.fazenda.gov.br/portal ou no site da Sefaz Autorizadora', fonte,
                            'T', 'C', False)
        fonte.tamanho = 6
        posicao_y = y + a_cabecalho
        largura_ult_caixa = round(x * 0.85)
        largura_pri_caixa = self.largura_max - largura_ult_caixa
        largura_ult_caixa -= self.x
        self.caixa_de_texto(self.x, posicao_y, largura_pri_caixa, 6, 'NATUREZA DA OPERAÇÃO', fonte)
        self.caixa_de_texto(self.x + largura_pri_caixa, posicao_y, largura_ult_caixa, 6, 'PROTOCOLO DE AUTORIZAÇÃO DE USO', fonte)
        fonte.tamanho = 9
        fonte.estilo = 'B'
        y_temp = posicao_y
        posicao_y += 0.5 + self.caixa_de_texto(self.x, posicao_y, largura_pri_caixa, 6, self.nfe.ide.natureza_operacao, fonte, 'B', 'L', False)
        if self.protocolo and self.data_recebimento:
            self.caixa_de_texto(self.x + largura_pri_caixa, y_temp, largura_ult_caixa, 6, f'{self.protocolo} - {f_dmah(self.data_recebimento)}', fonte, 'B',
                                'C', False)
        largura_pri_caixa = round(self.largura_max * 0.33) - self.x
        largura_ult_caixa = self.largura_max - (largura_pri_caixa * 2) - self.x
        fonte.tamanho = 6
        fonte.estilo = ''
        self.caixa_de_texto(self.x, posicao_y, largura_pri_caixa, 6, 'INSCRIÇÃO ESTADUAL', fonte)
        self.caixa_de_texto(self.x + largura_pri_caixa, posicao_y, largura_pri_caixa, 6, 'INSC. EST. DO SUBST. TRIBUTARIO', fonte)
        self.caixa_de_texto(self.x + largura_pri_caixa * 2, posicao_y, largura_ult_caixa, 6, 'CNPJ', fonte)
        fonte.tamanho = 10
        self.caixa_de_texto(self.x, posicao_y, largura_pri_caixa, 6, self.nfe.emitente.inscricao_estadual, fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_pri_caixa, posicao_y, largura_pri_caixa, 6, self.nfe.emitente.inscricao_estadual_st, fonte, 'B', 'R', borda=False)
        posicao_y += 1 + self.caixa_de_texto(self.x + largura_pri_caixa * 2, posicao_y, largura_ult_caixa, 6, f_cnpj(self.nfe.emitente.cnpj), fonte,
                                             'B', 'R', borda=False)

        if self.page_no() == 1:
            posicao_y = self.destinatario_emitente(posicao_y)
            posicao_y = self.duplicatas(posicao_y)
            posicao_y = self.imposto(posicao_y)
            posicao_y = self.transportador(posicao_y)
        self.y_agora = self.cabecalho_produtos(posicao_y)

    def destinatario_emitente(self, posicao_y: int) -> int:
        fonte = FontePDF(tamanho=7, estilo='B')
        largura_maior = round(self.largura_max * 0.68) - self.x
        largura_media = round(self.largura_max * 0.22) - self.x
        largura_menor = self.largura_max - largura_maior - largura_media - self.x
        posicao_y += 1 + self.caixa_de_texto(self.x, posicao_y, self.largura_max, 8, 'DESTINATÁRIO/EMITENTE', fonte, borda=False)
        fonte.tamanho = 6
        fonte.estilo = ''
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, 'NOME/RAZÃO SOCIAL', fonte)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_media, 6, 'CNPJ', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_media, posicao_y, largura_menor, 6, 'DATA DA EMISSÃO', fonte)
        fonte.tamanho = 10
        if self.nfe.destinatario.cnpj:
            cnpj_cpf = f_cpf(self.nfe.destinatario.cnpj)
        else:
            cnpj_cpf = f_cnpj(self.nfe.destinatario.cpf)
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, self.nfe.destinatario.razao_social, fonte, 'B', borda=False, forcar=True)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_media, 6, cnpj_cpf, fonte, 'B', 'R', borda=False)
        posicao_y += 0.5 + self.caixa_de_texto(self.x + largura_maior + largura_media, posicao_y, largura_menor, 6, f_dma(self.nfe.ide.data_emissao),
                                               fonte, 'B', 'R', borda=False)
        fonte.tamanho = 6
        largura_maior -= largura_menor
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, 'ENDERECO', fonte)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_media, 6, 'BAIRRO', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_media, posicao_y, largura_menor, 6, 'CEP', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_media + largura_menor, posicao_y, largura_menor, 6, 'DATA DA SAÍDA', fonte)
        fonte.tamanho = 10
        fonte.estilo = ''
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, construir_endereco(self.nfe.destinatario.endereco, com_cidade=False, com_bairro=False), fonte,
                            'B', borda=False, forcar=True)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_media, 6,
                            construir_endereco(self.nfe.destinatario.endereco, com_endereco=False, com_cidade=False), fonte, 'B', borda=False, forcar=True)
        self.caixa_de_texto(self.x + largura_maior + largura_media, posicao_y, largura_menor, 6,
                            construir_endereco(self.nfe.destinatario.endereco, com_endereco=False, com_cidade=False, com_bairro=False, com_cep=True), fonte,
                            'B', 'R', borda=False)
        posicao_y += 0.5 + self.caixa_de_texto(self.x + largura_maior + largura_media + largura_menor, posicao_y, largura_menor, 6,
                                               f_dma(self.nfe.ide.data_saida_entrada), fonte, 'B', 'R', borda=False)
        fonte.tamanho = 6
        largura_uf = self.get_string_width('0000')
        largura_maior -= largura_uf
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, 'MUNICÍPIO', fonte)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_uf, 6, 'UF', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_uf, posicao_y, largura_menor, 6, 'FONE/FAX', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_uf + largura_menor, posicao_y, largura_media, 6, 'INSCRIÇÃO ESTADUAL', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_uf + largura_media + largura_menor, posicao_y, largura_menor, 6, 'HORA DA SAÍDA', fonte)
        fonte.tamanho = 10
        fonte.estilo = ''
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, self.nfe.destinatario.endereco.municipio, fonte, 'B', borda=False, forcar=True)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_uf, 6, self.nfe.destinatario.endereco.uf, fonte, 'B', borda=False)
        self.caixa_de_texto(self.x + largura_maior + largura_uf, posicao_y, largura_menor, 6, f_fone(self.nfe.destinatario.endereco.telefone), fonte,
                            'B', 'R', borda=False, forcar=True)
        self.caixa_de_texto(self.x + largura_maior + largura_uf + largura_menor, posicao_y, largura_media, 6, self.nfe.destinatario.inscricao_estadual, fonte,
                            'B', 'R', borda=False)
        posicao_y = posicao_y + 1 + self.caixa_de_texto(self.x + largura_maior + largura_uf + largura_media + largura_menor, posicao_y, largura_menor, 6,
                                                        f_hora(self.nfe.ide.data_saida_entrada), fonte, 'B', 'R', borda=False)
        return posicao_y

    def duplicatas(self, posicao_y: int) -> int:
        fonte = FontePDF(tamanho=7, estilo='B')
        incremento_y = 0
        posicao_y = posicao_y + 1 + self.caixa_de_texto(self.x, posicao_y, self.largura_max, 8, 'FATURAS/DUPLICATAS', fonte, borda=False)
        posicao_x = self.x
        fonte.tamanho = 10
        fonte.estilo = ''
        self.configurar_fonte(fonte)
        for duplicata in self.nfe.cobranca.duplicatas:
            texto = f'{f_dma(duplicata.vencimento)} {duplicata.numero} {f_moeda(duplicata.valor)}'
            largura = self.get_string_width(texto) + 2
            if posicao_x + largura > self.largura_max:
                posicao_x = self.x
                posicao_y += incremento_y
            incremento_y = self.caixa_de_texto(posicao_x, posicao_y, largura, 6, texto, fonte, 'C') + 1.2
            posicao_x += largura
        return posicao_y + incremento_y

    def imposto(self, posicao_y: int) -> int:
        fonte = FontePDF(tamanho=7, estilo='B')
        largura_maior = round(self.largura_max / 5)
        largura_maior_ult = self.largura_max - self.x - largura_maior * 4
        largura_menor = round(self.largura_max / 7)
        largura_menor_ult = self.largura_max - self.x - largura_menor * 6

        posicao_y += 1 + self.caixa_de_texto(self.x, posicao_y, self.largura_max, 8, 'CÁLCULO DO IMPOSTO', fonte, borda=False)
        fonte.tamanho = 6
        fonte.estilo = ''
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, 'BASE CALC ICMS', fonte, )
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_maior, 6, 'VALOR ICMS', fonte)
        self.caixa_de_texto(self.x + largura_maior * 2, posicao_y, largura_maior, 6, 'BASE CALC ICMS ST', fonte)
        self.caixa_de_texto(self.x + largura_maior * 3, posicao_y, largura_maior, 6, 'VALOR ICMS ST', fonte)
        self.caixa_de_texto(self.x + largura_maior * 4, posicao_y, largura_maior_ult, 6, 'TOTAL DOS PRODUTOS', fonte)
        fonte.tamanho = 10
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, f_dec_milhar(self.nfe.total.icms.valor_base_calculo), fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_maior, 6, f_dec_milhar(self.nfe.total.icms.valor), fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_maior * 2, posicao_y, largura_maior, 6, f_dec_milhar(self.nfe.total.icms.valor_base_calculo_st), fonte, 'B', 'R',
                            borda=False)
        self.caixa_de_texto(self.x + largura_maior * 3, posicao_y, largura_maior, 6, f_dec_milhar(self.nfe.total.icms.valor_st), fonte, 'B', 'R', borda=False)
        posicao_y += 0.5 + self.caixa_de_texto(self.x + largura_maior * 4, posicao_y, largura_maior_ult, 6, f_dec_milhar(self.nfe.total.icms.valor_produtos),
                                               fonte,
                                               'B', 'R', borda=False)

        fonte.tamanho = 6
        fonte.estilo = ''
        self.caixa_de_texto(self.x, posicao_y, largura_menor, 6, 'VALOR FRETE', fonte, )
        self.caixa_de_texto(self.x + largura_menor, posicao_y, largura_menor, 6, 'VALOR SEGURO', fonte)
        self.caixa_de_texto(self.x + largura_menor * 2, posicao_y, largura_menor, 6, 'VALOR DESCONTO', fonte)
        self.caixa_de_texto(self.x + largura_menor * 3, posicao_y, largura_menor, 6, 'OUTRAS DESP', fonte)
        self.caixa_de_texto(self.x + largura_menor * 4, posicao_y, largura_menor, 6, 'VALOR IPI', fonte)
        self.caixa_de_texto(self.x + largura_menor * 5, posicao_y, largura_menor, 6, 'VALOR APROX. TRIB.', fonte)
        self.caixa_de_texto(self.x + largura_menor * 6, posicao_y, largura_menor_ult, 6, 'TOTAL DA NOTA', fonte)
        fonte.tamanho = 10
        self.caixa_de_texto(self.x, posicao_y, largura_menor, 6, f_dec_milhar(self.nfe.total.icms.valor_frete), fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_menor, posicao_y, largura_menor, 6, f_dec_milhar(self.nfe.total.icms.valor_seguro), fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_menor * 2, posicao_y, largura_menor, 6, f_dec_milhar(self.nfe.total.icms.valor_desconto), fonte, 'B', 'R',
                            borda=False)
        self.caixa_de_texto(self.x + largura_menor * 3, posicao_y, largura_menor, 6, f_dec_milhar(self.nfe.total.icms.valor_outros), fonte, 'B', 'R',
                            borda=False)
        self.caixa_de_texto(self.x + largura_menor * 4, posicao_y, largura_menor, 6, f_dec_milhar(self.nfe.total.icms.valor_ipi), fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_menor * 5, posicao_y, largura_menor, 6, f_dec_milhar(self.nfe.total.icms.valor_total_tributos), fonte, 'B', 'R',
                            borda=False)
        posicao_y += self.caixa_de_texto(self.x + largura_menor * 6, posicao_y, largura_menor_ult, 6, f_dec_milhar(self.nfe.total.icms.valor_nf), fonte, 'B',
                                         'R', borda=False)
        return posicao_y

    def transportador(self, posicao_y: int) -> int:
        def get_por_conta(modalidade: int) -> str:
            if modalidade == 0:
                return '0-EMITENTE'
            if modalidade == 1:
                return '1-DESTINATARIO'
            if modalidade == 2:
                return '2-TERCEIRO'
            return '9-SEM FRETE'

        fonte = FontePDF(tamanho=7, estilo='B')
        posicao_y += 1 + self.caixa_de_texto(self.x, posicao_y, self.largura_max, 8, 'TRANSPORTADOR/VOLUMES TRANSPORTADOS', fonte, borda=False)
        fonte.tamanho = 10
        fonte.estilo = ''
        self.configurar_fonte(fonte)
        largura_uf = self.get_string_width('0000')
        largura_maior = round(self.largura_max * 0.4)
        largura_menor = round((self.largura_max - largura_maior) / 4)
        largura_menor_ult = round(self.largura_max - largura_maior - largura_menor * 3) - self.x + largura_uf
        fonte.tamanho = 6
        if self.nfe.transporte.transportador:
            razao_social = self.nfe.transporte.transportador.razao_social
            endereco = self.nfe.transporte.transportador.endereco
            municipio = self.nfe.transporte.transportador.municipio
            uf = self.nfe.transporte.transportador.uf
            inscricao_estadual = self.nfe.transporte.transportador.inscricao_estadual
            if self.nfe.transporte.transportador.cnpj:
                cnpj_cpf = f_cnpj(self.nfe.transporte.transportador.cnpj)
            else:
                cnpj_cpf = f_cnpj(self.nfe.transporte.transportador.cpf)
        else:
            razao_social = endereco = municipio = uf = inscricao_estadual = cnpj_cpf = ''

        if self.nfe.transporte.veiculo:
            rntc = self.nfe.transporte.veiculo.rntc
            placa = self.nfe.transporte.veiculo.placa
            uf_placa = self.nfe.transporte.veiculo.uf
        elif self.nfe.transporte.reboques:
            reboque = self.nfe.transporte.reboques[0]
            rntc = reboque.rntc
            placa = reboque.placa
            uf_placa = reboque.uf
        else:
            rntc = placa = uf_placa = ''

        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, 'NOME/RAZÃO SOCIAL', fonte)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_menor, 6, 'FRETE POR CONTA', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_menor, posicao_y, largura_menor - largura_uf, 6, 'CÓDIGO ANTT', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 2 - largura_uf, posicao_y, largura_menor - largura_uf, 6, 'PLACA DO VEÍC', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf * 2, posicao_y, largura_uf, 6, 'UF', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf, posicao_y, largura_menor_ult, 6, 'CPF/CNPJ', fonte)
        fonte.tamanho = 10
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 6, razao_social, fonte, 'B', borda=False, forcar=True)
        self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_menor, 6, get_por_conta(self.nfe.transporte.modalidade_frete), fonte, 'B', borda=False)
        self.caixa_de_texto(self.x + largura_maior + largura_menor, posicao_y, largura_menor - largura_uf, 6, rntc, fonte, 'B', borda=False)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 2 - largura_uf, posicao_y, largura_menor - largura_uf, 6, placa, fonte, 'B', borda=False)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf * 2, posicao_y, largura_uf, 6, uf_placa, fonte, 'B', borda=False)
        posicao_y += 0.5 + self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf, posicao_y, largura_menor_ult, 6, cnpj_cpf, fonte, 'B',
                                               borda=False)
        fonte.tamanho = 6
        self.caixa_de_texto(self.x, posicao_y, largura_maior + largura_menor, 6, 'ENDEREÇO', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_menor, posicao_y, largura_menor * 2 - largura_uf * 2, 6, 'MUNICÍPIO', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf * 2, posicao_y, largura_uf, 6, 'UF', fonte)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf, posicao_y, largura_menor_ult, 6, 'INSCRIÇÃO ESTADUAL', fonte)
        fonte.tamanho = 10
        self.caixa_de_texto(self.x, posicao_y, largura_maior + largura_menor, 6, endereco, fonte, 'B', borda=False, forcar=True)
        self.caixa_de_texto(self.x + largura_maior + largura_menor, posicao_y, largura_menor * 2 - largura_uf * 2, 6, municipio, fonte, 'B', borda=False,
                            forcar=True)
        self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf * 2, posicao_y, largura_uf, 6, uf, fonte, 'B', borda=False)
        posicao_y += 0.5 + self.caixa_de_texto(self.x + largura_maior + largura_menor * 3 - largura_uf, posicao_y, largura_menor_ult, 6, inscricao_estadual,
                                               fonte, 'B', borda=False, forcar=True)
        fonte.tamanho = 6
        largura_menor = round(self.largura_max / 6)
        largura_menor_ult = self.largura_max - self.x - largura_menor * 5
        self.caixa_de_texto(self.x, posicao_y, largura_menor_ult, 6, 'QUANTIDADE', fonte)
        self.caixa_de_texto(self.x + largura_menor_ult, posicao_y, largura_menor, 6, 'ESPÉCIE', fonte)
        self.caixa_de_texto(self.x + largura_menor_ult + largura_menor, posicao_y, largura_menor, 6, 'MARCA', fonte)
        self.caixa_de_texto(self.x + largura_menor_ult + largura_menor * 2, posicao_y, largura_menor, 6, 'NUMERAÇÃO', fonte)
        self.caixa_de_texto(self.x + largura_menor_ult + largura_menor * 3, posicao_y, largura_menor, 6, 'PESO BRUTO', fonte)
        self.caixa_de_texto(self.x + largura_menor_ult + largura_menor * 4, posicao_y, largura_menor, 6, 'PESO LIQUIDO', fonte)
        fonte.tamanho = 10
        especie = marca = numero = ''
        quantidade = peso_liq = peso_bruto = 0
        for vol in self.nfe.transporte.volumes:
            quantidade += vol.quantidade
            peso_liq += vol.peso_liquido
            peso_bruto += vol.peso_bruto
            especie = 'VARIAS' if vol.especie != especie and especie != '' else vol.especie
            marca = 'VARIAS' if vol.marca != marca and marca != '' else vol.marca
            numero = 'VARIOS' if vol.numercao != numero and numero != '' else vol.numercao
        self.caixa_de_texto(self.x, posicao_y, largura_menor_ult, 6, str(quantidade), fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_menor_ult, posicao_y, largura_menor, 6, especie, fonte, 'B', borda=False)
        self.caixa_de_texto(self.x + largura_menor_ult + largura_menor, posicao_y, largura_menor, 6, marca, fonte, 'B', borda=False)
        self.caixa_de_texto(self.x + largura_menor_ult + largura_menor * 2, posicao_y, largura_menor, 6, numero, fonte, 'B', 'R', borda=False)
        self.caixa_de_texto(self.x + largura_menor_ult + largura_menor * 3, posicao_y, largura_menor, 6, f_dec_milhar(peso_liq), fonte, 'B', 'R', borda=False)
        posicao_y += self.caixa_de_texto(self.x + largura_menor_ult + largura_menor * 4, posicao_y, largura_menor, 6, f_dec_milhar(peso_bruto), fonte, 'B', 'R',
                                         borda=False)
        return posicao_y

    def cabecalho_produtos(self, posicao_y: int) -> int:
        fonte = FontePDF(tamanho=7, estilo='B')
        posicao_y += 1 + self.caixa_de_texto(self.x, posicao_y, self.largura_max, 8, 'DADOS DOS PRODUTOS/SERVIÇOS', fonte, borda=False)
        fonte.tamanho = 6
        fonte.estilo = ''
        # Preenchendo toda a página
        if self.page_no() == 1:
            altura_pagina = self.altura_max - self.y - posicao_y - 29
        else:
            altura_pagina = self.altura_max - posicao_y
        self.caixa_de_texto(self.x, posicao_y, self.largura_codigo, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo, posicao_y, self.largura_descricao, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao, posicao_y, self.largura_barras, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras, posicao_y, self.largura_ncm, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm, posicao_y, self.largura_cst_un,
                            altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un,
                            posicao_y, self.largura_cfop_aliq, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un +
                            self.largura_cfop_aliq, posicao_y, self.largura_cst_un, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq, posicao_y, self.largura_qt, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt, posicao_y, self.largura_qt, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 2, posicao_y, self.largura_qt, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 3, posicao_y, self.largura_qt, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 4, posicao_y, self.largura_qt, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 5, posicao_y, self.largura_cst_un, altura_pagina)
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 3 +
                            self.largura_cfop_aliq + self.largura_qt * 5, posicao_y, self.largura_tributos, altura_pagina)

        self.caixa_de_texto(self.x, posicao_y, self.largura_codigo, 6, 'CÓDIGO PRODUTO', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo, posicao_y, self.largura_descricao, 6, 'DESCRIÇÃO DO PRODUTO/SERVIÇO', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao, posicao_y, self.largura_barras, 6, 'CÓDIGO DE BARRAS', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras, posicao_y, self.largura_ncm, 6, 'NCM/SH', fonte, 'C',
                            'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm, posicao_y, self.largura_cst_un,
                            6, 'CST', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un,
                            posicao_y, self.largura_cfop_aliq, 6, 'CFOP', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un +
                            self.largura_cfop_aliq, posicao_y, self.largura_cst_un, 6, 'UNID', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq, posicao_y, self.largura_qt, 6, 'QUANT', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt, posicao_y, self.largura_qt, 6, 'VALOR UNIT', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 2, posicao_y, self.largura_qt, 6, 'VALOR TOTAL', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 3, posicao_y, self.largura_qt, 6, 'B.CÁLC ICMS', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 4, posicao_y, self.largura_qt, 6, 'VALOR ICMS', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                            self.largura_cfop_aliq + self.largura_qt * 5, posicao_y, self.largura_cst_un, 6, 'ALIQ. ICSM', fonte, 'C', 'C')
        self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 3 +
                            self.largura_cfop_aliq + self.largura_qt * 5, posicao_y, self.largura_tributos, 6, 'V.APRÓX. TRIBUTOS', fonte, 'C', 'C')
        posicao_y += 6

        return posicao_y

    def inserir_produtos(self):
        fonte = FontePDF(tamanho=7)
        altura = 10
        for seq, detalhe in self.nfe.detalhamento.items():
            if self.page_no() == 1:
                acrescimo = 32
            else:
                acrescimo = 0
            if self.y + self.y_agora + acrescimo > self.altura_max:
                self.add_page()
            produto = detalhe.produto
            icms = detalhe.imposto.icms.icms
            posicao_y = self.y_agora
            descricao = f'{produto.descricao}\n{detalhe.informacoes_adicionais}'
            altura = 1 + self.caixa_de_texto(self.x + self.largura_codigo, posicao_y, self.largura_descricao, altura, descricao, fonte, 'T', 'L', borda=False)
            self.caixa_de_texto(self.x, posicao_y, self.largura_codigo, altura, produto.codigo, fonte, 'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao, posicao_y, self.largura_barras, altura, produto.gtin, fonte, 'T', 'R',
                                borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras, posicao_y, self.largura_ncm, altura,
                                str(produto.ncm), fonte, 'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm, posicao_y,
                                self.largura_cst_un, altura, f_cst(icms.cst), fonte, 'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un,
                                posicao_y, self.largura_cfop_aliq, altura, str(produto.cfop), fonte, 'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un +
                                self.largura_cfop_aliq, posicao_y, self.largura_cst_un, altura, produto.unidade, fonte, 'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                                self.largura_cfop_aliq, posicao_y, self.largura_qt, altura, f_relevante(produto.quantidade), fonte, 'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                                self.largura_cfop_aliq + self.largura_qt, posicao_y, self.largura_qt, altura, f_dec_milhar(produto.valor_unitario, 2), fonte,
                                'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                                self.largura_cfop_aliq + self.largura_qt * 2, posicao_y, self.largura_qt, altura, f_dec_milhar(produto.valor_total, 2), fonte,
                                'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                                self.largura_cfop_aliq + self.largura_qt * 3, posicao_y, self.largura_qt, altura, f_dec_milhar(icms.valor_base_calculo, 2),
                                fonte, 'T', 'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                                self.largura_cfop_aliq + self.largura_qt * 4, posicao_y, self.largura_qt, altura, f_dec_milhar(icms.valor_icms, 2), fonte, 'T',
                                'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 2 +
                                self.largura_cfop_aliq + self.largura_qt * 5, posicao_y, self.largura_cst_un, altura, f_relevante(icms.aliquota), fonte, 'T',
                                'R', borda=False)
            self.caixa_de_texto(self.x + self.largura_codigo + self.largura_descricao + self.largura_barras + self.largura_ncm + self.largura_cst_un * 3 +
                                self.largura_cfop_aliq + self.largura_qt * 5, posicao_y, self.largura_tributos, altura,
                                f_dec_milhar(detalhe.imposto.total_tributos, 2), fonte, 'T', 'R', borda=False)
            self.line(self.x, posicao_y + altura, self.largura_max, posicao_y + altura)
            self.y_agora += altura

    def rodape(self):
        if self.page_no() > 1:
            return
        fonte = FontePDF(tamanho=7, estilo='B')
        if self.nfe.retirada:
            re = self.nfe.retirada
            texto = f'LOCAL DE RETIRADA : {re.cnpj if re.cnpj else re.cpf} - {re.logradouro}, {re.numero} {re.complemento} - {re.bairro} -  ' \
                    f'{re.municipio}/{re.uf}\n\n\n\n'
        elif self.nfe.entrega:
            re = self.nfe.entrega
            texto = f'LOCAL DE ENTREGA: {re.cnpj if re.cnpj else re.cpf} - {re.logradouro}, {re.numero} {re.complemento} - {re.bairro} -  ' \
                    f'{re.municipio}/{re.uf}\n\n\n\n'
        else:
            texto = ''
        posicao_y = self.altura_max - 32
        largura_maior = round(self.largura_max * 0.6)
        largura_menor = self.largura_max - largura_maior - self.x
        posicao_y += 1 + self.caixa_de_texto(self.x, posicao_y, self.largura_max, 6, 'DADOS ADICIONAIS', fonte, borda=False)
        fonte.tamanho = 6
        fonte.estilo = ''
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 25, 'INFORMAÇÕES COMPLEMENTARES', fonte)
        posicao_y += 1 + self.caixa_de_texto(self.x + largura_maior, posicao_y, largura_menor, 25, 'RESERVADO AO FISCO', fonte)
        texto += self.construir_documentos_referenciados()

        if self.nfe.informacao_adicionais.informacoes_complementares:
            texto += f'Inf. Contribuinte: {self.nfe.informacao_adicionais.informacoes_complementares}\n'
        self.caixa_de_texto(self.x, posicao_y, largura_maior, 25, texto, fonte, borda=False)
        posicao_y += 22
        self.caixa_de_texto(self.x, posicao_y, self.largura_max, 6, f'IMPRESSO EM: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', fonte, borda=False)
        self.caixa_de_texto(self.x, posicao_y, self.largura_max - self.x, 6, f'SIGe | Desenvolvimento: TI - Casa Norte LTDA', fonte, borda=False,
                            alinhamento_h='R')
