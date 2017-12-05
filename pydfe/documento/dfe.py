from collections import OrderedDict
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List


# Exceções
class ErroDeInicializacao(Exception):
    pass


class DocumentoInvalido(Exception):
    pass


# classes DFe
class BaseObjDFe(object):
    def __init__(self, dado: OrderedDict):
        self._conteudo_xml: OrderedDict = dado
        self._preencher()

    def _preencher(self) -> None:
        pass


class Cartao(BaseObjDFe):  # [#YA04]
    def __init__(self, dado: OrderedDict):
        self.autorizacao: str = str()  # Identifica o número da autorização da transação da operação com cartão de crédito e/ou débito :: <cAut> [#YA07]
        self.bandeira: str = str()  # Bandeira da operadora de cartão de crédito e/ou débito 01=Visa; 02=Mastercard; 03=American Express; 04=Sorocred;
        # 99=Outros :: <tBand> [#YA06]
        self.cnpj: int = int()  # Informar o CNPJ da Credenciadora de cartão de crédito / débito :: <CNPJ> [#YA05]
        super().__init__(dado)

    def _preencher(self) -> None:
        for chave, valor in self._conteudo_xml.items():
            if chave == 'cAut':
                self.autorizacao = ler_texto(valor)
            elif chave == 'tBand':
                self.bandeira = ler_texto(valor)
            elif chave == 'CNPJ':
                self.cnpj = int(valor)

    def descricao_bandeira(self):
        descricao = 'Outros'
        if self.bandeira == '01':
            descricao = 'Visa'
        elif self.bandeira == '02':
            descricao = 'Mastercard'
        elif self.bandeira == '03':
            descricao = 'American Express'
        elif self.bandeira == '02':
            descricao = 'Sorocred'
        return descricao


class Cobranca(BaseObjDFe):  # [#Y01]
    def __init__(self, dado: OrderedDict):
        self.duplicatas: ListaDuplicatas = []  # :: <dup> [#Y07]
        self.fatura: Fatura = None  # :: <fat> [#Y02]
        super().__init__(dado)

    def _preencher(self) -> None:
        for chave, valor in self._conteudo_xml.items():
            if chave == 'dup':
                if isinstance(valor, list):
                    for dup in valor:
                        duplicata = Duplicata(dup)
                        self.duplicatas.append(duplicata)
                else:
                    duplicata = Duplicata(valor)
                    self.duplicatas.append(duplicata)
            elif chave == 'fat':
                self.fatura = Fatura(valor)


class COFINS(BaseObjDFe):  # {#S01}
    def __init__(self, dado: OrderedDict):
        self.cofins_aliq: COFINSAliquota = None  # Grupo COFINS tributado pela alíquota  :: <COFINSAliq> [#S02]
        self.cofins_nao_tributado: COFINSNaoTributado = None  # Grupo COFINS não tributado :: <COFINSNT> [#S04]
        self.cofins_outros: COFINSOutros = None  # Grupo COFINS Outras Operações :: <COFINSOutr> [#S05]
        self.cofins_quantidade: COFINSQuantidade = None  # Grupo de COFINS tributado por Qtde  :: <COFINSQtde> [#S03]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'COFINSAliq':
                self.cofins_aliq = COFINSAliquota(valor)
            elif chave == 'COFINSNT':
                self.cofins_nao_tributado = COFINSNaoTributado(valor)
            elif chave == 'COFINSOutr':
                self.cofins_outros = COFINSOutros(valor)
            elif chave == 'COFINSQtde':
                self.cofins_quantidade = COFINSQuantidade(valor)


class COFINSAliquota(BaseObjDFe):  # {#S02}
    def __init__(self, dado: OrderedDict):
        self.aliquota: Decimal = Decimal()  # <pCOFINS> [#S08]
        self.cst: int = int()  # 01=Operação Tributável (base de cálculo = valor da operação alíquota normal (cumulativo/não cumulativo)); 02=Operação
        # Tributável (base de cálculo = valor da operação (alíquota diferenciada)); :: <CST> [#S06]
        self.valor: Decimal = Decimal()  # <vCOFINS> [#S11]
        self.valor_base_calculo: Decimal = Decimal()  # <vBC> [#S07]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pCOFINS':
                self.aliquota = Decimal(valor)
            elif chave == 'CST':
                self.cst = int(valor)
            elif chave == 'vCOFINS':
                self.valor = Decimal(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)


class COFINSNaoTributado(BaseObjDFe):  # {#S04}
    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # 04=Operação Tributável (tributação monofásica (alíquota zero)); 05=Operação Tributável (Substituição Tributária);
        # 06=Operação Tributável (alíquota zero); 07=Operação Isenta da Contribuição;08=Operação Sem Incidência da Contribuição;09=Operação com Suspensão da
        # Contribuição;  :: <CST> [#S06]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)


class COFINSOutros(COFINSAliquota):  # {#S05}
    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # 49=Outras Operações de Saída;50=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Tributada no Mercado
        # Interno; 51=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Não Tributada no Mercado Interno;52=Operação com Direito a Crédito –
        # Vinculada Exclusivamente a Receita de Exportação;53=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e Não-Tributadas no Mercado
        # Interno; 54=Operação com Direito a Crédito - Vinculada a Receitas Tributadas no Mercado Interno e de Exportação;55=Operação com Direito a Crédito -
        # Vinculada a Receitas NãoTributadas no Mercado Interno e de Exportação;56=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e
        # Não-Tributadas no Mercado Interno, e de Exportação;60=Crédito Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Tributada no
        # Mercado Interno;61=Crédito Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Não-Tributada no Mercado Interno; 62=Crédito
        # Presumido - Operação de  Aquisição Vinculada Exclusivamente a Receita de Exportação;63=Crédito Presumido - Operação de Aquisição Vinculada a Receitas
        # Tributadas e Não-Tributadas no Mercado Interno;64=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Tributadas no Mercado Interno e de
        # Exportação;65=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Não-Tributadas no Mercado Interno e de Exportação;66=Crédito Presumido -
        # Operação de Aquisição Vinculada a Receitas Tributadas e Não-Tributadas no Mercado Interno, e de Exportação;67=Crédito Presumido - Outras Operações;
        # 70=Operação de Aquisição sem Direito a Crédito; 71=Operação de Aquisição com Isenção;72=Operação de Aquisição com Suspensão;73=Operação de Aquisição
        # a Alíquota Zero;74=Operação de Aquisição; sem Incidência da Contribuição;75=Operação de Aquisição por Substituição Tributária;98=Outras Operações de
        # Entrada;99=Outras Operações;
        self.quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#Q10]
        self.valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#Q11]
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)
            elif chave == 'qBCProd':
                self.quantidade_base_calculo = Decimal(valor)
            if chave == 'vAliqProd':
                self.valor_aliquota = Decimal(valor)


class COFINSQuantidade(BaseObjDFe):  # {#S03}
    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # 03=Operação Tributável (base de cálculo = quantidade vendida x alíquota por unidade de produto); :: <CST> [#S06]
        self.quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#S09]
        self.valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#S10]
        self.valor: Decimal = Decimal()  # <vCOFINS> [#S11]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)
            elif chave == 'qBCProd':
                self.quantidade_base_calculo = Decimal(valor)
            elif chave == 'vAliqProd':
                self.valor_aliquota = Decimal(valor)
            elif chave == 'vCOFINS':
                self.valor = Decimal(valor)


class COFINSST(COFINSOutros):  # [#T01]
    def __init__(self, dado: OrderedDict):
        super().__init__(dado)


class Destinatario(BaseObjDFe):  # [#E01]
    def __init__(self, dado: OrderedDict):
        self.cnpj: int = int()  # :: <CNPJ> [#E02]
        self.cpf: int = int()  # :: <CPF> [#E03]
        self.email: str = str()  # :: <email> [#E19]
        self.id_estrangeiro: str = str()  # Identificação do destinatário no caso de comprador estrangeiro :: <idEstrangeiro> [#E03a]
        self.inscricao_municipal_tomador_servico: str = str()  # Campo opcional, pode ser informado na NF-e conjugada, com itens de produtos sujeitos ao ICMS
        # e itens de serviços sujeitos ao ISSQN. :: <IM> [#E20]
        self.indicador_inscricao_estadual: int = int()  # Indicador da IE do Destinatário: 1=Contribuinte ICMS (informar a IE do destinatário); 2=Contribuinte
        # isento de Inscrição no cadastro de Contribuintes do ICMS; 9=Não Contribuinte, que pode ou não possuir Inscrição Estadual no Cadastro de Contribuintes
        # do ICMS. Nota 1: No caso de NFC-e informar indIEDest=9 e não informar a tag IE do destinatário; Nota 2: No caso de operação com o Exterior informar
        # indIEDest=9 e não informar a tag IE do destinatário; Nota 3: No caso de Contribuinte Isento de Inscrição (indIEDest=2), não informar a tag IE do
        # destinatário. :: <indIEDest> [#E16a]
        self.inscricao_estadual: str = str()  # :: <IE> [#E17]
        self.inscricao_suframa: str = str()  # :: <ISUF> [#E18]
        self.endereco: Endereco = None  # :: <enderDest> [#E05]
        self.razao_social: str = str()  # Razão Sócial ou Nome do destinatário :: <xNome> [#E04]

        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'CPF':
                self.cpf = int(valor)
            elif chave == 'email':
                self.email = ler_texto(valor)
            elif chave == 'idEstrangeiro':
                self.id_estrangeiro = ler_texto(valor)
            elif chave == 'IM':
                self.inscricao_municipal_tomador_servico = ler_texto(valor)
            elif chave == 'indIEDest':
                self.indicador_inscricao_estadual = int(valor)
            elif chave == 'IE':
                self.inscricao_estadual = ler_texto(valor)
            elif chave == 'ISUF':
                self.inscricao_suframa = ler_texto(valor)
            elif chave == 'enderDest':
                self.endereco = Endereco(valor)
            elif chave == 'xNome':
                self.razao_social = ler_texto(valor)


