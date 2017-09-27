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


class Cobranca(BaseObjDFe):  # [#Y01]
    duplicatas: ListaDuplicatas = []  # :: <dup> [#Y07]
    fatura: Fatura = None  # :: <fat> [#Y02]

    def __init__(self, dado: OrderedDict):
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
    cofins_aliq: COFINSAliquota = None  # Grupo COFINS tributado pela alíquota  :: <COFINSAliq> [#S02]
    cofins_nao_tributado: COFINSNaoTributado = None  # Grupo COFINS não tributado :: <COFINSNT> [#S04]
    cofins_outros: COFINSOutros = None  # Grupo COFINS Outras Operações :: <COFINSOutr> [#S05]
    cofins_quantidade: COFINSQuantidade = None  # Grupo de COFINS tributado por Qtde  :: <COFINSQtde> [#S03]

    def __init__(self, dado: OrderedDict):
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
    aliquota: Decimal = Decimal()  # <pCOFINS> [#S08]
    cst: int = int()  # 01=Operação Tributável (base de cálculo = valor da operação alíquota normal (cumulativo/não cumulativo)); 02=Operação Tributável
    # (base de cálculo = valor da operação (alíquota diferenciada)); :: <CST> [#S06]
    valor: Decimal = Decimal()  # <vCOFINS> [#S11]
    valor_base_calculo: Decimal = Decimal()  # <vBC> [#S07]

    def __init__(self, dado: OrderedDict):
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
    cst: int = int()  # 04=Operação Tributável (tributação monofásica (alíquota zero)); 05=Operação Tributável (Substituição Tributária); 06=Operação Tributável

    # (alíquota zero); 07=Operação Isenta da Contribuição;08=Operação Sem Incidência da Contribuição;09=Operação com Suspensão da Contribuição;  :: <CST> [#S06]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)


class COFINSOutros(COFINSAliquota):  # {#S05}
    cst: int = int()  # 49=Outras Operações de Saída;50=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Tributada no Mercado Interno;
    # 51=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Não Tributada no Mercado Interno;52=Operação com Direito a Crédito – Vinculada
    # Exclusivamente a Receita de Exportação;53=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e Não-Tributadas no Mercado Interno;
    # 54=Operação com Direito a Crédito - Vinculada a Receitas Tributadas no Mercado Interno e de Exportação;55=Operação com Direito a Crédito - Vinculada a
    # Receitas NãoTributadas no Mercado Interno e de Exportação;56=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e Não-Tributadas no Mercado
    # Interno, e de Exportação;60=Crédito Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Tributada no Mercado Interno;61=Crédito
    # Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Não-Tributada no Mercado Interno; 62=Crédito Presumido - Operação de  Aquisição
    # Vinculada Exclusivamente a Receita de Exportação;63=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Tributadas e Não-Tributadas no Mercado
    # Interno;64=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Tributadas no Mercado Interno e de Exportação;65=Crédito Presumido - Operação de
    # Aquisição Vinculada a Receitas Não-Tributadas no Mercado Interno e de Exportação;66=Crédito Presumido - Operação de Aquisição Vinculada a Receitas
    # Tributadas e Não-Tributadas no Mercado Interno, e de Exportação;67=Crédito Presumido - Outras Operações;70=Operação de Aquisição sem Direito a Crédito;
    # 71=Operação de Aquisição com Isenção;72=Operação de Aquisição com Suspensão;73=Operação de Aquisição a Alíquota Zero;74=Operação de Aquisição;
    # sem Incidência da Contribuição;75=Operação de Aquisição por Substituição Tributária;98=Outras Operações de Entrada;99=Outras Operações;
    quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#Q10]
    valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#Q11]

    def __init__(self, dado: OrderedDict):
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
    cst: int = int()  # 03=Operação Tributável (base de cálculo = quantidade vendida x alíquota por unidade de produto); :: <CST> [#S06]
    quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#S09]
    valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#S10]
    valor: Decimal = Decimal()  # <vCOFINS> [#S11]

    def __init__(self, dado: OrderedDict):
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
    cnpj: int = int()  # :: <CNPJ> [#E02]
    cpf: int = int()  # :: <CPF> [#E03]
    email: str = str()  # :: <email> [#E19]
    id_estrangeiro: str = str()  # Identificação do destinatário no caso de comprador estrangeiro :: <idEstrangeiro> [#E03a]
    inscricao_municipal_tomador_servico: str = str()  # Campo opcional, pode ser informado na NF-e conjugada, com itens de produtos sujeitos ao ICMS e itens de
    # serviços sujeitos ao ISSQN. :: <IM> [#E20]
    indicador_inscricao_estadual: int = int()  # Indicador da IE do Destinatário: 1=Contribuinte ICMS (informar a IE do destinatário); 2=Contribuinte isento de
    # Inscrição no cadastro de Contribuintes do ICMS; 9=Não Contribuinte, que pode ou não possuir Inscrição Estadual no Cadastro de Contribuintes do ICMS.
    # Nota 1: No caso de NFC-e informar indIEDest=9 e não informar a tag IE do destinatário; Nota 2: No caso de operação com o Exterior informar indIEDest=9 e
    # não informar a tag IE do destinatário; Nota 3: No caso de Contribuinte Isento de Inscrição (indIEDest=2), não informar a tag IE do
    # destinatário. :: <indIEDest> [#E16a]
    inscricao_estadual: str = str()  # :: <IE> [#E17]
    inscricao_suframa: str = str()  # :: <ISUF> [#E18]
    endereco: Endereco = None  # :: <enderDest> [#E05]
    razao_social: str = str()  # Razão Sócial ou Nome do destinatário :: <xNome> [#E04]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'CPF':
                self.cpf = int(valor)
            elif chave == 'email':
                self.email = valor
            elif chave == 'idEstrangeiro':
                self.id_estrangeiro = valor
            elif chave == 'IM':
                self.inscricao_municipal_tomador_servico = valor
            elif chave == 'indIEDest':
                self.indicador_inscricao_estadual = int(valor)
            elif chave == 'IE':
                self.inscricao_estadual = valor
            elif chave == 'ISUF':
                self.inscricao_suframa = valor
            elif chave == 'enderDest':
                self.endereco = Endereco(valor)
            elif chave == 'xNome':
                self.razao_social = valor


