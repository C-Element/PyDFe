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
    inscricao_estadual: str = str()  #:: <IE> [#C17]
    inscricao_estadual_st: str = str()  #:: <IEST> [#C18]
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


class ICMS30(BaseObjDFe):  # [#N05]
    aliquota_st: Decimal = Decimal()  # :: <pICMSST> [#N22]
    cst: int = 30  # :: <CST> [#N12]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <ICMS00> [#N11]
    modalidade_base_calculo_st: int = int()  # 0=Preço tabelado ou máximo sugerido; 1=Lista Negativa (valor); 2=Lista Positiva (valor); 3=Lista Neutra (valor);
    # 4=Margem Valor Agregado (%); 5=Pauta (valor); :: <modBCST> [#N18]
    motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 6=Utilitários e Motocicletas da Amazônia Ocidental e Áreas de Livre Comércio
    # (Resolução 714/88 e 790/94 – CONTRAN e suas alterações); 7=SUFRAMA; 9=Outros;. :: <motDesICMS> [#N28]
    mva_st: Decimal = Decimal()  # Percentual da margem de valor Adicionado do ICMS ST :: <pMVAST> [#N19]
    reducao_base_calculo_st: Decimal = Decimal()  # Percentual da Redução de BC do ICMS ST :: <pRedBCST> [#N20]
    valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#N21]
    valor_icms_st: Decimal = Decimal()  # :: <vlICMSST> [#N23]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]


class ICMS4050(BaseObjDFe):  # [#N06]
    cst: int = int()  # :: <CST> [#N12]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <ICMS00> [#N11]
    motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 1=Táxi; 3=Produtor Agropecuário; 4=Frotista/Locadora; 5=Diplomático/Consular;
    # 6=Utilitários e Motocicletas da Amazônia Ocidental e Áreas de Livre Comércio (Resolução 714/88 e 790/94 – CONTRAN e suas alterações); 7=SUFRAMA;
    # 8=Venda a Órgão Público; 9=Outros. (NT 2011/004); 10=Deficiente Condutor (Convênio ICMS 38/12); 11=Deficiente Não Condutor
    # (Convênio ICMS 38/12). :: <motDesICMS> [#N28]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]


class ICMS51(ICMS00):  # [#N07]
    cst: int = 51  # :: <CST> [#N12]
    percentual_diferimento: Decimal = Decimal()  # :: <pDif> [#N16b]
    reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
    valor_icms_diferido: Decimal = Decimal()  # :: <vICMSDif> [#N16c]
    valor_icms_operacao: Decimal = Decimal()  # :: <vICMSOp> [#N16a]


class ICMS60(BaseObjDFe):  # [#N08]
    cst: int = 60  # :: <CST> [#N12]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <ICMS00> [#N11]
    valor_base_calculo_retido: Decimal = Decimal()  # :: <vBCSTRet> [#N26]
    valor_icms_retido: Decimal = Decimal()  # :: <vICMSSTRet> [#N27]


class ICMS7090(ICMS10):  # [#N09] [#N10]
    cst: int = int()  # :: <CST> [#N12]
    motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 3=Uso na agropecuária; 9=Outros; 12=Órgão de fomento e desenvolvimento
    # agropecuário. :: <motDesICMS> [#N28]
    reducao_base_calculo: Decimal = Decimal()  # Percentual da Redução de BC :: <pRedBC> [#N14]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]


class ICMSPartilha(ICMS7090):  # [#N10a]
    cst: int = int()  # :: <CST> [#N12]
    percentual_operacao_propria: Decimal = Decimal()  # :: <pBCOp> [#N25]
    uf_st: str = str()  # :: <UFST> [#24]


class ICMSST(ICMS60):  # [#N10b]
    cst: int = 41  # :: <CST> [#N12]
    valor_base_calculo_st_destino: Decimal = Decimal()  # :: <vBCSTDest> [#N31]
    valor_icms_st_destino: Decimal = Decimal()  # :: <vICMSSTDest> [#N32]