class Detalhamento(BaseObjDFe):  # [#H01]
    def __init__(self, dado: OrderedDict):
        self.imposto: Imposto = None  # Tributos incidentes no Produto ou Serviço. :: <impost> [#M01]
        self.informacoes_adicionais: str = str()  # Informações Adicionais :: <infAdProd> [#V01]
        self.numero_item: int = int()  # Número do item :: @nItem [#H02]
        self.produto: Produto = None  # Detalhamento de Produtos e Serviços :: <prod> [#I01]
        self.tributos_devolvidos: TributoDevolvido = None  # Informação do Imposto devolvido :: <impostoDevol> [#UA01]

        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'imposto':
                self.imposto = Imposto(valor)
            elif chave == 'infAdProd':
                self.informacoes_adicionais = ler_texto(valor)
            elif chave == '@nItem':
                self.numero_item = int(valor)
            elif chave == 'prod':
                self.produto = Produto(valor)
            elif chave == 'importDevol':
                self.tributos_devolvidos = TributoDevolvido(valor)


class DocumentoReferenciado(BaseObjDFe):  # [#BA01]

    def __init__(self, dado: OrderedDict):
        self.chave_nfe_ref: List[int] = []  # Chave de acesso da NF-e referenciada :: <refNFe> [#BA02]
        self.informacao_nf_ref: List[NFeReferenciada] = []  # Informação da NF modelo 1/1A referenciada :: <refNF> [#BA03]
        self.informacao_nfe_pr_ref: List[NFeReferenciadaProdutoRural] = []  # Informações da NF de produtor rural referenciada :: <refNFP> [#BA10]
        self.informacao_ecf_ref: List[ECFReferenciado] = []  # Informações do Cupom Fiscal referenciado :: <refECF> [#BA20]
        self.chave_cte_ref: List[int] = []  # Informações do CTe referenciado :: <refCTe> [#BA19]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'refNFe':
                if isinstance(valor, list):
                    for doc in valor:
                        documento = int(doc)
                        self.chave_nfe_ref.append(documento)
                else:
                    documento = int(valor)
                    self.chave_nfe_ref.append(documento)
            elif chave == 'refNF':
                if isinstance(valor, list):
                    for doc in valor:
                        documento = NFeReferenciada(doc)
                        self.informacao_nf_ref.append(documento)
                else:
                    documento = NFeReferenciada(valor)
                    self.informacao_nf_ref.append(documento)
            elif chave == 'refNFP':
                if isinstance(valor, list):
                    for doc in valor:
                        documento = NFeReferenciadaProdutoRural(doc)
                        self.informacao_nfe_pr_ref.append(documento)
                else:
                    documento = NFeReferenciadaProdutoRural(valor)
                    self.informacao_nfe_pr_ref.append(documento)
            elif chave == 'refECF':
                if isinstance(valor, list):
                    for doc in valor:
                        documento = ECFReferenciado(doc)
                        self.informacao_ecf_ref.append(documento)
                else:
                    documento = ECFReferenciado(valor)
                    self.informacao_ecf_ref.append(documento)
            elif chave == 'refCTe':
                if isinstance(valor, list):
                    for doc in valor:
                        documento = int(doc)
                        self.chave_cte_ref.append(documento)
                else:
                    documento = int(valor)
                    self.chave_cte_ref.append(documento)


class Duplicata(BaseObjDFe):  # [#Y07]

    def __init__(self, dado: OrderedDict):
        self.numero: str = str()  # :: <nDup> [#Y08]
        self.valor: Decimal = Decimal()  # :: <vDup> [#Y10]
        self.vencimento: date = None  # :: <dVenc> [#Y09]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'nDup':
                self.numero = ler_texto(valor)
            elif chave == 'vDup':
                self.valor = Decimal(valor)
            elif chave == 'dVenc':
                self.vencimento = ler_data(valor)


class ECFReferenciado(BaseObjDFe):  # [#BA20]

    def __init__(self, dado: OrderedDict):
        self.modelo: int = int()  # Modelo do cupom fiscal :: <mod> [#BA21]
        self.numero_coo: int = int()  # Número do Contador de Ordem de Operação - COO :: <nCOO> [#BA23]
        self.numero_ecf: int = int()  # Número de ordem sequencial do ECF :: <nECF> [#BA22]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'mod':
                self.modelo = int(valor)
            elif chave == 'nCOO':
                self.numero_coo = int(valor)
            elif chave == 'nECF':
                self.numero_ecf = int(valor)


class Emitente(BaseObjDFe):  # [#C01]

    def __init__(self, dado: OrderedDict):
        self.cnpj: int = int()  # :: <CNPJ> [#C02]
        self.cpf: int = int()  # :: <CPF> [#C02a]
        self.endereco = None  # :: <enderEmit> [#C05]
        self.fantasia: str = str()  # Nome Fantasia do emitente :: <xFant> [#C04]
        self.inscricao_estadual: str = str()  # :: <IE> [#C17]
        self.inscricao_estadual_st: str = str()  # :: <IEST> [#C18]
        self.razao_social: str = str()  # Razão Sócial ou Nome do emitente :: <xNome> [#C03]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'CPF':
                self.cpf = int(valor)
            elif chave == 'enderEmit':
                self.endereco = Endereco(valor)
            elif chave == 'xFant':
                self.fantasia = ler_texto(valor)
            elif chave == 'IE':
                self.inscricao_estadual = ler_texto(valor)
            elif chave == 'IEST':
                self.inscricao_estadual_st = ler_texto(valor)
            elif chave == 'xNome':
                self.razao_social = ler_texto(valor)


class Endereco(BaseObjDFe):  # [#C05]

    def __init__(self, dado: OrderedDict):
        self.bairro: str = str()  # :: <xBairro> [#C09] [#E09]
        self.cep: int = int()  # :: <CEP> [#C13] [#E13]
        self.codigo_municipio: int = int()  # :: <cMun> [#C10] [#E10]
        self.codigo_pais: int = int()  # :: <cPais> [#C14] [#E14]
        self.complemento: str = str()  # :: <xCpl> [#C08] [#E08]
        self.logradouro: str = str()  # :: <xLgr> [#C06] [#E06]
        self.municipio: str = str()  # :: <xMun> [#C11] [#E11]
        self.numero: str = str()  # :: <nro> [#C07] [#E07]
        self.pais: str = str()  # :: <xPais> [#C15] [#E15]
        self.telefone: int = int()  # :: <fone> [#C16] [#E16]
        self.uf: str = str()  # :: <UF> [#C12] [#E12]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'xBairro':
                self.bairro = ler_texto(valor)
            elif chave == 'CEP':
                self.cep = int(valor)
            elif chave == 'cMun':
                self.codigo_municipio = int(valor)
            elif chave == 'cPais':
                self.codigo_pais = int(valor)
            elif chave == 'xCpl':
                self.complemento = ler_texto(valor)
            elif chave == 'xLgr':
                self.logradouro = ler_texto(valor)
            elif chave == 'xMun':
                self.municipio = ler_texto(valor)
            elif chave == 'nro':
                self.numero = ler_texto(valor)
            elif chave == 'xPais':
                self.pais = ler_texto(valor)
            elif chave == 'fone':
                self.telefone = int(valor)
            elif chave == 'UF':
                self.uf = ler_texto(valor)


class EntregaRetirada(BaseObjDFe):  # [#F01]

    def __init__(self, dado: OrderedDict):
        self.bairro: str = str()  # :: <xBairro> [#F06]
        self.cnpj: int = int()  # CNPJ do Emitente :: <CNPJ> [#F02]
        self.cpf: int = int()  # CPF do Emitente :: <CPF> [#F02a]
        self.codigo_municipio: int = int()  # :: <cMun> [#F07]
        self.complemento: str = str()  # :: <xCpl> [#F05]
        self.logradouro: str = str()  # :: <xLgr> [#F03]
        self.municipio: str = str()  # :: <xMun> [#F08]
        self.numero: str = str()  # :: <nro> [#F04]
        self.uf: str = str()  # :: <UF> [#F09]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'xBairro':
                self.bairro = ler_texto(valor)
            elif chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'CPF':
                self.cpf = int(valor)
            elif chave == 'cMun':
                self.codigo_municipio = int(valor)
            elif chave == 'xCpl':
                self.complemento = ler_texto(valor)
            elif chave == 'xLgr':
                self.logradouro = ler_texto(valor)
            elif chave == 'xMun':
                self.municipio = ler_texto(valor)
            elif chave == 'nro':
                self.numero = ler_texto(valor)
            elif chave == 'UF':
                self.uf = ler_texto(valor)


class Fatura(BaseObjDFe):  # [#Y02]

    def __init__(self, dado: OrderedDict):
        self.numero: str = str()  # :: <nFat> [#Y03]
        self.valor_desconto: Decimal = Decimal()  # :: <vDesc> [#Y05]
        self.valor_liquido: Decimal = Decimal()  # :: <vLiq> [#Y06]
        self.valor_original: Decimal = Decimal()  # :: <vOrig> [#Y04]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'nFat':
                self.numero = ler_texto(valor)
            elif chave == 'vDesc':
                self.valor_desconto = Decimal(valor)
            elif chave == 'vLiq':
                self.valor_liquido = Decimal(valor)
            elif chave == 'vOrig':
                self.valor_original = Decimal(valor)