class Detalhamento(BaseObjDFe):  # [#H01]
    imposto: Imposto = None  # Tributos incidentes no Produto ou Serviço. :: <impost> [#M01]
    informacoes_adicionais: str = str()  # Informações Adicionais :: <infAdProd> [#V01]
    numero_item: int = int()  # Número do item :: @nItem [#H02]
    produto: Produto = None  # Detalhamento de Produtos e Serviços :: <prod> [#I01]
    tributos_devolvidos: TributoDevolvido = None  # Informação do Imposto devolvido :: <impostoDevol> [#UA01]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'impost':
                self.imposto = Imposto(valor)
            elif chave == 'infAdProd':
                self.informacoes_adicionais = valor
            elif chave == '@nItem':
                self.numero_item = int(valor)
            elif chave == 'prod':
                self.produto = Produto(valor)
            elif chave == 'importDevol':
                self.tributos_devolvidos = TributoDevolvido(valor)


class DocumentoReferenciado(BaseObjDFe):  # [#BA01]
    chave_nfe_ref: int = int()  # Chave de acesso da NF-e referenciada :: <refNFe> [#BA02]
    informacao_nfe_ref: NFeReferenciada = None  # Informação da NF modelo 1/1A referenciada :: <refNF> [#BA03]
    informacao_nfe_pr_ref: NFeReferenciadaProdutoRural = None  # Informações da NF de produtor rural referenciada :: <refNFP> [#BA10]
    informacao_ecf_ref: ECFReferenciado = None  # Informações do Cupom Fiscal referenciado :: <refECF> [#BA20]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'refNFe':
                self.chave_nfe_ref = int(valor)
            elif chave == 'refNF':
                self.informacao_nfe_ref = NFeReferenciada(valor)
            elif chave == 'refNFP':
                self.informacao_nfe_pr_ref = NFeReferenciadaProdutoRural(valor)
            elif chave == 'refECF':
                self.informacao_ecf_ref = ECFReferenciado(valor)


class Duplicata(BaseObjDFe):  # [#Y07]
    numero: str = str()  # :: <nDup> [#Y08]
    valor: Decimal = Decimal()  # :: <vDup> [#Y10]
    vencimento: date = None  # :: <dVenc> [#Y09]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'nDup':
                self.numero = valor
            elif chave == 'vDup':
                self.valor = Decimal(valor)
            elif chave == 'dVenc':
                self.vencimento = ler_data(valor)


class ECFReferenciado(BaseObjDFe):  # [#BA20]
    modelo: int = int()  # Modelo do cupom fiscal :: <mod> [#BA21]
    numero_coo: int = int()  # Número do Contador de Ordem de Operação - COO :: <nCOO> [#BA23]
    numero_ecf: int = int()  # Número de ordem sequencial do ECF :: <nECF> [#BA22]

    def __init__(self, dado: OrderedDict):
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
    cnpj: int = int()  # :: <CNPJ> [#C02]
    cpf: int = int()  # :: <CPF> [#C02a]
    endereco = None  # :: <enderEmit> [#C05]
    fantasia: str = str()  # Nome Fantasia do emitente :: <xFant> [#C04]
    inscricao_estadual: str = str()  # :: <IE> [#C17]
    inscricao_estadual_st: str = str()  # :: <IEST> [#C18]
    razao_social: str = str()  # Razão Sócial ou Nome do emitente :: <xNome> [#C03]

    def __init__(self, dado: OrderedDict):
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
                self.fantasia = valor
            elif chave == 'IE':
                self.inscricao_estadual = valor
            elif chave == 'IEST':
                self.inscricao_estadual_st = valor
            elif chave == 'xNome':
                self.razao_social = valor


class Endereco(BaseObjDFe):  # [#C05]
    bairro: str = str()  # :: <xBairro> [#C09] [#E09]
    cep: int = int()  # :: <CEP> [#C13] [#E13]
    codigo_municipio: int = int()  # :: <cMun> [#C10] [#E10]
    codigo_pais: int = int()  # :: <cPais> [#C14] [#E14]
    complemento: str = str()  # :: <xCpl> [#C08] [#E08]
    logradouro: str = str()  # :: <xLgr> [#C06] [#E06]
    municipio: str = str()  # :: <xMun> [#C11] [#E11]
    numero: str = str()  # :: <nro> [#C07] [#E07]
    pais: str = str()  # :: <xPais> [#C15] [#E15]
    telefone: int = int()  # :: <fone> [#C16] [#E16]
    uf: str = str()  # :: <UF> [#C12] [#E12]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'xBairro':
                self.bairro = valor
            elif chave == 'CEP':
                self.cep = int(valor)
            elif chave == 'cMun':
                self.codigo_municipio = int(valor)
            elif chave == 'cPais':
                self.codigo_pais = int(valor)
            elif chave == 'xCpl':
                self.complemento = valor
            elif chave == 'xLgr':
                self.logradouro = valor
            elif chave == 'xMun':
                self.municipio = valor
            elif chave == 'nro':
                self.numero = valor
            elif chave == 'xPais':
                self.pais = valor
            elif chave == 'fone':
                self.telefone = int(valor)
            elif chave == 'UF':
                self.uf = valor


class EntregaRetirada(BaseObjDFe):  # [#F01]
    bairro: str = str()  # :: <xBairro> [#F06]
    cnpj: int = int()  # CNPJ do Emitente :: <CNPJ> [#F02]
    cpf: int = int()  # CPF do Emitente :: <CPF> [#F02a]
    codigo_municipio: int = int()  # :: <cMun> [#F07]
    complemento: str = str()  # :: <xCpl> [#F05]
    logradouro: str = str()  # :: <xLgr> [#F03]
    municipio: str = str()  # :: <xMun> [#F08]
    numero: str = str()  # :: <nro> [#F04]
    uf: str = str()  # :: <UF> [#F09]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'xBairro':
                self.bairro = valor
            elif chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'CPF':
                self.cpf = int(valor)
            elif chave == 'cMun':
                self.codigo_municipio = int(valor)
            elif chave == 'xCpl':
                self.complemento = valor
            elif chave == 'xLgr':
                self.logradouro = valor
            elif chave == 'xMun':
                self.municipio = valor
            elif chave == 'nro':
                self.numero = valor
            elif chave == 'UF':
                self.uf = valor


