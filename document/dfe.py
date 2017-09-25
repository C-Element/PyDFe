from datetime import datetime, date

# Exceções
from decimal import Decimal


class ErroDeInicializacao(Exception):
    pass


class DocumentoInvalido(Exception):
    pass


# classes DFe
class Destinatario(object):  # [#E01]
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
    endereco = Endereco()  # :: <enderDest> [#E05]
    razao_social: str = str()  # Razão Sócial ou Nome do destinatário :: <xNome> [#E04]


class Detalhamento(object):  # [#H01]
    imposto: Imposto = Imposto()  # Tributos incidentes no Produto ou Serviço. :: <impost> [#M01]
    informacoes_adicionais: str = str()  # Informações Adicionais :: <infAdProd> [#V01]
    numero_item: int = int()  # Número do item :: @nItem [#H02]
    produto: Produto = Produto()  # Detalhamento de Produtos e Serviços :: <prod> [#I01]


class DocumentoReferenciado(object):  # [#BA01]
    chave_nfe_ref: int = int()  # Chave de acesso da NF-e referenciada :: <refNFe> [#BA02]
    informacao_nfe_ref: NFeReferenciada = NFeReferenciada()  # Informação da NF modelo 1/1A referenciada :: <refNF> [#BA03]
    informacao_nfe_pr_ref: NFeReferenciadaProdutoRural = NFeReferenciadaProdutoRural()  # Informações da NF de produtor rural referenciada :: <refNFP> [#BA10]
    informacao_ecf_ref: ECFReferenciado = ECFReferenciado()  # Informações do Cupom Fiscal referenciado :: <refECF> [#BA20]


class ECFReferenciado(object):  # [#BA20]
    modelo: int = int()  # Modelo do cupom fiscal :: <mod> [#BA21]
    numero_coo: int = int()  # Número do Contador de Ordem de Operação - COO :: <nCOO> [#BA23]
    numero_ecf: int = int()  # Número de ordem sequencial do ECF :: <nECF> [#BA22]


class Emitente(object):  # [#C01]
    cnpj: int = int()  # :: <CNPJ> [#C02]
    cpf: int = int()  # :: <CPF> [#C02a]
    endereco = Endereco()  # :: <enderEmit> [#C05]
    fantasia: str = str()  # Nome Fantasia do emitente :: <xFant> [#C04]
    inscricao_estadual: str = str()  #:: <IE> [#C17]
    inscricao_estadual_st: str = str()  #:: <IEST> [#C18]
    razao_social: str = str()  # Razão Sócial ou Nome do emitente :: <xNome> [#C03]


class Endereco(object):  # [#C05]
    bairro: str = str()  # :: <xBairro> [#C09] [#E09]
    cep: int = int()  # :: <CEP> [#C13] [#E13]
    codigo_municipio: int = int()  # :: <cMun> [#C10] [#E10]
    codigo_pais: int = int()  # :: <cPais> [#C14] [#E14]
    complemento: str = str()  # :: <xCpl> [#C08] [#E08]
    logradouro: str = str()  # :: <xLgr> [#C06] [#E06]
    municipio: str = str()  # :: <xMun> [#C11] [#E11]
    nro: str = str()  # :: <nro> [#C07] [#E07]
    pais: str = str()  # :: <xPais> [#C15] [#E15]
    telefone: int = int()  # :: <fone> [#C16] [#E16]
    uf: str = str()  # :: <UF> [#C12] [#E12]


class EntregaRetirada(object):  # [#F01]
    bairro: str = str()  # :: <xBairro> [#F06]
    cnpj: int = int()  # CNPJ do Emitente :: <CNPJ> [#F02]
    cpf: int = int()  # CPF do Emitente :: <CPF> [#F02a]
    codigo_municipio: int = int()  # :: <cMun> [#F07]
    complemento: str = str()  # :: <xCpl> [#F05]
    logradouro: str = str()  # :: <xLgr> [#F03]
    municipio: str = str()  # :: <xMun> [#F08]
    nro: str = str()  # :: <nro> [#F04]
    uf: str = str()  # :: <UF> [#F09]