class IDe(BaseObjDFe):  # [#B01]
    # data_contingenncia: datetime = None  # Data e Hora da entrada em contingência :: <dhCont>
    # justificativa_ccontigencia: str = str()  # Justificativa da entrada em contingência

    cnf: int = int()  # Código numérico que compõe a Chave de Acesso. Número aleatório gerado pelo emitente :: <cNF> [#B03]
    data_emissao: datetime = None  # Data/Hora da emissão <dhEmi> [#B09]
    data_saida_entrada: datetime = None  # Data/Hora da saída/entrada <dhSaiEnt > [#B10]
    documento_referenciado: DocumentoReferenciado = DocumentoReferenciado()  # Informação de Documentos Fiscais referenciados :: <NFref> #[#BA01]
    dv: int = int()  # DV da chave de acesso :: <cDV> [#B23]
    finalidade: int = int()  # Finalidade de emissão  1=NF-e normal; 2=NF-e complementar; 3=NF-e de ajuste 4=Devolução de mercadoria. :: <finNFe>  [#B25]
    id_dest: int = int()  # Identificador de local de destino. 1=Op. interna; 2=Op. interestadual; 3=Op. com exterior :: <idDest> [#B11a]
    ind_final: int = int()  # Indica operação com Consumidor final. 0=Normal; 1=Consumidor final; :: <indFinal> [#B25a]
    ind_pag: int = int()  # Indicador da forma de pagamento. 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros. :: <indPag> [#B05]
    ind_presenca: int = int()  # Indicador de presença dp comprador. 0=Não se aplica (por exemplo, Nota Fiscal complementar ou de ajuste); 1=Operação
    # presencial; 2=Operação não presencial, pela Internet; 3=Operação não presencial, Teleatendimento; 4=NFC-e em operação com entrega a domicílio;
    # 9=Operação não presencial,  outros. :: <indPres> [#B25b]
    modelo: int = 55  # Código do Modelo do DFe. 55=NFe; 65=NFCe <mod> [#B06]
    municipio: int = int()  # Código do Município de Ocorrência <cMunFG> [#B12]
    nat_operacao: str = str()  # Descrição da Natureza da Operação :: <natOp> [#B04]
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


class Imposto(BaseObjDFe):  # [#M01]
    cofins: COFINS = COFINS()  # :: <COFINS> [#S01]
    cofins_st: COFINSST = COFINSST  # :: <COFINSST> [#T01]
    icms: ICMS = ICMS()  # Informações do ICMS da Operação própria e ST. :: <icms> [#N01]
    importacao: ImpostoImportacao = ImpostoImportacao()  # Grupo Imposto de Importação :: <II> [#P01]
    ipi: IPI = IPI()  # Grupo IPI Informar apenas quando o item for sujeito ao IPI :: <IPI> [#O01]
    issqn: ISSQN = ISSQN()  # Campos para cálculo do ISSQN na NF-e conjugada, onde há a prestação de serviços sujeitos ao ISSQN e fornecimento de peças sujeitas
    # ao ICMS. Grupo ISSQN é mutuamente exclusivo com os grupos ICMS, IPI e II, isto é se ISSQN for informado os grupos ICMS, IPI e II não serão informados e
    # vice-versa :: <ISSQN> [#U01]
    pis: PIS = PIS()  # ::<PIS> [#Q01}
    pis_st: PISST = PISST()  # :: <PISST> [#R01]
    total_tributos: Decimal = Decimal()  # Valor aproximado total de tributos federais, estaduais e municipais. :: <vTotTrib> [#M02]


class ImpostoImportacao(BaseObjDFe):  # [#P01]
    valor: Decimal = Decimal()  # :: <vII> [#P04]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#P02]
    valor_desepesas_aduaneiras: Decimal = Decimal()  # :: <vDespAdu> [#P03]
    valor_iof: Decimal = Decimal()  # :: <vIOF> [#P05]