class Fatura(BaseObjDFe):  # [#Y02]
    numero: str = str()  # :: <nFat> [#Y03]
    valor_desconto: Decimal = Decimal()  # :: <vDesc> [#Y05]
    valor_liquido: Decimal = Decimal()  # :: <vLiq> [#Y06]
    valor_original: Decimal = Decimal()  # :: <vOrig> [#Y04]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'nFat':
                self.numero = valor
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
    icms = None  # Pode ser qualquer um dos tipos acima
    icms_partilha: ICMSPartilha = None  # Operação interestadual para consumidor final com partilha do ICMS devido na operação entre a UF de origem
    # e a do destinatário, ou a UF definida na legislação. :: <ICMSPart> [#N10a]
    icms_st: ICMSST = None  # Grupo de informação do ICMS ST devido para a UF de destino, nas operações interestaduais de produtos que tiveram retenção

    # antecipada de ICMS por ST na UF do remetente. Repasse via Substituto Tributário. . :: <ICMSST> [#N10b]

    def __init__(self, dado: OrderedDict):
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
    aliquota: Decimal = Decimal()  # :: <pICMS> [#N16]
    cst: int = int()  # :: <CST> [#N12]
    modalidade_base_calculo: int = int()  # 0=Margem Valor Agregado (%); 1=Pauta (Valor);  2=Preço Tabelado Máx. (valor); 3=Valor da operação. :: <CST> [#N13]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#N15]
    valor_icms: Decimal = Decimal()  # :: <vICMS> [#N17]

    def __init__(self, dado: OrderedDict):
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
    aliquota_st: Decimal = Decimal()  # :: <pICMSST> [#N22]
    cst: int = 10  # :: <CST> [#N12]
    modalidade_base_calculo_st: int = int()  # 0=Preço tabelado ou máximo sugerido; 1=Lista Negativa (valor); 2=Lista Positiva (valor); 3=Lista Neutra (valor);
    # 4=Margem Valor Agregado (%); 5=Pauta (valor); :: <modBCST> [#N18]
    mva_st: Decimal = Decimal()  # Percentual da margem de valor Adicionado do ICMS ST :: <pMVAST> [#N19]
    reducao_base_calculo_st: Decimal = Decimal()  # Percentual da Redução de BC do ICMS ST :: <pRedBCST> [#N20]
    valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#N21]
    valor_icms_st: Decimal = Decimal()  # :: <vICMSST> [#N23]

    def __init__(self, dado: OrderedDict):
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
    cst: int = 20  # :: <CST> [#N12]
    motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 3=Uso na agropecuária; 9=Outros; 12=Órgão de fomento e desenvolvimento
    # agropecuário. :: <motDesICMS> [#N28]
    reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'motDesICMS':
                self.motivo_icms_desonerado = valor
            elif chave == 'pRedBC':
                self.reducao_base_calculo = Decimal(valor)
            elif chave == 'vICMSDeson':
                self.valor_icms_desonerado = Decimal(valor)


class ICMS30(BaseObjDFe):  # [#N05]
    aliquota_st: Decimal = Decimal()  # :: <pICMSST> [#N22]
    cst: int = 30  # :: <CST> [#N12]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
    modalidade_base_calculo_st: int = int()  # 0=Preço tabelado ou máximo sugerido; 1=Lista Negativa (valor); 2=Lista Positiva (valor); 3=Lista Neutra (valor);
    # 4=Margem Valor Agregado (%); 5=Pauta (valor); :: <modBCST> [#N18]
    motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 6=Utilitários e Motocicletas da Amazônia Ocidental e Áreas de Livre Comércio
    # (Resolução 714/88 e 790/94 – CONTRAN e suas alterações); 7=SUFRAMA; 9=Outros;. :: <motDesICMS> [#N28]
    mva_st: Decimal = Decimal()  # Percentual da margem de valor Adicionado do ICMS ST :: <pMVAST> [#N19]
    reducao_base_calculo_st: Decimal = Decimal()  # Percentual da Redução de BC do ICMS ST :: <pRedBCST> [#N20]
    valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#N21]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]
    valor_icms_st: Decimal = Decimal()  # :: <vICMSST> [#N23]

    def __init__(self, dado: OrderedDict):
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
    cst: int = int()  # :: <CST> [#N12]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
    motivo_icms_desonerado: int = int()  # Informar o motivo da desoneração: 1=Táxi; 3=Produtor Agropecuário; 4=Frotista/Locadora; 5=Diplomático/Consular;
    # 6=Utilitários e Motocicletas da Amazônia Ocidental e Áreas de Livre Comércio (Resolução 714/88 e 790/94 – CONTRAN e suas alterações); 7=SUFRAMA;
    # 8=Venda a Órgão Público; 9=Outros. (NT 2011/004); 10=Deficiente Condutor (Convênio ICMS 38/12); 11=Deficiente Não Condutor
    # (Convênio ICMS 38/12). :: <motDesICMS> [#N28]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]

    def __init__(self, dado: OrderedDict):
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
    cst: int = 51  # :: <CST> [#N12]
    percentual_diferimento: Decimal = Decimal()  # :: <pDif> [#N16b]
    reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
    valor_icms_diferido: Decimal = Decimal()  # :: <vICMSDif> [#N16c]
    valor_icms_operacao: Decimal = Decimal()  # :: <vICMSOp> [#N16a]

    def __init__(self, dado: OrderedDict):
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
    cst: int = 60  # :: <CST> [#N12]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <orig> [#N11]
    valor_base_calculo_retido: Decimal = Decimal()  # :: <vBCSTRet> [#N26]
    valor_icms_retido: Decimal = Decimal()  # :: <vICMSSTRet> [#N27]

    def __init__(self, dado: OrderedDict):
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
    cst: int = int()  # :: <CST> [#N12]
    motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 3=Uso na agropecuária; 9=Outros; 12=Órgão de fomento e desenvolvimento
    # agropecuário. :: <motDesICMS> [#N28]
    reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'motDesICMS':
                self.motivo_icms_desonerado = valor
            elif chave == 'pRedBC':
                self.reducao_base_calculo = Decimal(valor)
            elif chave == 'vICMSDeson':
                self.valor_icms_desonerado = Decimal(valor)


class ICMSPartilha(ICMS7090):  # [#N10a]
    cst: int = int()  # :: <CST> [#N12]
    percentual_operacao_propria: Decimal = Decimal()  # :: <pBCOp> [#N25]
    uf_st: str = str()  # :: <UFST> [#24]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pBCOp':
                self.percentual_operacao_propria = Decimal(valor)
            elif chave == 'UFST':
                self.uf_st = valor