class ICMS(object):  # [#N01]
    icms00: ICMS00 = ICMS00()  # Tributada integralmente. :: <ICMS00> [#N02]


class ICMS00(object):  # [#N02]
    aliquota: Decimal = Decimal()  # :: <pICMS> [#N16]
    cst: int = int()  # :: <CST> [#N12]
    modalidade_base_calculo: int = int()  # 0=Margem Valor Agregado (%); 1=Pauta (Valor);  2=Preço Tabelado Máx. (valor); 3=Valor da operação. :: <CST> [#N13]
    origem: int = int()  # Origem da mercadoria. 0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8; 1 - Estrangeira - Importação direta, exceto a
    # indicada no código 6; 2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7; 3 - Nacional, mercadoria ou bem com Conteúdo de
    # Importação superior a 40% e inferior ou igual a 70%; 4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de
    # que tratam as legislações citadas nos Ajustes; 5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%; 6 - Estrangeira -
    # Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural; 7 - Estrangeira - Adquirida no mercado interno, sem similar nacional,
    # constante lista CAMEX e gás natural. 8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%; :: <ICMS00> [#N11]
    valor_base_calculo: Decimal = Decimal()  # :: <vBC> [#N15]
    valor_icms: Decimal = Decimal()  # :: <vlICMS> [#N17]


class ICMS10(ICMS00):  # [#N03]
    aliquota_st: Decimal = Decimal()  # :: <pICMSST> [#N22]
    cst: int = 10  # :: <CST> [#N12]
    modalidade_base_calculo_st: int = int()  # 0=Preço tabelado ou máximo sugerido; 1=Lista Negativa (valor); 2=Lista Positiva (valor); 3=Lista Neutra (valor);
    # 4=Margem Valor Agregado (%); 5=Pauta (valor); :: <modBCST> [#N18]
    mva_st: Decimal = Decimal()  # Percentual da margem de valor Adicionado do ICMS ST :: <pMVAST> [#N19]
    reducao_base_calculo_st: Decimal = Decimal()  # Percentual da Redução de BC do ICMS ST :: <pRedBCST> [#N20]
    valor_base_calculo_st: Decimal = Decimal()  # :: <vBCST> [#N21]
    valor_icms_st: Decimal = Decimal()  # :: <vlICMSST> [#N23]


class ICMS20(ICMS00):  # [#N04]
    cst: int = 20  # :: <CST> [#N12]
    motivo_icms_desonerado: str = str()  # Informar o motivo da desoneração: 3=Uso na agropecuária; 9=Outros; 12=Órgão de fomento e desenvolvimento
    # agropecuário. :: <motDesICMS> [#N28]
    valor_icms_desonerado: Decimal = Decimal()  # :: <vICMSDeson> [#N27a]


class IDe(object):  # [#B01]
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
    ind_presenca: int = int()  # Indicador de presença dp comprador. 0=Não se aplica (por exemplo, Nota Fiscal complementar ou de ajuste); 1=Operação presencial; 2=Operação não presencial, pela Internet; 3=Operação não presencial, Teleatendimento; 4=NFC-e em operação com entrega a domicílio; 9=Operação não presencial,  outros. :: <indPres> [#B25b]
    modelo: int = 55  # Código do Modelo do DFe. 55=NFe; 65=NFCe <mod> [#B06]
    municipio: int = int()  # Código do Município de Ocorrência <cMunFG> [#B12]
    nat_operacao: str = str()  # Descrição da Natureza da Operação :: <natOp> [#B04]
    nf: int = int()  # Número do DFe <nNF> [#B08]
    processo_emissao: int = int()  # Processo de emissão da NF-e. 0=Emissão de NF-e com aplicativo do contribuinte; 1=Emissão de NF-e avulsa pelo Fisco; 2=Emissão de NF-e avulsa, pelo contribuinte com seu certificado digital, através do site do Fisco; 3=Emissão NF-e pelo contribuinte com aplicativo fornecido pelo Fisco. :: <procEmi> [#B26]
    serie: int = int()  # Série do DFe <serie> [#B07]
    tipo_ambiente: int = int()  # Identificação do ambiente 1=Produção/2=Homologação :: <tpAmb> [#B24]
    tipo_emissao: int = 1  # Tipo de Emissão do DFe 1=Emissão normal (não em contingência); 2=Contingência FS-IA, com impressão do DANFE em formulário de segurança; 3=Contingência SCAN (Sistema de Contingência do Ambiente Nacional); 4=Contingência DPEC (Declaração Prévia da Emissão em Contingência); 5=Contingência FS-DA, com impressão do DANFE em formulário de segurança; 6=Contingência SVC-AN (SEFAZ Virtual de Contingência do AN); 7=Contingência SVC-RS (SEFAZ Virtual de Contingência do RS); 9=Contingência off-line da NFC-e (as demais opções de contingência são válidas também para a NFC-e). Para a NFC-e somente estão disponíveis e são válidas as opções de contingência 5 e 9. :: <tpEmis> [#B22]
    tipo_impressao: int = 1  # Formato de Impressão do DANFE  <tpImp> [#B21]
    tipo_nf: int = int()  # Tipo de operação. 0=Entrada; 1=Saída :: <tpNF> [#B11]
    uf: str = str()  # Código da UF do emitente do DFe :: <cUF> [#B02]
    versao_processo: str = str()  # Versão do Processo de emissão da NF-e :: <verProc> [#B27]