class InformcaoAdicional(BaseObjDFe):  # [#Z01]
    fisco: str = str()  # :: <infAdFisco> [#Z02]
    informacoes_complementares: str = str()  # :: <infCpl> [#Z03]
    observacoes_contribuinte: ListaObservacoesContribuinte = []  # :: <obsCont> [#Z04]
    observacoes_fisco: ListaObservacoesContribuinte = []  # :: <obsFisco> [#Z07]


class InfNFe(BaseObjDFe):  # [#A01]
    cobranca: Cobranca = Cobranca()  # Grupo Cobrança :: <cobr> [#Y01]
    destinatario: Destinatario = Destinatario()  # Identificação do Destinatário da NF-e  :: <dest> [#E01]
    detalhamento: DetalhesProduto = dict()  # Detalhamento de Produtos e Serviços :: <det> [#H01]
    emitente: Emitente = Emitente()  # Identificação do emitente da NF-e :: <emit> [#C01]
    entrega: EntregaRetirada = EntregaRetirada()  # Identificação do Local de entrega. Informar somente se diferente do endereço
    # destinatário. :: <entrega> [#F01]
    ide: IDe = IDe()  # Identificação da NFe :: <ide> [#B01]
    id: str = str()  # Cheve NFe precedida da literal 'NFe' :: @Id [#A03]
    informacao_adicionais: InformcaoAdicional = InformcaoAdicional()  # :: <infAdic> [#Z01]
    retirada: EntregaRetirada = EntregaRetirada()  # Identificação do Local de retirada. Informar somente se diferente do endereço do
    # remetente. :: <retirada> [#F01]
    total: Total = Total()  # Grupo Totais da NF-e :: <total> [#W01]
    transporte: Transporte = Transporte()  # Grupo Informações do Transporte :: <transp> [#X01]
    versao: str = str()  # Versão do layout NFe :: @versao [#A02]


class IPI(BaseObjDFe):  # [# O01]
    class_de_enquadramento: str = str()  # <clEnq> [#O02]
    cnpj_produtor: int = int()  # CNPJ do produtor da mercadoria, quando diferente do emitente. Somente para os casos de exportação direta ou
    # indireta. <CNPJProd> [#O03]
    codigo_enquadramento: str = str()  # Tabela a ser criada pela RFB, informar 999 enquanto a tabela não for criada :: <cEnq> [#O06]
    codigo_selo: str = str()  # :: <cSelo> [#O04]
    nao_tributado: IPINaoTributado = IPINaoTributado()  # Grupo CST 01, 02, 03, 04, 51, 52, 53, 54 e 55:: <IPIINT> [#O08]
    quantidade_selo: int = int()  # :: <qSelo> [#O05]
    tributacao: IPITributacao = IPITributacao()  # Grupo do CST 00, 49, 50 e 99  :: <IPITrib> [#O07]


class IPINaoTributado(BaseObjDFe):  # [#O08]
    cst: int = int()  # 01=Entrada tributada com alíquota zero;02=Entrada isenta;03=Entrada não-tributada;04=Entrada imune;05=Entrada com suspensão;
    # 51=Saída tributada com alíquota zero;52=Saída isenta;53=Saída não-tributada;54=Saída imune;55=Saída com suspensão :: <CST> [#O09]


class IPITributacao(BaseObjDFe):  # [#O07]
    aliquota: Decimal = Decimal()  # :: <pIPI> [#O13]
    cst: int = int()  # 00=Entrada com recuperação de crédito; 49=Outras entradas; 50=Saída tributada; 99=Outras saídas :: <CST> [#O09]
    quantidade_unidade: Decimal = Decimal()  # :: <qUnid> [#O11]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#O10]
    valor_unidade: Decimal = Decimal()  # :: <vUnid> [#O12]
    valor: Decimal = Decimal()  # :: <vIPI> [#O14]


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