class ICMSST(ICMS60):  # [#N10b]
    cst: int = 41  # :: <CST> [#N12]
    valor_base_calculo_st_destino: Decimal = Decimal()  # :: <vBCSTDest> [#N31]
    valor_icms_st_destino: Decimal = Decimal()  # :: <vICMSSTDest> [#N32]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vBCSTDest':
                self.valor_base_calculo_retido = Decimal(valor)
            elif chave == 'vICMSSTDest':
                self.valor_icms_st_destino = valor


class IDe(BaseObjDFe):  # [#B01]
    # data_contingenncia: datetime = None  # Data e Hora da entrada em contingência :: <dhCont>
    # justificativa_ccontigencia: str = str()  # Justificativa da entrada em contingência

    cnf: int = int()  # Código numérico que compõe a Chave de Acesso. Número aleatório gerado pelo emitente :: <cNF> [#B03]
    data_emissao: datetime = None  # Data/Hora da emissão <dhEmi> [#B09]
    data_saida_entrada: datetime = None  # Data/Hora da saída/entrada <dhSaiEnt > [#B10]
    documento_referenciado: DocumentoReferenciado = None  # Informação de Documentos Fiscais referenciados :: <NFref> #[#BA01]
    dv: int = int()  # DV da chave de acesso :: <cDV> [#B23]
    finalidade: int = int()  # Finalidade de emissão  1=NF-e normal; 2=NF-e complementar; 3=NF-e de ajuste 4=Devolução de mercadoria. :: <finNFe>  [#B25]
    id_destino: int = int()  # Identificador de local de destino. 1=Op. interna; 2=Op. interestadual; 3=Op. com exterior :: <idDest> [#B11a]
    indicador_consumidor_final: int = int()  # Indica operação com Consumidor final. 0=Normal; 1=Consumidor final; :: <indFinal> [#B25a]
    indicador_pagamento: int = int()  # Indicador da forma de pagamento. 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros. :: <indPag> [#B05]
    indicador_presenca: int = int()  # Indicador de presença dp comprador. 0=Não se aplica (por exemplo, Nota Fiscal complementar ou de ajuste); 1=Operação
    # presencial; 2=Operação não presencial, pela Internet; 3=Operação não presencial, Teleatendimento; 4=NFC-e em operação com entrega a domicílio;
    # 9=Operação não presencial,  outros. :: <indPres> [#B25b]
    modelo: int = 55  # Código do Modelo do DFe. 55=NFe; 65=NFCe <mod> [#B06]
    municipio: int = int()  # Código do Município de Ocorrência <cMunFG> [#B12]
    natureza_operacao: str = str()  # Descrição da Natureza da Operação :: <natOp> [#B04]
    nf: int = int()  # Número do DFe <nNF> [#B08]
    processo_emissao: int = int()  # Processo de emissão da NF-e. 0=Emissão de NF-e com aplicativo do contribuinte; 1=Emissão de NF-e avulsa pelo Fisco;
    # 2=Emissão de NF-e avulsa, pelo contribuinte com seu certificado digital, através do site do Fisco; 3=Emissão NF-e pelo contribuinte com aplicativo
    # fornecido pelo Fisco. :: <procEmi> [#B26]
    serie: int = int()  # Série do DFe <serie> [#B07]
    tipo_ambiente: int = int()  # Identificação do ambiente 1=Produção/2=Homologação :: <tpAmb> [#B24]
    tipo_emissao: int = 1  # Tipo de Emissão do DFe 1=Emissão normal (não em contingência); 2=Contingência FS-IA, com impressão do DANFE em formulário de
    # segurança; 3=Contingência SCAN (Sistema de Contingência do Ambiente Nacional); 4=Contingência DPEC (Declaração Prévia da Emissão em Contingência);
    # 5=Contingência FS-DA, com impressão do DANFE em formulário de segurança; 6=Contingência SVC-AN (SEFAZ Virtual de Contingência do AN); 7=Contingência
    # SVC-RS (SEFAZ Virtual de Contingência do RS); 9=Contingência off-line da NFC-e (as demais opções de contingência são válidas também para a NFC-e). Para a
    # NFC-e somente estão disponíveis e são válidas as opções de contingência 5 e 9. :: <tpEmis> [#B22]
    tipo_impressao: int = 1  # Formato de Impressão do DANFE  <tpImp> [#B21]
    tipo_nf: int = int()  # Tipo de operação. 0=Entrada; 1=Saída :: <tpNF> [#B11]
    uf: str = str()  # Código da UF do emitente do DFe :: <cUF> [#B02]
    versao_processo: str = str()  # Versão do Processo de emissão da NF-e :: <verProc> [#B27]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'cNF':
                self.cnf = int(valor)
            elif chave == 'dhEmi':
                self.data_emissao = ler_data_hora(valor)
            elif chave == 'dhSaiEnt':
                self.data_saida_entrada = ler_data_hora(valor)
            elif chave == 'NFref':
                self.documento_referenciado = DocumentoReferenciado(valor)
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
                self.natureza_operacao = valor
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
                self.uf = valor
            elif chave == 'verProc':
                self.versao_processo = valor