class ICMS(BaseObjDFe):  # [#N01]
    # icms00: ICMS00 = ICMS00()  # Tributada integralmente. :: <ICMS00> [#N02]
    # icms10: ICMS10 = ICMS10()  # Tributada e com cobrança do ICMS por substituição tributária. :: <ICMS10> [#N03]
    # icms20: ICMS20 = ICMS20()  # Tributação com redução de base de cálculo. :: <ICMS20> [#N04]
    # icms30: ICMS30 = ICMS30()  # Tributação Isenta ou não tributada e com cobrança do ICMS por substituição tributária. :: <ICMS30> [#N05]
    # icms4050: ICMS4050 = ICMS4050()  # Tributação Isenta, Não tributada ou Suspensão. :: <ICMS40> <ICMS41> <ICMS50> [#N06]
    # icms51: ICMS51 = ICMS51()  # Tributação com Diferimento (a exigência do preenchimento das informações do ICMS diferido fica a critério de cada
    # UF). :: <ICMS51> [#N07]
    # icms60: ICMS60 = ICMS60()  # Tributação ICMS cobrado anteriormente por substituição tributária. :: <ICMS60> [#N08]
    # icms70: ICMS7090 = ICMS7090()  # Tributação ICMS com redução de base de cálculo e cobrança do ICMS por substituição
    # tributária. :: <ICMS70> <ICMS90> [#N09]

    def __init__(self, dado: OrderedDict):
        self.icms = None  # Pode ser qualquer um dos tipos acima
        self.icms_partilha: ICMSPartilha = None  # Operação interestadual para consumidor final com partilha do ICMS devido na operação entre a UF de origem
        # e a do destinatário, ou a UF definida na legislação. :: <ICMSPart> [#N10a]
        self.icms_st: ICMSST = None  # Grupo de informação do ICMS ST devido para a UF de destino, nas operações interestaduais de produtos que tiveram retenção
        # antecipada de ICMS por ST na UF do remetente. Repasse via Substituto Tributário. . :: <ICMSST> [#N10b]

        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'ICMS00':
                self.icms = ICMS00(valor)
            elif chave == 'ICMS10':
                self.icms = ICMS10(valor)
            elif chave == 'ICMS20':
                self.icms = ICMS20(valor)
            elif chave == 'ICMS30':
                self.icms = ICMS30(valor)
            elif chave in ('ICMS40', 'ICMS41', 'ICMS50'):
                self.icms = ICMS4050(valor)
            elif chave == 'ICMS51':
                self.icms = ICMS51(valor)
            elif chave == 'ICMS60':
                self.icms = ICMS60(valor)
            elif chave in ('ICMS70', 'ICMS90'):
                self.icms = ICMS7090(valor)
            elif chave == 'ICMSPart':
                self.icms_partilha = ICMSPartilha(valor)
            elif chave == 'ICMSST':
                self.icms_st = ICMSST(valor)


class ICMS00(BaseObjDFe):  # [#N02]

    def __init__(self, dado: OrderedDict):
        self.aliquota: Decimal = Decimal()  # :: <pICMS> [#N16]
        self.cst: int = int()  # :: <CST> [#N12]
        self.modalidade_base_calculo: int = int()  # 0=Margem Valor Agregado (%); 1=Pauta (Valor);  2=Preço Tabelado Máx. (valor); 3=Valor da
        # operação. :: <CST> [#N13]
        self.origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
        # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
        # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
        # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
        # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
        # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
        self.valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#N15]
        self.valor_icms: Decimal = Decimal()  # :: <vICMS> [#N17]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pICMS':
                self.aliquota = Decimal(valor)
            elif chave == 'CST':
                self.cst = int(valor)
            elif chave == 'orig':
                self.origem = int(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vICMS':
                self.valor_icms = Decimal(valor)


class ICMS10(ICMS00):  # [#N03]

    def __init__(self, dado: OrderedDict):
        self.aliquota_st: Decimal = Decimal()  # :: <pICMSST> [#N22]
        self.cst: int = 10  # :: <CST> [#N12]
        self.modalidade_base_calculo_st: int = int()  # 0=Preço tabelado ou máximo sugerido; 1=Lista Negativa (valor); 2=Lista Positiva (valor); 3=Lista Neutra (valor);
        # 4=Margem Valor Agregado (%); 5=Pauta (valor); :: <modBCST> [#N18]
        self.mva_st: Decimal = Decimal()  # Percentual da margem de valor Adicionado do ICMS ST :: <pMVAST> [#N19]
        self.reducao_base_calculo_st: Decimal = Decimal()  # Percentual da Redução de BC do ICMS ST :: <pRedBCST> [#N20]
        self.valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#N21]
        self.valor_icms_st: Decimal = Decimal()  # :: <vICMSST> [#N23]
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pICMSST':
                self.aliquota_st = Decimal(valor)
            elif chave == 'modBCST':
                self.modalidade_base_calculo_st = int(valor)
            elif chave == 'pMVAST':
                self.mva_st = Decimal(valor)
            elif chave == 'pRedBCST':
                self.reducao_base_calculo_st = Decimal(valor)
            elif chave == 'vBCST':
                self.valor_base_calculo_st = Decimal(valor)
            elif chave == 'vICMSST':
                self.valor_icms_st = Decimal(valor)


class ICMS20(ICMS00):  # [#N04]

    def __init__(self, dado: OrderedDict):
        self.cst: int = 20  # :: <CST> [#N12]
        self.motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 3=Uso na agropecuária; 9=Outros; 12=Órgão de fomento e desenvolvimento
        # agropecuário. :: <motDesICMS> [#N28]
        self.reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
        self.valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'motDesICMS':
                self.motivo_icms_desonerado = ler_texto(valor)
            elif chave == 'pRedBC':
                self.reducao_base_calculo = Decimal(valor)
            elif chave == 'vICMSDeson':
                self.valor_icms_desonerado = Decimal(valor)


class ICMS30(BaseObjDFe):  # [#N05]

    def __init__(self, dado: OrderedDict):
        self.aliquota_st: Decimal = Decimal()  # :: <pICMSST> [#N22]
        self.cst: int = 30  # :: <CST> [#N12]
        self.origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto
        #  a indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo
        # de Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos
        # básicos de que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 -
        # Estrangeira - Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem
        # similar nacional, constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
        self.modalidade_base_calculo_st: int = int()  # 0=Preço tabelado ou máximo sugerido; 1=Lista Negativa (valor); 2=Lista Positiva (valor); 3=Lista Neutra
        # (valor); 4=Margem Valor Agregado (%); 5=Pauta (valor); :: <modBCST> [#N18]
        self.motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 6=Utilitários e Motocicletas da Amazônia Ocidental e Áreas de Livre
        # Comércio (Resolução 714/88 e 790/94 – CONTRAN e suas alterações); 7=SUFRAMA; 9=Outros;. :: <motDesICMS> [#N28]
        self.mva_st: Decimal = Decimal()  # Percentual da margem de valor Adicionado do ICMS ST :: <pMVAST> [#N19]
        self.reducao_base_calculo_st: Decimal = Decimal()  # Percentual da Redução de BC do ICMS ST :: <pRedBCST> [#N20]
        self.valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#N21]
        self.valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]
        self.valor_icms_st: Decimal = Decimal()  # :: <vICMSST> [#N23]

        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pICMSST':
                self.aliquota_st = Decimal(valor)
            elif chave == 'orig':
                self.origem = int(valor)
            elif chave == 'modBCST':
                self.modalidade_base_calculo_st = int(valor)
            elif chave == 'motDesICMS':
                self.motivo_icms_desonerado = int(valor)
            elif chave == 'pMVAST':
                self.mva_st = Decimal(valor)
            elif chave == 'pRedBCST':
                self.reducao_base_calculo_st = Decimal(valor)
            elif chave == 'vBCST':
                self.valor_base_calculo_st = Decimal(valor)
            elif chave == 'vICMSDeson':
                self.valor_icms_desonerado = Decimal(valor)
            elif chave == 'vICMSST':
                self.valor_icms_st = Decimal(valor)


class ICMS4050(BaseObjDFe):  # [#N06]

    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # :: <CST> [#N12]
        self.origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto
        # a indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
        # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos
        # de que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira
        # - Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar
        # nacional, constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
        self.motivo_icms_desonerado: int = int()  # Informar o motivo da desoneração: 1=Táxi; 3=Produtor Agropecuário; 4=Frotista/Locadora;
        # 5=Diplomático/Consular; 6=Utilitários e Motocicletas da Amazônia Ocidental e Áreas de Livre Comércio (Resolução 714/88 e 790/94 – CONTRAN e suas
        # alterações); 7=SUFRAMA; 8=Venda a Órgão Público; 9=Outros. (NT 2011/004); 10=Deficiente Condutor (Convênio ICMS 38/12); 11=Deficiente Não Condutor
        # (Convênio ICMS 38/12). :: <motDesICMS> [#N28]
        self.valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)
            elif chave == 'orig':
                self.origem = int(valor)
            elif chave == 'motDesICMS':
                self.motivo_icms_desonerado = int(valor)
            elif chave == 'vICMSDeson':
                self.valor_icms_desonerado = Decimal(valor)


class ICMS51(ICMS00):  # [#N07]

    def __init__(self, dado: OrderedDict):
        self.cst: int = 51  # :: <CST> [#N12]
        self.percentual_diferimento: Decimal = Decimal()  # :: <pDif> [#N16b]
        self.reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
        self.valor_icms_diferido: Decimal = Decimal()  # :: <vICMSDif> [#N16c]
        self.valor_icms_operacao: Decimal = Decimal()  # :: <vICMSOp> [#N16a]

        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pDif':
                self.percentual_diferimento = Decimal(valor)
            elif chave == 'pRedBC':
                self.reducao_base_calculo = Decimal(valor)
            elif chave == 'vICMSDif':
                self.valor_icms_diferido = Decimal(valor)
            elif chave == 'vICMSOp':
                self.valor_icms_operacao = Decimal(valor)