class Imposto(object):  # [#M01]
    total_tributos: Decimal = Decimal()  # Valor aproximado total de tributos federais, estaduais e municipais. :: <vTotTrib> [#M02]
    icms: ICMS = ICMS()  # Informações do ICMS da Operação própria e ST. :: <icms> [#N01]


class InfNFe(object):  # [#A01]
    destinatario: Destinatario = Destinatario()  # Identificação do Destinatário da NF-e  :: <dest> [#E01]
    detalhamento: Detalhamento = Detalhamento()  # Detalhamento de Produtos e Serviços :: <det> [#H01]
    emitente: Emitente = Emitente()  # Identificação do emitente da NF-e :: <emit> [#C01]
    entrega: EntregaRetirada = EntregaRetirada()  # Identificação do Local de entrega. Informar somente se diferente do endereço
    # destinatário. :: <entrega> [#F01]
    ide: IDe = IDe()  # Identificação da NFe :: <ide> [#B01]
    id: str = str()  # Cheve NFe precedida da literal 'NFe' :: @Id [#A03]
    retirada: EntregaRetirada = EntregaRetirada()  # Identificação do Local de retirada. Informar somente se diferente do endereço do
    # remetente. :: <retirada> [#F01]
    versao: str = str()  # Versão do layout NFe :: @versao [#A02]


class NFeReferenciada(object):  # [#BA03]
    cnpj: int = int()  # CNPJ do Emitente. :: <CNPJ> [#BA06]
    emissao: date = None  # Ano e Mês da emissão no formato AAMM :: <AAMM> [#BA05]
    modelo: int = int()  # Modelo do documento fiscal :: <mod> [#BA07]
    nf: int = int()  # Número do documento fiscal :: <nNF> [#BA09]
    serie: int = int()  # Série do documento fiscal :: <serie> [#BA08]
    uf: str = str()  # Código da UF do emitente :: <cUF> [#BA04]


class NFeReferenciadaProdutoRural(object):  # [#BA10]
    cnpj: int = int()  # CNPJ do Emitente :: <CNPJ> [#BA13]
    cpf: int = int()  # CPF do Emitente :: <CPF> [#BA14]
    cte_referenciada: int = int()  # Chave de acesso do CT-e referenciada  :: <refCTe> [#BA19]
    emissao: date = None  # Ano e Mês da emissão no formato AAMM :: <AAMM> [#BA12]
    inscricao_estadual: int = int()  # IE do Emitente :: <IE> [#BA15]
    modelo: int = int()  # Modelo do documento fiscal :: <mod> [#BA16]
    nf: int = int()  # Número do documento fiscal :: <nNF> [#BA18]
    serie: int = int()  # Série do documento fiscal :: <serie> [#BA17]
    uf: str = str()  # Código da UF do emitente :: <cUF> [#BA11]


class Produto(object):  # [#I01]
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