class Imposto(BaseObjDFe):  # [#M01]
    cofins: COFINS = None  # :: <COFINS> [#S01]
    cofins_st: COFINSST = None  # :: <COFINSST> [#T01]
    icms: ICMS = None  # Informações do ICMS da Operação própria e ST. :: <ICMS> [#N01]
    importacao: ImpostoImportacao = None  # Grupo Imposto de Importação :: <II> [#P01]
    ipi: IPI = None  # Grupo IPI Informar apenas quando o item for sujeito ao IPI :: <IPI> [#O01]
    issqn: ISSQN = None  # Campos para cálculo do ISSQN na NF-e conjugada, onde há a prestação de serviços sujeitos ao ISSQN e fornecimento de peças sujeitas
    # ao ICMS. Grupo ISSQN é mutuamente exclusivo com os grupos ICMS, IPI e II, isto é se ISSQN for informado os grupos ICMS, IPI e II não serão informados e
    # vice-versa :: <ISSQN> [#U01]
    pis: PIS = None  # ::<PIS> [#Q01}
    pis_st: PISST = None  # :: <PISST> [#R01]
    total_tributos: Decimal = Decimal()  # Valor aproximado total de tributos federais, estaduais e municipais. :: <vTotTrib> [#M02]

    def __init__(self, dado: OrderedDict):
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
    valor: Decimal = Decimal()  # :: <vII> [#P04]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#P02]
    valor_desepesas_aduaneiras: Decimal = Decimal()  # :: <vDespAdu> [#P03]
    valor_iof: Decimal = Decimal()  # :: <vIOF> [#P05]

    def __init__(self, dado: OrderedDict):
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
    fisco: str = str()  # :: <infAdFisco> [#Z02]
    informacoes_complementares: str = str()  # :: <infCpl> [#Z03]
    observacoes_contribuinte: ListaObservacoesContribuinte = []  # :: <obsCont> [#Z04]
    observacoes_fisco: ListaObservacoesContribuinte = []  # :: <obsFisco> [#Z07]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'infAdFisco':
                self.fisco = valor
            elif chave == 'infCpl':
                self.informacoes_complementares = valor
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
    cobranca: Cobranca = None  # Grupo Cobrança :: <cobr> [#Y01]
    destinatario: Destinatario = None  # Identificação do Destinatário da NF-e  :: <dest> [#E01]
    detalhamento: DetalhesProduto = dict()  # Detalhamento de Produtos e Serviços :: <det> [#H01]
    emitente: Emitente = None  # Identificação do emitente da NF-e :: <emit> [#C01]
    entrega: EntregaRetirada = None  # Identificação do Local de entrega. Informar somente se diferente do endereço
    # destinatário. :: <entrega> [#F01]
    ide: IDe = None  # Identificação da NFe :: <ide> [#B01]
    id: str = str()  # Cheve NFe precedida da literal 'NFe' :: @Id [#A03]
    informacao_adicionais: InformcaoAdicional = None  # :: <infAdic> [#Z01]
    retirada: EntregaRetirada = None  # Identificação do Local de retirada. Informar somente se diferente do endereço do
    # remetente. :: <retirada> [#F01]
    total: Total = None  # Grupo Totais da NF-e :: <total> [#W01]
    transporte: Transporte = None  # Grupo Informações do Transporte :: <transp> [#X01]
    versao: str = str()  # Versão do layout NFe :: @versao [#A02]

    def __init__(self, dado: OrderedDict):
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
            elif chave == '@id':
                self.id = valor
            elif chave == 'infAdic':
                self.informacao_adicionais = InformcaoAdicional(valor)
            elif chave == 'retirada':
                self.retirada = EntregaRetirada(valor)
            elif chave == 'total':
                self.total = Total(valor)
            elif chave == 'transp':
                self.transporte = Transporte(valor)
            elif chave == '@versao':
                self.versao = valor


class IPI(BaseObjDFe):  # [# O01]
    class_de_enquadramento: str = str()  # <clEnq> [#O02]
    cnpj_produtor: int = int()  # CNPJ do produtor da mercadoria, quando diferente do emitente. Somente para os casos de exportação direta ou
    # indireta. <CNPJProd> [#O03]
    codigo_enquadramento: str = str()  # Tabela a ser criada pela RFB, informar 999 enquanto a tabela não for criada :: <cEnq> [#O06]
    codigo_selo: str = str()  # :: <cSelo> [#O04]
    nao_tributado: IPINaoTributado = None  # Grupo CST 01, 02, 03, 04, 51, 52, 53, 54 e 55:: <IPINT> [#O08]
    quantidade_selo: int = int()  # :: <qSelo> [#O05]
    tributacao: IPITributacao = None  # Grupo do CST 00, 49, 50 e 99  :: <IPITrib> [#O07]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'clEnq':
                self.class_de_enquadramento = valor
            elif chave == 'CNPJProd':
                self.cnpj_produtor = int(valor)
            elif chave == 'cEnq':
                self.codigo_enquadramento = valor
            elif chave == 'cSelo':
                self.codigo_selo = valor
            elif chave == 'IPINT':
                self.nao_tributado = IPINaoTributado(valor)
            elif chave == 'qSelo':
                self.quantidade_selo = int(valor)
            elif chave == 'IPITrib':
                self.tributacao = IPITributacao(valor)


class IPINaoTributado(BaseObjDFe):  # [#O08]
    cst: int = int()  # 01=Entrada tributada com alíquota zero;02=Entrada isenta;03=Entrada não-tributada;04=Entrada imune;05=Entrada com

    # suspensão;51=Saída tributada com alíquota zero;52=Saída isenta;53=Saída não-tributada;54=Saída imune;55=Saída com suspensão :: <CST> [#O09]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)


class IPITributacao(BaseObjDFe):  # [#O07]
    aliquota: Decimal = Decimal()  # :: <pIPI> [#O13]
    cst: int = int()  # 00=Entrada com recuperação de crédito; 49=Outras entradas; 50=Saída tributada; 99=Outras saídas :: <CST> [#O09]
    quantidade_unidade: Decimal = Decimal()  # :: <qUnid> [#O11]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#O10]
    valor_unidade: Decimal = Decimal()  # :: <vUnid> [#O12]
    valor: Decimal = Decimal()  # :: <vIPI> [#O14]

    def __init__(self, dado: OrderedDict):
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
    aliquota: Decimal = Decimal  # :: <vAliq> [#U03]
    codigo_municipio_fato_gerador: int = int()  # :: <cMunFG> [#U05]
    codigo_municipio: int = int()  # :: <cMun> [#U14]
    codigo_pais: int = int()  # :: <cPais> [#U15]
    codigo_servico: str = str()  # :: <cServico> [#U13]
    indicador_incentivo_fiscal: int = int()  # 1=Sim; 2=Não; :: <indIcentivo> [#U17]
    indicador_iss: int = int()  # 1=Exigível, 2=Não incidência; 3=Isenção; 4=Exportação;5=Imunidade; 6=Exigibilidade Suspensa por Decisão Judicial;
    # 7=Exigibilidade Suspensa por Processo Administrativo; :: <indISS> [#U12]
    item_lista_servico: str = str()  # :: <cListServ> [#U06]
    processo: str = str()  # :: <nProcesso> [#U16]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#U02]
    valor_deducao: Decimal = Decimal()  # :: <vDeducao> [#U07]
    valor_desconto_condicionado: Decimal = Decimal()  # :: <vDescCond> [#U10]
    valor_desconto_incondicionado: Decimal = Decimal()  # :: <vDescIncond> [#U09]
    valor_outro: Decimal = Decimal()  # :: <vOutro> [#U08]
    valor_iss_retido: Decimal = Decimal()  # :: <vISSRet> [#U11]
    valor: Decimal = Decimal()  # :: <vISSQN> [#U04]

    def __init__(self, dado: OrderedDict):
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
                self.codigo_servico = valor
            elif chave == 'indIncentivo':
                self.indicador_incentivo_fiscal = int(valor)
            elif chave == 'indISS':
                self.indicador_iss = int(valor)
            elif chave == 'cListServ':
                self.item_lista_servico = valor
            elif chave == 'nProcesso':
                self.processo = valor
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
    cnpj: int = int()  # CNPJ do Emitente. :: <CNPJ> [#BA06]
    emissao: date = None  # Ano e Mês da emissão no formato AAMM :: <AAMM> [#BA05]
    modelo: int = int()  # Modelo do documento fiscal :: <mod> [#BA07]
    nf: int = int()  # Número do documento fiscal :: <nNF> [#BA09]
    serie: int = int()  # Série do documento fiscal :: <serie> [#BA08]
    uf: str = str()  # Código da UF do emitente :: <cUF> [#BA04]

    def __init__(self, dado: OrderedDict):
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
                self.uf = valor