class ICMS60(BaseObjDFe):  # [#N08]

    def __init__(self, dado: OrderedDict):
        self.cst: int = 60  # :: <CST> [#N12]
        self.origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto
        # a indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
        # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos
        # de que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira
        # - Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar
        # nacional, constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
        self.valor_base_calculo_retido: Decimal = Decimal()  # :: <vBCSTRet> [#N26]
        self.valor_icms_retido: Decimal = Decimal()  # :: <vICMSSTRet> [#N27]

        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)
            elif chave == 'orig':
                self.origem = int(valor)
            elif chave == 'vBCICMSRet':
                self.valor_base_calculo_retido = Decimal(valor)
            elif chave == 'vICMSRet':
                self.valor_icms_retido = Decimal(valor)


class ICMS7090(ICMS10):  # [#N09] [#N10]
    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # :: <CST> [#N12]
        self.motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 3=Uso na agropecuária; 9=Outros; 12=Órgão de fomento e desenvolvimento
        # agropecuário. :: <motDesICMS> [#N28]
        self.reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
        self.valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]

        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'motDesICMS':
                self.motivo_icms_desonerado = ler_texto(valor)
            elif chave == 'pRedBC':
                self.reducao_base_calculo = Decimal(valor)
            elif chave == 'vICMSDeson':
                self.valor_icms_desonerado = Decimal(valor)


class ICMSPartilha(ICMS7090):  # [#N10a]
    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # :: <CST> [#N12]
        self.percentual_operacao_propria: Decimal = Decimal()  # :: <pBCOp> [#N25]
        self.uf_st: str = str()  # :: <UFST> [#24]
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pBCOp':
                self.percentual_operacao_propria = Decimal(valor)
            elif chave == 'UFST':
                self.uf_st = ler_texto(valor)


class ICMSST(ICMS60):  # [#N10b]
    def __init__(self, dado: OrderedDict):
        self.cst: int = 41  # :: <CST> [#N12]
        self.valor_base_calculo_st_destino: Decimal = Decimal()  # :: <vBCSTDest> [#N31]
        self.valor_icms_st_destino: Decimal = Decimal()  # :: <vICMSSTDest> [#N32]
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vBCSTDest':
                self.valor_base_calculo_retido = Decimal(valor)
            elif chave == 'vICMSSTDest':
                self.valor_icms_st_destino = ler_texto(valor)


class IDe(BaseObjDFe):  # [#B01]
    # data_contingenncia: datetime = None  # Data e Hora da entrada em contingência :: <dhCont>
    # justificativa_ccontigencia: str = str()  # Justificativa da entrada em contingência
    def __init__(self, dado: OrderedDict):
        self.cnf: int = int()  # Código numérico que compõe a Chave de Acesso. Número aleatório gerado pelo emitente :: <cNF> [#B03]
        self.data_emissao: datetime = None  # Data/Hora da emissão <dhEmi(V3)|dEmi(V2)> [#B09]
        self.data_saida_entrada: datetime = None  # Data/Hora da saída/entrada <dhSaiEnt > [#B10]
        self.documentos_referenciados: ListaDocumentoReferenciado = []  # Informação de Documentos Fiscais referenciados :: <NFref> #[#BA01]
        self.dv: int = int()  # DV da chave de acesso :: <cDV> [#B23]
        self.finalidade: int = int()  # Finalidade de emissão  1=NF-e normal; 2=NF-e complementar; 3=NF-e de ajuste 4=Devolução de mercadoria.:: <finNFe> [#B25]
        self.id_destino: int = int()  # Identificador de local de destino. 1=Op. interna; 2=Op. interestadual; 3=Op. com exterior :: <idDest> [#B11a]
        self.indicador_consumidor_final: int = int()  # Indica operação com Consumidor final. 0=Normal; 1=Consumidor final; :: <indFinal> [#B25a]
        self.indicador_pagamento: int = int()  # Indicador da forma de pagamento. 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros. :: <indPag> [#B05]
        self.indicador_presenca: int = int()  # Indicador de presença dp comprador. 0=Não se aplica (por exemplo, Nota Fiscal complementar ou de ajuste);
        # 1=Operação presencial; 2=Operação não presencial, pela Internet; 3=Operação não presencial, Teleatendimento; 4=NFC-e em operação com entrega a
        # domicílio; 9=Operação não presencial,  outros. :: <indPres> [#B25b]
        self.modelo: int = 55  # Código do Modelo do DFe. 55=NFe; 65=NFCe <mod> [#B06]
        self.municipio: int = int()  # Código do Município de Ocorrência <cMunFG> [#B12]
        self.natureza_operacao: str = str()  # Descrição da Natureza da Operação :: <natOp> [#B04]
        self.nf: int = int()  # Número do DFe <nNF> [#B08]
        self.processo_emissao: int = int()  # Processo de emissão da NF-e. 0=Emissão de NF-e com aplicativo do contribuinte; 1=Emissão de NF-e avulsa pelo
        # Fisco; 2=Emissão de NF-e avulsa, pelo contribuinte com seu certificado digital, através do site do Fisco; 3=Emissão NF-e pelo contribuinte com
        # aplicativo fornecido pelo Fisco. :: <procEmi> [#B26]
        self.serie: int = int()  # Série do DFe <serie> [#B07]
        self.tipo_ambiente: int = int()  # Identificação do ambiente 1=Produção/2=Homologação :: <tpAmb> [#B24]
        self.tipo_emissao: int = 1  # Tipo de Emissão do DFe 1=Emissão normal (não em contingência); 2=Contingência FS-IA, com impressão do DANFE em formulário
        # de segurança; 3=Contingência SCAN (Sistema de Contingência do Ambiente Nacional); 4=Contingência DPEC (Declaração Prévia da Emissão em Contingência);
        # 5=Contingência FS-DA, com impressão do DANFE em formulário de segurança; 6=Contingência SVC-AN (SEFAZ Virtual de Contingência do AN); 7=Contingência
        # SVC-RS (SEFAZ Virtual de Contingência do RS); 9=Contingência off-line da NFC-e (as demais opções de contingência são válidas também para a NFC-e).
        # Para a NFC-e somente estão disponíveis e são válidas as opções de contingência 5 e 9. :: <tpEmis> [#B22]
        self.tipo_impressao: int = 1  # Formato de Impressão do DANFE  <tpImp> [#B21]
        self.tipo_nf: int = int()  # Tipo de operação. 0=Entrada; 1=Saída :: <tpNF> [#B11]
        self.uf: str = str()  # Código da UF do emitente do DFe :: <cUF> [#B02]
        self.versao_processo: str = str()  # Versão do Processo de emissão da NF-e :: <verProc> [#B27]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'cNF':
                self.cnf = int(valor)
            elif chave == 'dhEmi':
                self.data_emissao = ler_data_hora(valor)
            elif chave == 'dEmi':
                self.data_emissao = ler_data_hora(valor+'T00:00:00')
            elif chave == 'dhSaiEnt':
                self.data_saida_entrada = ler_data_hora(valor)
            elif chave == 'NFref':
                if isinstance(valor, list):
                    for doc in valor:
                        documento = DocumentoReferenciado(doc)
                        self.documentos_referenciados.append(documento)
                else:
                    documento = DocumentoReferenciado(valor)
                    self.documentos_referenciados.append(documento)
            elif chave == 'cDV':
                self.dv = int(valor)
            elif chave == 'finNFe':
                self.finalidade = int(valor)
            elif chave == 'idDest':
                self.id_destino = int(valor)
            elif chave == 'indFinal':
                self.indicador_consumidor_final = int(valor)
            elif chave == 'indPag':
                self.indicador_pagamento = int(valor)
            elif chave == 'indPres':
                self.indicador_presenca = int(valor)
            elif chave == 'mod':
                self.modelo = int(valor)
            elif chave == 'cMunFG':
                self.municipio = int(valor)
            elif chave == 'natOp':
                self.natureza_operacao = ler_texto(valor)
            elif chave == 'nNF':
                self.nf = int(valor)
            elif chave == 'procEmi':
                self.processo_emissao = int(valor)
            elif chave == 'serie':
                self.serie = int(valor)
            elif chave == 'tpAmb':
                self.tipo_ambiente = int(valor)
            elif chave == 'tpEmis':
                self.tipo_emissao = int(valor)
            elif chave == 'tpImp':
                self.tipo_impressao = int(valor)
            elif chave == 'tpNF':
                self.tipo_nf = int(valor)
            elif chave == 'cUF':
                self.uf = ler_texto(valor)
            elif chave == 'verProc':
                self.versao_processo = ler_texto(valor)


class Imposto(BaseObjDFe):  # [#M01]
    def __init__(self, dado: OrderedDict):
        self.cofins: COFINS = None  # :: <COFINS> [#S01]
        self.cofins_st: COFINSST = None  # :: <COFINSST> [#T01]
        self.icms: ICMS = None  # Informações do ICMS da Operação própria e ST. :: <ICMS> [#N01]
        self.importacao: ImpostoImportacao = None  # Grupo Imposto de Importação :: <II> [#P01]
        self.ipi: IPI = None  # Grupo IPI Informar apenas quando o item for sujeito ao IPI :: <IPI> [#O01]
        self.issqn: ISSQN = None  # Campos para cálculo do ISSQN na NF-e conjugada, onde há a prestação de serviços sujeitos ao ISSQN e fornecimento de peças
        # sujeitas ao ICMS. Grupo ISSQN é mutuamente exclusivo com os grupos ICMS, IPI e II, isto é se ISSQN for informado os grupos ICMS, IPI e II não serão
        # informados e vice-versa :: <ISSQN> [#U01]
        self.pis: PIS = None  # ::<PIS> [#Q01}
        self.pis_st: PISST = None  # :: <PISST> [#R01]
        self.total_tributos: Decimal = Decimal()  # Valor aproximado total de tributos federais, estaduais e municipais. :: <vTotTrib> [#M02]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'COFINS':
                self.cofins = COFINS(valor)
            elif chave == 'COFINSST':
                self.cofins_st = COFINSST(valor)
            elif chave == 'ICMS':
                self.icms = ICMS(valor)
            elif chave == 'II':
                self.importacao = ImpostoImportacao(valor)
            elif chave == 'IPI':
                self.ipi = IPI(valor)
            elif chave == 'ISSQN':
                self.issqn = ISSQN(valor)
            elif chave == 'PIS':
                self.pis = PIS(valor)
            elif chave == 'PISST':
                self.pis_st = PISST(valor)
            elif chave == 'vTotTrib':
                self.total_tributos = Decimal(valor)