class NFeReferenciada(BaseObjDFe):  # [#BA03]
    cnpj: int = int()  # CNPJ do Emitente. :: <CNPJ> [#BA06]
    emissao: date = None  # Ano e Mês da emissão no formato AAMM :: <AAMM> [#BA05]
    modelo: int = int()  # Modelo do documento fiscal :: <mod> [#BA07]
    nf: int = int()  # Número do documento fiscal :: <nNF> [#BA09]
    serie: int = int()  # Série do documento fiscal :: <serie> [#BA08]
    uf: str = str()  # Código da UF do emitente :: <cUF> [#BA04]


class NFeReferenciadaProdutoRural(BaseObjDFe):  # [#BA10]
    cnpj: int = int()  # CNPJ do Emitente :: <CNPJ> [#BA13]
    cpf: int = int()  # CPF do Emitente :: <CPF> [#BA14]
    cte_referenciada: int = int()  # Chave de acesso do CT-e referenciada  :: <refCTe> [#BA19]
    emissao: date = None  # Ano e Mês da emissão no formato AAMM :: <AAMM> [#BA12]
    inscricao_estadual: int = int()  # IE do Emitente :: <IE> [#BA15]
    modelo: int = int()  # Modelo do documento fiscal :: <mod> [#BA16]
    nf: int = int()  # Número do documento fiscal :: <nNF> [#BA18]
    serie: int = int()  # Série do documento fiscal :: <serie> [#BA17]
    uf: str = str()  # Código da UF do emitente :: <cUF> [#BA11]


class ObservacaoContribuinte(BaseObjDFe):  # [#Z04]
    campo: str = str()  # :: <xCampo> [#Z05]
    texto: str = str()  # :: <xCampo> [#Z06]


class ObservacaoFisco(ObservacaoContribuinte):  # [#Z07]
    pass


class PIS(BaseObjDFe):  # [#Q01]
    pis_aliq: PISAliquota = PISAliquota()  # Grupo PIS tributado pela alíquota :: <PISAliq> [#Q02]
    pis_nao_tributado: PISNaoTributado = PISNaoTributado()  # Grupo PIS não tributado :: <PISNT> [#Q04]
    pis_outros: PISOutros = PISOutros()  # Grupo PIS Outras Operações :: <PISOutr> [#Q05]
    pis_quantidade: PISQuantidade = PISQuantidade()  # Grupo PIS tributado por Qtde :: <PISQtde> [#Q03]


class PISAliquota(BaseObjDFe):  # {#Q02}
    aliquota: Decimal = Decimal()  # <pPIS> [#Q08]
    cst: int = int()  # 01=Operação Tributável (base de cálculo = valor da operação alíquota normal (cumulativo/não cumulativo)); 02=Operação Tributável
    # (base de cálculo = valor da operação (alíquota diferenciada)); :: <CST> [#Q06]
    valor_base_calculo: Decimal = Decimal()  # <vBC> [#Q07]
    valor: Decimal = Decimal()  # <vPIS> [#Q09]


class PISNaoTributado(BaseObjDFe):  # {#Q04}
    cst: int = int()  # 04=Operação Tributável (tributação monofásica (alíquota zero)); 05=Operação Tributável (Substituição Tributária); 06=Operação Tributável
    # (alíquota zero); 07=Operação Isenta da Contribuição;08=Operação Sem Incidência da Contribuição;09=Operação com Suspensão da Contribuição;  :: <CST> [#Q06]


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


class PISQuantidade(BaseObjDFe):  # {#Q03}
    cst: int = int()  # 03=Operação Tributável (base de cálculo = quantidade vendida x alíquota por unidade de produto); :: <CST> [#Q06]
    quantidade_base_calculo: Decimal = Decimal()  # <qBCProd> [#Q10]
    valor_aliquota: Decimal = Decimal()  # <vAliqProd> [#Q11]
    valor: Decimal = Decimal()  # <vPIS> [#Q09]


class PISST(PISOutros):  # [#R01]
    cst: None = None  # Nessa classe não existe CST