class NFeReferenciadaProdutoRural(NFeReferenciada):  # [#BA10]
    cpf: int = int()  # CPF do Emitente :: <CPF> [#BA14]
    cte_referenciada: int = int()  # Chave de acesso do CT-e referenciada  :: <refCTe> [#BA19]
    inscricao_estadual: str = str()  # IE do Emitente :: <IE> [#BA15]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        super()._preencher()
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CPF':
                self.cpf = int(valor)
            elif chave == 'refCTe':
                self.cte_referenciada = int(valor)
            elif chave == 'IE':
                self.inscricao_estadual = valor


class ObservacaoContribuinte(BaseObjDFe):  # [#Z04]
    campo: str = str()  # :: <xCampo> [#Z05]
    texto: str = str()  # :: <xTexto> [#Z06]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'xCampo':
                self.campo = valor
            elif chave == 'xText':
                self.texto = valor


class ObservacaoFisco(ObservacaoContribuinte):  # [#Z07]
    def __init__(self, dado: OrderedDict):
        super().__init__(dado)


class PIS(BaseObjDFe):  # [#Q01]
    pis_aliq: PISAliquota = None  # Grupo PIS tributado pela alíquota :: <PISAliq> [#Q02]
    pis_nao_tributado: PISNaoTributado = None  # Grupo PIS não tributado :: <PISNT> [#Q04]
    pis_outros: PISOutros = None  # Grupo PIS Outras Operações :: <PISOutr> [#Q05]
    pis_quantidade: PISQuantidade = None  # Grupo PIS tributado por Qtde :: <PISQtde> [#Q03]

    def __init__(self, dado: OrderedDict):
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
    aliquota: Decimal = Decimal()  # <pPIS> [#Q08]
    cst: int = int()  # 01=Operação Tributável (base de cálculo = valor da operação alíquota normal (cumulativo/não cumulativo)); 02=Operação Tributável
    # (base de cálculo = valor da operação (alíquota diferenciada)); :: <CST> [#Q06]
    valor_base_calculo: Decimal = Decimal()  # <vBC> [#Q07]
    valor: Decimal = Decimal()  # <vPIS> [#Q09]

    def __init__(self, dado: OrderedDict):
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
    cst: int = int()  # 04=Operação Tributável (tributação monofásica (alíquota zero)); 05=Operação Tributável (Substituição Tributária); 06=Operação Tributável

    # (alíquota zero); 07=Operação Isenta da Contribuição;08=Operação Sem Incidência da Contribuição;09=Operação com Suspensão da Contribuição;  :: <CST> [#Q06]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CST':
                self.cst = int(valor)


class PISOutros(PISAliquota):  # {#Q05}
    cst: int = int()  # 49=Outras Operações de Saída;50=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Tributada no Mercado Interno;
    # 51=Operação com Direito a Crédito - Vinculada Exclusivamente a Receita Não Tributada no Mercado Interno;52=Operação com Direito a Crédito – Vinculada
    # Exclusivamente a Receita de Exportação;53=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e Não-Tributadas no Mercado Interno;
    # 54=Operação com Direito a Crédito - Vinculada a Receitas Tributadas no Mercado Interno e de Exportação;55=Operação com Direito a Crédito - Vinculada a
    # Receitas NãoTributadas no Mercado Interno e de Exportação;56=Operação com Direito a Crédito - Vinculada a Receitas Tributadas e Não-Tributadas no Mercado
    # Interno, e de Exportação;60=Crédito Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Tributada no Mercado Interno;61=Crédito
    # Presumido - Operação de Aquisição Vinculada Exclusivamente a Receita Não-Tributada no Mercado Interno; 62=Crédito Presumido - Operação de  Aquisição
    # Vinculada Exclusivamente a Receita de Exportação;63=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Tributadas e Não-Tributadas no Mercado
    # Interno;64=Crédito Presumido - Operação de Aquisição Vinculada a Receitas Tributadas no Mercado Interno e de Exportação;65=Crédito Presumido - Operação de
    # Aquisição Vinculada a Receitas Não-Tributadas no Mercado Interno e de Exportação;66=Crédito Presumido - Operação de Aquisição Vinculada a Receitas
    # Tributadas e Não-Tributadas no Mercado Interno, e de Exportação;67=Crédito Presumido - Outras Operações;70=Operação de Aquisição sem Direito a Crédito;
    # 71=Operação de Aquisição com Isenção;72=Operação de Aquisição com Suspensão;73=Operação de Aquisição a Alíquota Zero;74=Operação de Aquisição;
    # sem Incidência da Contribuição;75=Operação de Aquisição por Substituição Tributária;98=Outras Operações de Entrada;99=Outras Operações;
    quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#Q10]
    valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#Q11]

    def __init__(self, dado: OrderedDict):
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
    cst: int = int()  # 03=Operação Tributável (base de cálculo = quantidade vendida x alíquota por unidade de produto); :: <CST> [#Q06]
    quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#Q10]
    valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#Q11]
    valor: Decimal = Decimal()  # <vPIS> [#Q09]

    def __init__(self, dado: OrderedDict):
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
    cst: None = None  # Nessa classe não existe CST

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)