class ImpostoImportacao(BaseObjDFe):  # [#P01]

    def __init__(self, dado: OrderedDict):
        self.valor: Decimal = Decimal()  # :: <vII> [#P04]
        self.valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#P02]
        self.valor_desepesas_aduaneiras: Decimal = Decimal()  # :: <vDespAdu> [#P03]
        self.valor_iof: Decimal = Decimal()  # :: <vIOF> [#P05]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vII':
                self.valor = Decimal(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vDespAdu':
                self.valor_desepesas_aduaneiras = Decimal(valor)
            elif chave == 'vIOF':
                self.valor_iof = Decimal(valor)


class InformcaoAdicional(BaseObjDFe):  # [#Z01]

    def __init__(self, dado: OrderedDict):
        self.fisco: str = str()  # :: <infAdFisco> [#Z02]
        self.informacoes_complementares: str = str()  # :: <infCpl> [#Z03]
        self.observacoes_contribuinte: ListaObservacoesContribuinte = []  # :: <obsCont> [#Z04]
        self.observacoes_fisco: ListaObservacoesContribuinte = []  # :: <obsFisco> [#Z07]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'infAdFisco':
                self.fisco = ler_texto(valor)
            elif chave == 'infCpl':
                self.informacoes_complementares = ler_texto(valor)
            elif chave == 'obsCont':
                if isinstance(valor, list):
                    for obs in valor:
                        self.observacoes_contribuinte.append(ObservacaoContribuinte(obs))
                else:
                    self.observacoes_contribuinte.append(ObservacaoContribuinte(valor))
            elif chave == 'obsFisco':
                if isinstance(valor, list):
                    for obs in valor:
                        self.observacoes_fisco.append(ObservacaoFisco(obs))
                else:
                    self.observacoes_fisco.append(ObservacaoFisco(valor))


class InfNFe(BaseObjDFe):  # [#A01]
    def __init__(self, dado: OrderedDict):
        self.cobranca: Cobranca = None  # Grupo Cobrança :: <cobr> [#Y01]
        self.destinatario: Destinatario = None  # Identificação do Destinatário da NF-e  :: <dest> [#E01]
        self.detalhamento: DetalhesProduto = dict()  # Detalhamento de Produtos e Serviços :: <det> [#H01]
        self.emitente: Emitente = None  # Identificação do emitente da NF-e :: <emit> [#C01]
        self.entrega: EntregaRetirada = None  # Identificação do Local de entrega. Informar somente se diferente do endereço
        # destinatário. :: <entrega> [#F01]
        self.ide: IDe = None  # Identificação da NFe :: <ide> [#B01]
        self.id: str = str()  # Cheve NFe precedida da literal 'NFe' :: @Id [#A03]
        self.informacao_adicionais: InformcaoAdicional = None  # :: <infAdic> [#Z01]
        self.pagamentos: List[Pagamento] = []  # Grupo de Formas de Pagamento obrigatório para a NFC-e, a critério da UF. :: <pag> [#YA01]
        self.retirada: EntregaRetirada = None  # Identificação do Local de retirada. Informar somente se diferente do endereço do
        # remetente. :: <retirada> [#F01]
        self.total: Total = None  # Grupo Totais da NF-e :: <total> [#W01]
        self.transporte: Transporte = None  # Grupo Informações do Transporte :: <transp> [#X01]
        self.versao: str = str()  # Versão do layout NFe :: @versao [#A02]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'cobr':
                self.cobranca = Cobranca(valor)
            elif chave == 'dest':
                self.destinatario = Destinatario(valor)
            elif chave == 'det':
                if isinstance(valor, list):
                    for det in valor:
                        temp = Detalhamento(det)
                        self.detalhamento[temp.numero_item] = temp
                else:
                    temp = Detalhamento(valor)
                    self.detalhamento[temp.numero_item] = temp
            elif chave == 'emit':
                self.emitente = Emitente(valor)
            elif chave == 'entrega':
                self.entrega = EntregaRetirada(valor)
            elif chave == 'ide':
                self.ide = IDe(valor)
            elif chave == '@Id':
                self.id = ler_texto(valor)
            elif chave == 'infAdic':
                self.informacao_adicionais = InformcaoAdicional(valor)
            elif chave == 'pag':
                if isinstance(valor, list):
                    for pag in valor:
                        self.pagamentos.append(Pagamento(pag))
                else:
                    self.pagamentos.append(Pagamento(valor))
            elif chave == 'retirada':
                self.retirada = EntregaRetirada(valor)
            elif chave == 'total':
                self.total = Total(valor)
            elif chave == 'transp':
                self.transporte = Transporte(valor)
            elif chave == '@versao':
                self.versao = ler_texto(valor)


class IPI(BaseObjDFe):  # [# O01]
    def __init__(self, dado: OrderedDict):
        self.class_de_enquadramento: str = str()  # <clEnq> [#O02]
        self.cnpj_produtor: int = int()  # CNPJ do produtor da mercadoria, quando diferente do emitente. Somente para os casos de exportação direta ou
        # indireta. <CNPJProd> [#O03]
        self.codigo_enquadramento: str = str()  # Tabela a ser criada pela RFB, informar 999 enquanto a tabela não for criada :: <cEnq> [#O06]
        self.codigo_selo: str = str()  # :: <cSelo> [#O04]
        self.nao_tributado: IPINaoTributado = None  # Grupo CST 01, 02, 03, 04, 51, 52, 53, 54 e 55:: <IPINT> [#O08]
        self.quantidade_selo: int = int()  # :: <qSelo> [#O05]
        self.tributacao: IPITributacao = None  # Grupo do CST 00, 49, 50 e 99  :: <IPITrib> [#O07]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'clEnq':
                self.class_de_enquadramento = ler_texto(valor)
            elif chave == 'CNPJProd':
                self.cnpj_produtor = int(valor)
            elif chave == 'cEnq':
                self.codigo_enquadramento = ler_texto(valor)
            elif chave == 'cSelo':
                self.codigo_selo = ler_texto(valor)
            elif chave == 'IPINT':
                self.nao_tributado = IPINaoTributado(valor)
            elif chave == 'qSelo':
                self.quantidade_selo = int(valor)
            elif chave == 'IPITrib':
                self.tributacao = IPITributacao(valor)


class IPINaoTributado(BaseObjDFe):  # [#O08]
    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # 01=Entrada tributada com alíquota zero;02=Entrada isenta;03=Entrada não-tributada;04=Entrada imune;05=Entrada com
        # suspensão;51=Saída tributada com alíquota zero;52=Saída isenta;53=Saída não-tributada;54=Saída imune;55=Saída com suspensão :: <CST> [#O09]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)


class IPITributacao(BaseObjDFe):  # [#O07]

    def __init__(self, dado: OrderedDict):
        self.aliquota: Decimal = Decimal()  # :: <pIPI> [#O13]
        self.cst: int = int()  # 00=Entrada com recuperação de crédito; 49=Outras entradas; 50=Saída tributada; 99=Outras saídas :: <CST> [#O09]
        self.quantidade_unidade: Decimal = Decimal()  # :: <qUnid> [#O11]
        self.valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#O10]
        self.valor_unidade: Decimal = Decimal()  # :: <vUnid> [#O12]
        self.valor: Decimal = Decimal()  # :: <vIPI> [#O14]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pIPI':
                self.aliquota = Decimal(valor)
            elif chave == 'CST':
                self.cst = int(valor)
            elif chave == 'qUnid':
                self.quantidade_unidade = Decimal(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vUnid':
                self.valor_unidade = Decimal(valor)
            elif chave == 'vIPI':
                self.valor = Decimal(valor)


class ISSQN(BaseObjDFe):  # [#U01]

    def __init__(self, dado: OrderedDict):
        self.aliquota: Decimal = Decimal  # :: <vAliq> [#U03]
        self.codigo_municipio_fato_gerador: int = int()  # :: <cMunFG> [#U05]
        self.codigo_municipio: int = int()  # :: <cMun> [#U14]
        self.codigo_pais: int = int()  # :: <cPais> [#U15]
        self.codigo_servico: str = str()  # :: <cServico> [#U13]
        self.indicador_incentivo_fiscal: int = int()  # 1=Sim; 2=Não; :: <indIcentivo> [#U17]
        self.indicador_iss: int = int()  # 1=Exigível, 2=Não incidência; 3=Isenção; 4=Exportação;5=Imunidade; 6=Exigibilidade Suspensa por Decisão Judicial;
        # 7=Exigibilidade Suspensa por Processo Administrativo; :: <indISS> [#U12]
        self.item_lista_servico: str = str()  # :: <cListServ> [#U06]
        self.processo: str = str()  # :: <nProcesso> [#U16]
        self.valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#U02]
        self.valor_deducao: Decimal = Decimal()  # :: <vDeducao> [#U07]
        self.valor_desconto_condicionado: Decimal = Decimal()  # :: <vDescCond> [#U10]
        self.valor_desconto_incondicionado: Decimal = Decimal()  # :: <vDescIncond> [#U09]
        self.valor_outro: Decimal = Decimal()  # :: <vOutro> [#U08]
        self.valor_iss_retido: Decimal = Decimal()  # :: <vISSRet> [#U11]
        self.valor: Decimal = Decimal()  # :: <vISSQN> [#U04]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vAliq':
                self.aliquota = Decimal(valor)
            elif chave == 'cMunFG':
                self.codigo_municipio_fato_gerador = int(valor)
            elif chave == 'cMun':
                self.codigo_municipio = int(valor)
            elif chave == 'cPais':
                self.codigo_pais = int(valor)
            elif chave == 'cServico':
                self.codigo_servico = ler_texto(valor)
            elif chave == 'indIncentivo':
                self.indicador_incentivo_fiscal = int(valor)
            elif chave == 'indISS':
                self.indicador_iss = int(valor)
            elif chave == 'cListServ':
                self.item_lista_servico = ler_texto(valor)
            elif chave == 'nProcesso':
                self.processo = ler_texto(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vDeducao':
                self.valor_deducao = Decimal(valor)
            elif chave == 'vDescCond':
                self.valor_desconto_condicionado = Decimal(valor)
            elif chave == 'vDescIncond':
                self.valor_desconto_incondicionado = Decimal(valor)
            elif chave == 'vOutro':
                self.valor_outro = Decimal(valor)
            elif chave == 'vISSRet':
                self.valor_iss_retido = Decimal(valor)
            elif chave == 'vISSQN':
                self.valor = Decimal(valor)


class NFeReferenciada(BaseObjDFe):  # [#BA03]

    def __init__(self, dado: OrderedDict):
        self.cnpj: int = int()  # CNPJ do Emitente. :: <CNPJ> [#BA06]
        self.emissao: date = None  # Ano e Mês da emissão no formato AAMM :: <AAMM> [#BA05]
        self.modelo: int = int()  # Modelo do documento fiscal :: <mod> [#BA07]
        self.nf: int = int()  # Número do documento fiscal :: <nNF> [#BA09]
        self.serie: int = int()  # Série do documento fiscal :: <serie> [#BA08]
        self.uf: str = str()  # Código da UF do emitente :: <cUF> [#BA04]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'AAMM':
                self.emissao = ler_data(valor, formato_data_ano_mes)
            elif chave == 'mod':
                self.modelo = int(valor)
            elif chave == 'nNF':
                self.nf = int(valor)
            elif chave == 'serie':
                self.serie = int(valor)
            elif chave == 'cUF':
                self.uf = ler_texto(valor)


class NFeReferenciadaProdutoRural(NFeReferenciada):  # [#BA10]

    def __init__(self, dado: OrderedDict):
        self.cpf: int = int()  # CPF do Emitente :: <CPF> [#BA14]
        self.cte_referenciada: int = int()  # Chave de acesso do CT-e referenciada  :: <refCTe> [#BA19]
        self.inscricao_estadual: str = str()  # IE do Emitente :: <IE> [#BA15]
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CPF':
                self.cpf = int(valor)
            elif chave == 'refCTe':
                self.cte_referenciada = int(valor)
            elif chave == 'IE':
                self.inscricao_estadual = ler_texto(valor)


class ObservacaoContribuinte(BaseObjDFe):  # [#Z04]

    def __init__(self, dado: OrderedDict):
        self.campo: str = str()  # :: <xCampo> [#Z05]
        self.texto: str = str()  # :: <xTexto> [#Z06]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'xCampo':
                self.campo = ler_texto(valor)
            elif chave == 'xText':
                self.texto = ler_texto(valor)


class ObservacaoFisco(ObservacaoContribuinte):  # [#Z07]
    def __init__(self, dado: OrderedDict):
        super().__init__(dado)


class Pagamento(BaseObjDFe):  # [#YA01]
    def __init__(self, dado: OrderedDict):
        self.cartao: Cartao = None  # :: <card> [#YA04]
        self.tipo: str = str()  # Forma de pagamento. 01=Dinheiro; 02=Cheque; 03=Cartão de Crédito; 04=Cartão de Débito; 05=Crédito Loja; 10=Vale Alimentação;
        # 11=Vale Refeição; 12=Vale Presente; 13=Vale Combustível; 99=Outros :: <tPag> [#YA02]
        self.valor: Decimal = Decimal()  # Valor do Pagamento :: <vPag> [#YA03]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'card':
                self.cartao = Cartao(valor)
            elif chave == 'tPag':
                self.tipo = ler_texto(valor)
            elif chave == 'vPag':
                self.valor = Decimal(valor)

    def descricao_pagamento(self):
        descricao = 'Outros'
        if self.tipo == '01':
            descricao = 'Dinheiro'
        elif self.tipo == '02':
            descricao = 'Cheque'
        elif self.tipo == '03':
            descricao = 'Cartão de Crédito'
        elif self.tipo == '04':
            descricao = 'Cartão de Débito'
        elif self.tipo == '05':
            descricao = 'Crédito Loja'
        elif self.tipo == '10':
            descricao = 'Vale Alimentação'
        elif self.tipo == '11':
            descricao = 'Vale Refeição'
        elif self.tipo == '12':
            descricao = 'Vale Presente'
        elif self.tipo == '13':
            descricao = 'Vale Combustível'
        return descricao


class PIS(BaseObjDFe):  # [#Q01]
    def __init__(self, dado: OrderedDict):
        self.pis_aliq: PISAliquota = None  # Grupo PIS tributado pela alíquota :: <PISAliq> [#Q02]
        self.pis_nao_tributado: PISNaoTributado = None  # Grupo PIS não tributado :: <PISNT> [#Q04]
        self.pis_outros: PISOutros = None  # Grupo PIS Outras Operações :: <PISOutr> [#Q05]
        self.pis_quantidade: PISQuantidade = None  # Grupo PIS tributado por Qtde :: <PISQtde> [#Q03]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'PISAliq':
                self.pis_aliq = PISAliquota(valor)
            elif chave == 'PISNT':
                self.pis_nao_tributado = PISNaoTributado(valor)
            elif chave == 'PISOutr':
                self.pis_outros = PISOutros(valor)
            elif chave == 'PISQtde':
                self.pis_quantidade = PISQuantidade(valor)


class PISAliquota(BaseObjDFe):  # {#Q02}

    def __init__(self, dado: OrderedDict):
        self.aliquota: Decimal = Decimal()  # <pPIS> [#Q08]
        self.cst: int = int()  # 01=Operação Tributável (base de cálculo = valor da operação alíquota normal (cumulativo/não cumulativo)); 02=Operação
        # Tributável (base de cálculo = valor da operação (alíquota diferenciada)); :: <CST> [#Q06]
        self.valor_base_calculo: Decimal = Decimal()  # <vBC> [#Q07]
        self.valor: Decimal = Decimal()  # <vPIS> [#Q09]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pPIS':
                self.aliquota = Decimal(valor)
            elif chave == 'CST':
                self.cst = int(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vPIS':
                self.valor = Decimal(valor)


class PISNaoTributado(BaseObjDFe):  # {#Q04}
    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # 04=Operação Tributável (tributação monofásica (alíquota zero)); 05=Operação Tributável (Substituição Tributária); 06=Operação
        # Tributável (alíquota zero); 07=Operação Isenta da Contribuição;08=Operação Sem Incidência da Contribuição;09=Operação com Suspensão da
        # Contribuição;  :: <CST> [#Q06]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)


class PISOutros(PISAliquota):  # {#Q05}

    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # 49=Outras Operações de Saída;50=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Tributada no Mercado
        # Interno; 51=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Não Tributada no Mercado Interno;52=Operação com Direito a Crédito –
        # Vinculada Exclusivamente a Receita de Exportação;53=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e Não-Tributadas no Mercado
        # Interno; 54=Operação com Direito a Crédito - Vinculada a Receitas Tributadas no Mercado Interno e de Exportação;55=Operação com Direito a Crédito -
        # Vinculada a Receitas NãoTributadas no Mercado Interno e de Exportação;56=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e
        # Não-Tributadas no Mercado Interno, e de Exportação;60=Crédito Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Tributada no
        # Mercado Interno;61=Crédito Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Não-Tributada no Mercado Interno; 62=Crédito Presumido
        # - Operação de  Aquisição Vinculada Exclusivamente a Receita de Exportação;63=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Tributadas
        # e Não-Tributadas no Mercado Interno;64=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Tributadas no Mercado Interno e de Exportação;
        # 65=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Não-Tributadas no Mercado Interno e de Exportação;66=Crédito Presumido - Operação de
        # Aquisição Vinculada a Receitas Tributadas e Não-Tributadas no Mercado Interno, e de Exportação;67=Crédito Presumido - Outras Operações;70=Operação de
        # Aquisição sem Direito a Crédito; 71=Operação de Aquisição com Isenção;72=Operação de Aquisição com Suspensão;73=Operação de Aquisição a Alíquota Zero;
        # 74=Operação de Aquisição; sem Incidência da Contribuição;75=Operação de Aquisição por Substituição Tributária;98=Outras Operações de Entrada;99=Outras
        # Operações;
        self.quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#Q10]
        self.valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#Q11]
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)
            elif chave == 'qBCProd':
                self.quantidade_base_calculo = Decimal(valor)
            elif chave == 'vAliqProd':
                self.valor_aliquota = Decimal(valor)


class PISQuantidade(BaseObjDFe):  # {#Q03}

    def __init__(self, dado: OrderedDict):
        self.cst: int = int()  # 03=Operação Tributável (base de cálculo = quantidade vendida x alíquota por unidade de produto); :: <CST> [#Q06]
        self.quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#Q10]
        self.valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#Q11]
        self.valor: Decimal = Decimal()  # <vPIS> [#Q09]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)
            elif chave == 'qBCProd':
                self.quantidade_base_calculo = Decimal(valor)
            elif chave == 'vAliqProd':
                self.valor_aliquota = Decimal(valor)
            elif chave == 'vPIS':
                self.valor = Decimal(valor)


class PISST(PISOutros):  # [#R01]

    def __init__(self, dado: OrderedDict):
        self.cst: None = None  # Nessa classe não existe CST
        super().__init__(dado)


class Produto(BaseObjDFe):  # [#I01]

    def __init__(self, dado: OrderedDict):
        self.codigo: str = str()  # Código do produto ou serviço. :: <cProd> [#I02]
        self.cfop: int = int()  # Código Fiscal de Operações e Prestações. :: <CFOP> [#I08]
        self.desconto: Decimal = Decimal()  # :: <vDesc> [#I17]
        self.descricao: str = str()  # :: <xProd> [#I04]
        self.ex_tipi: int = int()  # Preencher de acordo com o código EX da TIPI. Em caso de serviço, não incluir a TAG. :: <EXTIPI> [#I06]
        self.gtin: str = str()  # Preencher com o código GTIN-8, GTIN-12, GTIN-13 ou GTIN-14 (antigos códigos EAN, UPC e DUN-14), não informar o conteúdo da
        # TAG em caso de o produto não possuir este código. :: <cEAN> [#I03]
        self.gtin_tribut: str = str()  # Preencher com o código GTIN-8, GTIN-12, GTIN-13 ou GTIN-14 (antigos códigos EAN, UPC e DUN-14) da unidade tributável
        # do produto, não informar o conteúdo da TAG em caso de o produto não possuir este código. :: <cEANTrib> [#I12]
        self.indicador_total: int = int()  # Indica se valor do Item (vProd) entra no valor total da NF-e (vProd): 0=Valor do item (vProd) não compõe o valor
        # total da NF-e 1=Valor do item (vProd) compõe o valor total da NF-e (vProd)(v2.0) :: <indTot> [#I17b]
        self.ncm: int = int()  # Código NCM : Em caso de item de serviço ou item que não tenham produto (ex. transferência de crédito, crédito do ativo
        # imobilizado, etc.), informar o valor 00 (dois zeros). (NT2014/004). :: <NCM> [#I05]
        self.nve: str = str()  # Codificação NVE - Nomenclatura de Valor Aduaneiro e Estatística. :: <NVE> [#I05a]
        self.quantidade: Decimal = Decimal()  # Quantidade Comercial. :: <qCom> [#I10]
        self.quantidade_tributavel: Decimal = Decimal()  # Quantidade Tributável. :: <qTrib> [#I14]
        self.unidade: str = str()  # Unidade Comercial. :: <uCom> [#I09]
        self.unidade_tributavel: str = str()  # Unidade Tributável. :: <uTrib> [#I13]
        self.valor_seguro: Decimal = Decimal()  # :: <vSeg> [#I16]
        self.valor_frete: Decimal = Decimal()  # :: <vFrete> [#I15]
        self.valor_outro: Decimal = Decimal()  # :: <vOutro> [#I17a]
        self.valor_total: Decimal = Decimal()  # :: <vProd> [#I11]
        self.valor_unitario: Decimal = Decimal()  # :: <vUnCom> [#I10a]
        self.valor_unitario_tributavel: Decimal = Decimal()  # :: <vUnTrib> [#I14a]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'cProd':
                self.codigo = ler_texto(valor)
            elif chave == 'CFOP':
                self.cfop = int(valor)
            elif chave == 'vDesc':
                self.desconto = Decimal(valor)
            elif chave == 'xProd':
                self.descricao = ler_texto(valor)
            elif chave == 'EXTIPI':
                self.ex_tipi = int(valor)
            elif chave == 'vFrete':
                self.valor_frete = Decimal(valor)
            elif chave == 'cEAN':
                self.gtin = ler_texto(valor)
            elif chave == 'cEANTrib':
                self.gtin_tribut = ler_texto(valor)
            elif chave == 'indTot':
                self.indicador_total = int(valor)
            elif chave == 'NCM':
                self.ncm = int(valor)
            elif chave == 'NVE':
                self.nve = ler_texto(valor)
            elif chave == 'vOutro':
                self.valor_outro = Decimal(valor)
            elif chave == 'qCom':
                self.quantidade = Decimal(valor)
            elif chave == 'qTrib':
                self.quantidade_tributavel = Decimal(valor)
            elif chave == 'vSeg':
                self.valor_seguro = Decimal(valor)
            elif chave == 'uCom':
                self.unidade = ler_texto(valor)
            elif chave == 'uTrib':
                self.unidade_tributavel = ler_texto(valor)
            elif chave == 'vProd':
                self.valor_total = Decimal(valor)
            elif chave == 'vUnCom':
                self.valor_unitario = Decimal(valor)
            elif chave == 'vUnTrib':
                self.valor_unitario_tributavel = Decimal(valor)


class RetencaoTransporte(BaseObjDFe):  # [#X11]

    def __init__(self, dado: OrderedDict):
        self.aliquota: Decimal = Decimal()  # :: <pICMSRet> [#X14]
        self.cfop: int = int()  # :: <CFOP> [#X16]
        self.codigo_municipio: int = int()  # :: <cMunFG> [#X127
        self.valor_base_calculo: Decimal = Decimal()  # :: <vBCRet> [#X13]
        self.valor_icms: Decimal = Decimal()  # :: <vICMSRet> [#X15]
        self.valor_servico: Decimal = Decimal()  # :: <vServ> [#X12]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pICMSRet':
                self.aliquota = Decimal(valor)
            elif chave == 'CFOP':
                self.cfop = int(valor)
            elif chave == 'cMunFG':
                self.codigo_municipio = int(valor)
            elif chave == 'vBCRet':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vICMSRet':
                self.valor_icms = Decimal(valor)
            elif chave == 'vServ':
                self.valor_servico = Decimal(valor)


class Total(BaseObjDFe):  # [#W01]

    def __init__(self, dado: OrderedDict):
        self.icms: TotalICMS = None  # :: <ICMSTot> [#W02]
        self.issqn: TotalISSQN = None  # :: <ISSQNtot> [#W17]
        self.retencao: TotalRetencao = None  # :: <retTrib> [#W23]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'ICMSTot':
                self.icms = TotalICMS(valor)
            elif chave == 'ISSQNTot':
                self.icms = TotalISSQN(valor)
            elif chave == 'retTrib':
                self.icms = TotalRetencao(valor)


class TotalICMS(BaseObjDFe):  # [#W02]

    def __init__(self, dado: OrderedDict):
        self.valor: Decimal = Decimal()  # :: <vICMS> [#W04]
        self.valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#W03]
        self.valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#W05]
        self.valor_cofins: Decimal = Decimal()  # :: <vCOFINS> [#W14]
        self.valor_desconto: Decimal = Decimal()  # :: <vDesc> [#W10]
        self.valor_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#W04a]
        self.valor_frete: Decimal = Decimal()  # :: <vFrete> [#W08]
        self.valor_imposto_importado: Decimal = Decimal()  # :: <vII> [#W11]
        self.valor_ipi: Decimal = Decimal()  # :: <vIPI> [#W12]
        self.valor_nf: Decimal = Decimal()  # :: <vNF> [#W16]
        self.valor_outros: Decimal = Decimal()  # :: <vOutro> [#W15]
        self.valor_produtos: Decimal = Decimal()  # :: <vProd> [#W07]
        self.valor_pis: Decimal = Decimal()  # :: <vPIS> [#W13]
        self.valor_seguro: Decimal = Decimal()  # :: <vSeg> [#W09]
        self.valor_st: Decimal = Decimal()  # :: <vST> [#W06]
        self.valor_total_tributos: Decimal = Decimal()  # :: <vTotTrib> [#W16a]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vICMS':
                self.valor = Decimal(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vBCST':
                self.valor_base_calculo_st = Decimal()
            elif chave == 'vCOFINS':
                self.valor_cofins = Decimal(valor)
            elif chave == 'vDesc':
                self.valor_desconto = Decimal(valor)
            elif chave == 'vICMSDeson':
                self.valor_desonerado = Decimal(valor)
            elif chave == 'vFrete':
                self.valor_frete: Decimal = Decimal(valor)
            elif chave == 'vII':
                self.valor_imposto_importado = Decimal(valor)
            elif chave == 'vIPI':
                self.valor_ipi = Decimal(valor)
            elif chave == 'vNF':
                self.valor_nf = Decimal(valor)
            elif chave == 'vOutro':
                self.valor_outros = Decimal(valor)
            elif chave == 'vProd':
                self.valor_produtos = Decimal(valor)
            elif chave == 'vPIS':
                self.valor_pis = Decimal(valor)
            elif chave == 'vSeg':
                self.valor_seguro = Decimal(valor)
            elif chave == 'vST':
                self.valor_st = Decimal(valor)
            elif chave == 'vTotTrib':
                self.valor_total_tributos = Decimal(valor)


class TotalISSQN(BaseObjDFe):  # :: <ISSQNtot> [#W17]

    def __init__(self, dado: OrderedDict):
        self.codigo_regime_tributacao: int = int()  # 1=Microempresa Municipal; 2=Estimativa;3=Sociedade de Profissionais; 4=Cooperativa;5=Microempresário
        # Individual (MEI);6=Microempresário e Empresa de Pequeno Porte (ME/EPP) :: <cRegTrib> [#W22g]
        self.data_competencia: date = None  # :: <dCompet> [#W22a]
        self.valor: Decimal = Decimal()  # :: <vISS> [#W20]
        self.valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#W19]
        self.valor_cofins: Decimal = Decimal()  # :: <vCOFINS> [#W22]
        self.valor_deducao: Decimal = Decimal()  # :: <vDeducao> [#W22b]
        self.valor_desconto_condicionado: Decimal = Decimal()  # :: <vDescCond> [#W22e]
        self.valor_desconto_incondicionado: Decimal = Decimal()  # :: <vDescIncond> [#W22d]
        self.valor_outro: Decimal = Decimal()  # :: <vOutro> [#W22c]
        self.valor_iss_retido: Decimal = Decimal()  # :: <vISSRet> [#W22f]
        self.valor_pis: Decimal = Decimal()  # :: <vPIS> [#W21]
        self.valor_servico: Decimal = Decimal()  # :: <vServ> [#W18]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'cRegTrib':
                self.codigo_regime_tributacao = int(valor)
            elif chave == 'dCompet':
                self.data_competencia = ler_data(valor)
            elif chave == 'vISS':
                self.valor = Decimal(valor)
            elif chave == 'vBC':
                self.valor_base_calculo = Decimal(valor)
            elif chave == 'vCOFINS':
                self.valor_cofins = Decimal(valor)
            elif chave == 'vDeducao':
                self.valor_deducao = Decimal(valor)
            elif chave == 'vDescCond':
                self.valor_desconto_condicionado = Decimal(valor)
            elif chave == 'vDescIncond':
                self.valor_desconto_incondicionado = Decimal(valor)
            elif chave == 'vOutro':
                self.valor_outro = Decimal(valor)
            elif chave == 'vISSRet':
                self.valor_iss_retido = Decimal(valor)
            elif chave == 'vPIS':
                self.valor_pis = Decimal(valor)
            elif chave == 'vServ':
                self.valor_servico = Decimal(valor)


class TotalRetencao(BaseObjDFe):  # :: [#W23]

    def __init__(self, dado: OrderedDict):
        self.retencao_cofins: Decimal = Decimal()  # :: <vRetCOFINS> [#W25]
        self.retencao_csll: Decimal = Decimal()  # :: <vRetCSLL> [#W26]
        self.retencao_irrf: Decimal = Decimal()  # :: <vRetIRRF> [#W28]
        self.retencao_pis: Decimal = Decimal()  # :: <vRetPIS> [#W24]
        self.retencao_previdencia: Decimal = Decimal()  # :: <vRetPrev> [#W30]
        self.valor_base_calculo_irrf: Decimal = Decimal()  # :: <vRetBCIRRF> [#W27]
        self.valor_base_calculo_previdencia: Decimal = Decimal()  # :: <vRetBCPrev> [#W29]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vRetCOFINS':
                self.retencao_cofins = Decimal(valor)
            elif chave == 'vRetCSLL':
                self.retencao_csll = Decimal(valor)
            elif chave == 'vRetIRRF':
                self.retencao_irrf = Decimal(valor)
            elif chave == 'vRetPIS':
                self.retencao_pis = Decimal(valor)
            elif chave == 'vRetRetPrev':
                self.retencao_previdencia = Decimal(valor)
            elif chave == 'vRetBCIRRF':
                self.valor_base_calculo_irrf = Decimal(valor)
            elif chave == 'vRetBCPrev':
                self.valor_base_calculo_previdencia = Decimal(valor)


class Transportador(BaseObjDFe):  # [#X03]

    def __init__(self, dado: OrderedDict):
        self.cnpj: int = int()  # :: <CNPJ> [#X04]
        self.cpf: int = int()  # :: <CPF> [#X05]
        self.endereco: str = str()  # :: <xEnder> [#X08]
        self.inscricao_estadual: str = str()  # :: <IE> [#X07]
        self.municipio: str = str()  # :: <xMun> [#X09]
        self.razao_social: str = str()  # :: <xNome> [#X06]
        self.retencao: RetencaoTransporte = None  # :: <retTransp> [#X11]
        self.uf: str = str()  # :: <UF> [#X10]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'cpf':
                self.cpf = int(valor)
            elif chave == 'xEnder':
                self.endereco = ler_texto(valor)
            elif chave == 'IE':
                self.inscricao_estadual = ler_texto(valor)
            elif chave == 'xMun':
                self.municipio = ler_texto(valor)
            elif chave == 'xNome':
                self.razao_social = ler_texto(valor)
            elif chave == 'retTransp':
                self.retencao = RetencaoTransporte(valor)
            elif chave == 'UF':
                self.uf = ler_texto(valor)


class Transporte(BaseObjDFe):  # [#X01]

    def __init__(self, dado: OrderedDict):
        self.balsa: str = str()  # :: <balsa> [#X25b]
        self.modalidade_frete: int = int()  # 0=Por conta do emitente;1=Por conta do destinatário/remetente;2=Por conta de terceiros;9=Sem
        # frete.  :: <modFrete> [#X02]
        self.reboques: ListaTransporteReboques = []  # Grupo Reboque :: <reboque>
        self.transportador: Transportador = None  # Grupo Transportador  :: <transporta>[#X03]
        self.vagao: str = str()  # :: <vagao> [#X25a]
        self.veiculo: TransporteVeiculo = None  # :: <veicTransp> [#X18]
        self.volumes: ListaTransporteVolumes = []  # :: <vol> [#X26]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'balsa':
                self.balsa = ler_texto(valor)
            elif chave == 'modFrete':
                self.modalidade_frete = int(valor)
            elif chave == 'reboque':
                if isinstance(valor, list):
                    for reboque in valor:
                        self.reboques.append(TransporteReboque(reboque))
                else:
                    self.reboques.append(TransporteReboque(valor))
            elif chave == 'transporta':
                self.transportador = Transportador(valor)
            elif chave == 'vagao':
                self.vagao = ler_texto(valor)
            elif chave == 'veicTransp':
                self.veiculo = TransporteVeiculo(valor)
            elif chave == 'vol':
                if isinstance(valor, list):
                    for volume in valor:
                        self.volumes.append(TransporteVolume(volume))
                else:
                    self.volumes.append(TransporteVolume(valor))


class TransporteReboque(BaseObjDFe):  # [#X22]

    def __init__(self, dado: OrderedDict):
        self.placa: str = str()  # :: <placa> [#X23]
        self.rntc: str = str()  # Registro Nacional de Transportador de Carga (ANTT) :: <RNTC> [#X25]
        self.uf: str = str()  # :: <UF> [#X24]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'placa':
                self.placa = ler_texto(valor)
            elif chave == 'RNTC':
                self.rntc = ler_texto(valor)
            elif chave == 'UF':
                self.uf = ler_texto(valor)


class TransporteVeiculo(TransporteReboque):  # [#X18]
    def __init__(self, dado: OrderedDict):
        super().__init__(dado)


class TransporteVolume(BaseObjDFe):  # :: <vol> [#X26]

    def __init__(self, dado: OrderedDict):
        self.especie: str = str()  # :: <esp> [#X28]
        self.lacres: ListaLacres = []  # :: <lacres> [#X33]
        self.marca: str = str()  # :: <marca> [#X29]
        self.numercao: str = str()  # :: <nVol> [#X30]
        self.peso_bruto: Decimal = Decimal()  # :: <pesoB> [#X32]
        self.peso_liquido: Decimal = Decimal()  # :: <pesoL> [#X31]
        self.quantidade: int = int()  # :: <qVol> [#X27]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'esp':
                self.especie = ler_texto(valor)
            elif chave == 'lacres':
                if isinstance(valor, list):
                    for lacre in valor:
                        self.lacres.append(VolumeLacre(lacre))
                else:
                    self.lacres.append(VolumeLacre(valor))
            elif chave == 'marca':
                self.marca = ler_texto(valor)
            elif chave == 'nVol':
                self.numercao = ler_texto(valor)
            elif chave == 'pesoB':
                self.peso_bruto = Decimal(valor)
            elif chave == 'pesoL':
                self.peso_liquido = Decimal(valor)
            elif chave == 'qVol':
                self.quantidade = int(valor)


class TributoDevolvido(BaseObjDFe):  # [#UA01]

    def __init__(self, dado: OrderedDict):
        self.percentual_devolucao: Decimal = Decimal()  # O valor máximo deste percentual é 100%, no caso de devolução total da mercadoria. :: <pDevol> [#UA02]
        self.ipi: TributoDevolvidoIPI = None  # :: <IPI> [#UA03]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pDevol':
                self.percentual_devolucao = Decimal(valor)
            elif chave == 'IPI':
                self.ipi = TributoDevolvidoIPI(valor)


class TributoDevolvidoIPI(BaseObjDFe):  # [#UA03]

    def __init__(self, dado: OrderedDict):
        self.valor: Decimal = Decimal()  # :: <vIPIDevol> [#UA04]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vIPIDevol':
                self.valor = Decimal(valor)


class VolumeLacre(BaseObjDFe):  # [#X33]

    def __init__(self, dado: OrderedDict):
        self.numero: str = str()  # :: <nLacre> [#X4]
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'nLacre':
                self.numero = ler_texto(valor)


# Tipos
DetalhesProduto = Dict[int, Detalhamento]
ListaDocumentoReferenciado = List[DocumentoReferenciado]
ListaDuplicatas = List[Duplicata]
ListaLacres = List[VolumeLacre]
ListaObservacoesContribuinte = List[ObservacaoContribuinte]
ListaObservacoesFisco = List[ObservacaoFisco]
ListaTransporteReboques = List[TransporteReboque]
ListaTransporteVolumes = List[TransporteVolume]

# formato
formato_data_padrao = '%Y-%m-%d'
formato_data_ano_mes = '%Y%m'


# funções
def ler_data(texto: str, formato: str = formato_data_padrao) -> date:
    return datetime.strptime(texto, formato).date()


def ler_data_hora(texto: str) -> datetime:
    try:
        return datetime.strptime(texto[:22] + texto[23:], '%Y-%m-%dT%H:%M:%S%z')
    except:
        return datetime.strptime(texto[:22] + texto[23:], '%Y-%m-%dT%H:%M:%S')


def ler_texto(texto: str) -> str:
    if texto is None:
        return str()
    return texto