class Produto(BaseObjDFe):  # [#I01]
    codigo: str = str()  # Código do produto ou serviço. :: <cProd> [#I02]
    cfop: int = int()  # Código Fiscal de Operações e Prestações. :: <CFOP> [#I08]
    desconto: Decimal = Decimal()  # :: <vDesc> [#I17]
    descricao: str = str()  # :: <xProd> [#I04]
    ex_tipi: int = int()  # Preencher de acordo com o código EX da TIPI. Em caso de serviço, não incluir a TAG. :: <EXTIPI> [#I06]
    frete: Decimal = Decimal()  # :: <vFrete> [#I15]
    gtin: str = str()  # Preencher com o código GTIN-8, GTIN-12, GTIN-13 ou GTIN-14 (antigos códigos EAN, UPC e DUN-14), não informar o conteúdo da TAG em caso
    # de o produto não possuir este código. :: <cEAN> [#I03]
    gtin_tribut: str = str()  # Preencher com o código GTIN-8, GTIN-12, GTIN-13 ou GTIN-14 (antigos códigos EAN, UPC e DUN-14) da unidade tributável
    # do produto, não informar o conteúdo da TAG em caso de o produto não possuir este código. :: <cEANTrib> [#I12]
    indicador_total: int = int()  # Indica se valor do Item (vProd) entra no valor total da NF-e (vProd): 0=Valor do item (vProd) não compõe o valor total da
    # NF-e 1=Valor do item (vProd) compõe o valor total da NF-e (vProd)(v2.0) :: <indTot> [#I17b]
    ncm: int = int()  # Código NCM : Em caso de item de serviço ou item que não tenham produto (ex. transferência de crédito, crédito do ativo imobilizado,
    # etc.), informar o valor 00 (dois zeros). (NT2014/004). :: <NCM> [#I05]
    nvm: str = str()  # Codificação NVE - Nomenclatura de Valor Aduaneiro e Estatística. :: <NVE> [#I05a]
    outro: Decimal = Decimal()  # :: <vOutro> [#I17a]
    quantidade: Decimal = Decimal()  # Quantidade Comercial. :: <qCom> [#I10]
    quantidade_tributavel: Decimal = Decimal()  # Quantidade Tributável. :: <qTrib> [#I14]
    seguro: Decimal = Decimal()  # :: <vSeg> [#I16]
    unidade: str = str()  # Unidade Comercial. :: <uCom> [#I09]
    unidade_tributavel: str = str()  # Unidade Tributável. :: <uCom> [#I13]
    valor_unitario: Decimal = Decimal()  # :: <vUnCom> [#I11]
    valor_unitario_tributavel: Decimal = Decimal()  # :: <vUnTrib> [#I14a]
    valor_total: Decimal = Decimal()  # :: <vUnCom> [#11]


class RetencaoTransporte(BaseObjDFe):  # [#X11]
    aliquota: Decimal = Decimal()  # :: <pICMSRet> [#X14]
    cfop: int = int()  # :: <CFOP> [#X16]
    codigo_municipio: int = int()  # :: <cMunFG> [#X127
    valor_base_calculo: Decimal = Decimal()  # :: <vBCRet> [#X13]
    valor_icms: Decimal = Decimal()  # :: <vICMSRet> [#X15]
    valor_servico: Decimal = Decimal()  # :: <vServ> [#X12]


class Total(BaseObjDFe):  # [#W01]
    icms: TotalICMS = TotalICMS()  # :: <ICMSTot> [#W02]
    issqn: TotalISSQN = TotalISSQN()  # :: <ISSQNtot> [#W17]
    retencao: TotalRetencao = TotalRetencao()  # :: <retTrib> [#W23]


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


class TotalRetencao(BaseObjDFe):  # :: [#W23]
    retencao_cofins: Decimal = Decimal()  # :: <vRetCOFINS> [#W25]
    retencao_csll: Decimal = Decimal()  # :: <vRetCSLL> [#W26]
    retencao_irrf: Decimal = Decimal()  # :: <vRetIRRF> [#W28]
    retencao_pis: Decimal = Decimal()  # :: <vRetPIS> [#W24]
    retencao_previdencia: Decimal = Decimal()  # :: <vRetPrev> [#W30]
    valor_base_calculo_irrf: Decimal = Decimal()  # :: <vRetBCIRRF> [#W27]
    valor_base_calculo_previdencia: Decimal = Decimal()  # :: <vRetBCPrev> [#W29]