class Produto(BaseObjDFe):  # [#I01]
    codigo: str = str()  # Código do produto ou serviço. :: <cProd> [#I02]
    cfop: int = int()  # Código Fiscal de Operações e Prestações. :: <CFOP> [#I08]
    desconto: Decimal = Decimal()  # :: <vDesc> [#I17]
    descricao: str = str()  # :: <xProd> [#I04]
    ex_tipi: int = int()  # Preencher de acordo com o código EX da TIPI. Em caso de serviço, não incluir a TAG. :: <EXTIPI> [#I06]
    gtin: str = str()  # Preencher com o código GTIN-8, GTIN-12, GTIN-13 ou GTIN-14 (antigos códigos EAN, UPC e DUN-14), não informar o conteúdo da TAG em caso
    # de o produto não possuir este código. :: <cEAN> [#I03]
    gtin_tribut: str = str()  # Preencher com o código GTIN-8, GTIN-12, GTIN-13 ou GTIN-14 (antigos códigos EAN, UPC e DUN-14) da unidade tributável
    # do produto, não informar o conteúdo da TAG em caso de o produto não possuir este código. :: <cEANTrib> [#I12]
    indicador_total: int = int()  # Indica se valor do Item (vProd) entra no valor total da NF-e (vProd): 0=Valor do item (vProd) não compõe o valor total da
    # NF-e 1=Valor do item (vProd) compõe o valor total da NF-e (vProd)(v2.0) :: <indTot> [#I17b]
    ncm: int = int()  # Código NCM : Em caso de item de serviço ou item que não tenham produto (ex. transferência de crédito, crédito do ativo imobilizado,
    # etc.), informar o valor 00 (dois zeros). (NT2014/004). :: <NCM> [#I05]
    nve: str = str()  # Codificação NVE - Nomenclatura de Valor Aduaneiro e Estatística. :: <NVE> [#I05a]
    quantidade: Decimal = Decimal()  # Quantidade Comercial. :: <qCom> [#I10]
    quantidade_tributavel: Decimal = Decimal()  # Quantidade Tributável. :: <qTrib> [#I14]
    unidade: str = str()  # Unidade Comercial. :: <uCom> [#I09]
    unidade_tributavel: str = str()  # Unidade Tributável. :: <uTrib> [#I13]
    valor_seguro: Decimal = Decimal()  # :: <vSeg> [#I16]
    valor_frete: Decimal = Decimal()  # :: <vFrete> [#I15]
    valor_outro: Decimal = Decimal()  # :: <vOutro> [#I17a]
    valor_total: Decimal = Decimal()  # :: <vProd> [#I11]
    valor_unitario: Decimal = Decimal()  # :: <vUnCom> [#I10a]
    valor_unitario_tributavel: Decimal = Decimal()  # :: <vUnTrib> [#I14a]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'cProd':
                self.codigo = valor
            elif chave == 'CFOP':
                self.cfop = int(valor)
            elif chave == 'vDesc':
                self.desconto = Decimal(valor)
            elif chave == 'xProd':
                self.desconto = valor
            elif chave == 'EXTIPI':
                self.ex_tipi = int(valor)
            elif chave == 'vFrete':
                self.valor_frete = Decimal(valor)
            elif chave == 'cEAN':
                self.gtin = valor
            elif chave == 'cEANTrib':
                self.gtin_tribut = valor
            elif chave == 'indTot':
                self.indicador_total = int(valor)
            elif chave == 'NCM':
                self.ncm = int(valor)
            elif chave == 'NVE':
                self.nve = valor
            elif chave == 'vOutro':
                self.valor_outro = Decimal(valor)
            elif chave == 'qCom':
                self.quantidade = Decimal(valor)
            elif chave == 'qTrib':
                self.quantidade_tributavel = Decimal(valor)
            elif chave == 'vSeg':
                self.valor_seguro = Decimal(valor)
            elif chave == 'uCom':
                self.unidade = valor
            elif chave == 'uTrib':
                self.unidade_tributavel = valor
            elif chave == 'vProd':
                self.valor_total = Decimal(valor)
            elif chave == 'vUnCom':
                self.valor_unitario = Decimal(valor)
            elif chave == 'vUnTrib':
                self.valor_unitario_tributavel = Decimal(valor)


class RetencaoTransporte(BaseObjDFe):  # [#X11]
    aliquota: Decimal = Decimal()  # :: <pICMSRet> [#X14]
    cfop: int = int()  # :: <CFOP> [#X16]
    codigo_municipio: int = int()  # :: <cMunFG> [#X127
    valor_base_calculo: Decimal = Decimal()  # :: <vBCRet> [#X13]
    valor_icms: Decimal = Decimal()  # :: <vICMSRet> [#X15]
    valor_servico: Decimal = Decimal()  # :: <vServ> [#X12]

    def __init__(self, dado: OrderedDict):
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
    icms: TotalICMS = None  # :: <ICMSTot> [#W02]
    issqn: TotalISSQN = None  # :: <ISSQNtot> [#W17]
    retencao: TotalRetencao = None  # :: <retTrib> [#W23]

    def __init__(self, dado: OrderedDict):
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
    valor: Decimal = Decimal()  # :: <vICMS> [#W04]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#W03]
    valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#W05]
    valor_cofins: Decimal = Decimal()  # :: <vCOFINS> [#W14]
    valor_desconto: Decimal = Decimal()  # :: <vDesc> [#W10]
    valor_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#W04a]
    valor_frete: Decimal = Decimal()  # :: <vFrete> [#W08]
    valor_imposto_importado: Decimal = Decimal()  # :: <vII> [#W11]
    valor_ipi: Decimal = Decimal()  # :: <vIPI> [#W12]
    valor_nf: Decimal = Decimal()  # :: <vNF> [#W16]
    valor_outros: Decimal = Decimal()  # :: <vOutro> [#W15]
    valor_produtos: Decimal = Decimal()  # :: <vProd> [#W07]
    valor_pis: Decimal = Decimal()  # :: <vPIS> [#W13]
    valor_seguro: Decimal = Decimal()  # :: <vSeg> [#W09]
    valor_st: Decimal = Decimal()  # :: <vST> [#W06]
    valor_total_tributos: Decimal = Decimal()  # :: <vTotTrib> [#W16a]

    def __init__(self, dado: OrderedDict):
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
    codigo_regime_tributacao: int = int()  # 1=Microempresa Municipal; 2=Estimativa;3=Sociedade de Profissionais; 4=Cooperativa;5=Microempresário Individual
    # (MEI);6=Microempresário e Empresa de Pequeno Porte (ME/EPP) :: <cRegTrib> [#W22g]
    data_competencia: date = None  # :: <dCompet> [#W22a]
    valor: Decimal = Decimal()  # :: <vISS> [#W20]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#W19]
    valor_cofins: Decimal = Decimal()  # :: <vCOFINS> [#W22]
    valor_deducao: Decimal = Decimal()  # :: <vDeducao> [#W22b]
    valor_desconto_condicionado: Decimal = Decimal()  # :: <vDescCond> [#W22e]
    valor_desconto_incondicionado: Decimal = Decimal()  # :: <vDescIncond> [#W22d]
    valor_outro: Decimal = Decimal()  # :: <vOutro> [#W22c]
    valor_iss_retido: Decimal = Decimal()  # :: <vISSRet> [#W22f]
    valor_pis: Decimal = Decimal()  # :: <vPIS> [#W21]
    valor_servico: Decimal = Decimal()  # :: <vServ> [#W18]

    def __init__(self, dado: OrderedDict):
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
    retencao_cofins: Decimal = Decimal()  # :: <vRetCOFINS> [#W25]
    retencao_csll: Decimal = Decimal()  # :: <vRetCSLL> [#W26]
    retencao_irrf: Decimal = Decimal()  # :: <vRetIRRF> [#W28]
    retencao_pis: Decimal = Decimal()  # :: <vRetPIS> [#W24]
    retencao_previdencia: Decimal = Decimal()  # :: <vRetPrev> [#W30]
    valor_base_calculo_irrf: Decimal = Decimal()  # :: <vRetBCIRRF> [#W27]
    valor_base_calculo_previdencia: Decimal = Decimal()  # :: <vRetBCPrev> [#W29]

    def __init__(self, dado: OrderedDict):
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
    cnpj: int = int()  # :: <CNPJ> [#X04]
    cpf: int = int()  # :: <CPF> [#X05]
    endereco: str = str()  # :: <xEnder> [#X08]
    inscricao_estadual: str = str()  # :: <IE> [#X07]
    municipio: str = str()  # :: <xMun> [#X09]
    razao_social: str = str()  # :: <xNome> [#X06]
    retencao: RetencaoTransporte = None  # :: <retTransp> [#X11]
    uf: str = str()  # :: <UF> [#X10]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'CNPJ':
                self.cnpj = int(valor)
            elif chave == 'cpf':
                self.cpf = int(valor)
            elif chave == 'xEnder':
                self.endereco = valor
            elif chave == 'IE':
                self.inscricao_estadual = valor
            elif chave == 'xMun':
                self.municipio = valor
            elif chave == 'xNome':
                self.razao_social = valor
            elif chave == 'retTransp':
                self.retencao = RetencaoTransporte(valor)
            elif chave == 'UF':
                self.uf = valor