class Transportador(BaseObjDFe):  # [#X03]
    cnpj: int = int()  # :: <CNPJ> [#X04]
    cpf: int = int()  # :: <CPF> [#X05]
    endereco: str = str()  # :: <xEnder> [#X08]
    inscricao_estadual: str = str()  # :: <IE> [#X07]
    municipio: str = str()  # :: <xMun> [#X09]
    razao_social: str = str()  # :: <xNome> [#X06]
    retencao: RetencaoTransporte = RetencaoTransporte()  # :: <retTransp> [#X11]
    uf: str = str()  # :: <UF> [#X10]


class Transporte(BaseObjDFe):  # [#X01]
    balsa: str = str()  # :: <balsa> [#X25b]
    modalidade_frete: int = int()  # 0=Por conta do emitente;1=Por conta do destinatário/remetente;2=Por conta de terceiros;9=Sem frete.  :: <modFrete> [#X02]
    reboque: ListaTransporteReboques = []  # Grupo Reboque :: <reboque>
    transportador: Transportador = Transportador()  # Grupo Transportador  :: <transporta>[#X03]
    vagao: str = str()  # :: <vagao> [#X25a]
    veiculo: TransporteVeiculo = TransporteVeiculo()  # :: <veicTransp> [#X18]
    volumes: ListaTransporteVolumes = []  # :: <vol> [#X26]


class TransporteReboque(BaseObjDFe):  # [#X22]
    placa: str = str()  # :: <placa> [#X23]
    rntc: str = str()  # Registro Nacional de Transportador de Carga (ANTT) :: <RNTC> [#X25]
    uf: str = str()  # :: <UF> [#X24]


class TransporteVeiculo(TransporteReboque):  # [#X18]
    pass


class TransporteVolume(BaseObjDFe):  # :: <vol> [#X26]
    especie: str = str()  # :: <esp> [#X28]
    lacres: ListaLacres = []  # :: <lacres> [#X33]
    marca: str = str()  # :: <marca> [#X29]
    numercao: str = str()  # :: <nVol> [#X30]
    peso_liquido: Decimal = Decimal()  # :: <peloL> [#X31]
    peso_bruto: int = int()  # :: <pesoB> [#X32]
    quantidade: int = int()  # :: <qVol> [#X27]


class TributoDevolvido(BaseObjDFe):  # [#UA01]
    percentual_devolucao: Decimal = Decimal()  # O valor máximo deste percentual é 100%, no caso de devolução total da mercadoria. :: <pDevol> [#UA02]
    ipi: TributoDevolvidoIPI = TributoDevolvidoIPI()  # :: <IPI> [#UA03]


class TributoDevolvidoIPI(BaseObjDFe):  # [#UA03]
    valor: Decimal = Decimal()  # :: <vIPIDevol> [#UA04]


class VolumeLacre(BaseObjDFe):  # [#X33]
    numero: str = str()  # :: <nLacre> [#X4]


# Tipos
DetalhesProduto = Dict[int, Detalhamento]
ListaDuplicatas = List[Duplicata]
ListaLacres = List[VolumeLacre]
ListaObservacoesContribuinte = List[ObservacaoContribuinte]
ListaObservacoesFisco = List[ObservacaoFisco]
ListaTransporteReboques = List[TransporteReboque]
ListaTransporteVolumes = List[TransporteReboque]


# funções

def ler_data(texto: str) -> date:
    return datetime.strptime(texto, '%Y-%m-%d').date()


def ler_data_hora(texto: str) -> datetime:
    return datetime.strptime(texto[:22] + texto[23:], '%Y-%m-%dT%H:%M:%S%z')