class Transporte(BaseObjDFe):  # [#X01]
    balsa: str = str()  # :: <balsa> [#X25b]
    modalidade_frete: int = int()  # 0=Por conta do emitente;1=Por conta do destinatário/remetente;2=Por conta de terceiros;9=Sem frete.  :: <modFrete> [#X02]
    reboques: ListaTransporteReboques = []  # Grupo Reboque :: <reboque>
    transportador: Transportador = None  # Grupo Transportador  :: <transporta>[#X03]
    vagao: str = str()  # :: <vagao> [#X25a]
    veiculo: TransporteVeiculo = None  # :: <veicTransp> [#X18]
    volumes: ListaTransporteVolumes = []  # :: <vol> [#X26]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'balsa':
                self.balsa = valor
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
                self.vagao = valor
            elif chave == 'vaicTransp':
                self.veiculo = TransporteVeiculo(valor)
            elif chave == 'vol':
                if isinstance(valor, list):
                    for volume in valor:
                        self.volumes.append(TransporteVolume(volume))
                else:
                    self.volumes.append(TransporteVolume(valor))


class TransporteReboque(BaseObjDFe):  # [#X22]
    placa: str = str()  # :: <placa> [#X23]
    rntc: str = str()  # Registro Nacional de Transportador de Carga (ANTT) :: <RNTC> [#X25]
    uf: str = str()  # :: <UF> [#X24]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'placa':
                self.placa = valor
            elif chave == 'RNTC':
                self.rntc = valor
            elif chave == 'UF':
                self.uf = valor


class TransporteVeiculo(TransporteReboque):  # [#X18]
    def __init__(self, dado: OrderedDict):
        super().__init__(dado)


class TransporteVolume(BaseObjDFe):  # :: <vol> [#X26]
    especie: str = str()  # :: <esp> [#X28]
    lacres: ListaLacres = []  # :: <lacres> [#X33]
    marca: str = str()  # :: <marca> [#X29]
    numercao: str = str()  # :: <nVol> [#X30]
    peso_bruto: int = int()  # :: <pesoB> [#X32]
    peso_liquido: Decimal = Decimal()  # :: <pesoL> [#X31]
    quantidade: int = int()  # :: <qVol> [#X27]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'esp':
                self.especie = valor
            elif chave == 'lacres':
                if isinstance(valor, list):
                    for lacre in valor:
                        self.lacres.append(VolumeLacre(lacre))
                else:
                    self.lacres.append(VolumeLacre(valor))
            elif chave == 'marca':
                self.marca = valor
            elif chave == 'nVol':
                self.numercao = valor
            elif chave == 'pesoB':
                self.peso_bruto = Decimal(valor)
            elif chave == 'pesoL':
                self.peso_liquido = Decimal(valor)
            elif chave == 'qVol':
                self.quantidade = int(valor)


class TributoDevolvido(BaseObjDFe):  # [#UA01]
    percentual_devolucao: Decimal = Decimal()  # O valor máximo deste percentual é 100%, no caso de devolução total da mercadoria. :: <pDevol> [#UA02]
    ipi: TributoDevolvidoIPI = None  # :: <IPI> [#UA03]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'pDevol':
                self.percentual_devolucao = Decimal(valor)
            elif chave == 'IPI':
                self.ipi = TributoDevolvidoIPI(valor)


class TributoDevolvidoIPI(BaseObjDFe):  # [#UA03]
    valor: Decimal = Decimal()  # :: <vIPIDevol> [#UA04]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'vIPIDevol':
                self.valor = Decimal(valor)


class VolumeLacre(BaseObjDFe):  # [#X33]
    numero: str = str()  # :: <nLacre> [#X4]

    def __init__(self, dado: OrderedDict):
        super().__init__(dado)

    def _preencher(self):
        for chave, valor in self._conteudo_xml.items():
            if chave == 'nLacre':
                self.numero = valor


# Tipos
DetalhesProduto = Dict[int, Detalhamento]
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
    return datetime.strptime(texto[:22] + texto[23:], '%Y-%m-%dT%H:%M:%S%z')
