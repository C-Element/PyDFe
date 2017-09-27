from collections import OrderedDict

from xmltodict import parse as x2d_parse
from datetime import datetime

from decimal import Decimal

from documento.dfe import DestinatarioEmitente, ErroDeInicializacao, DocumentoInvalido, InfNFe


class NFe(object):
    infNFe: InfNFe = InfNFe()


#######################
class NFeOld(object):
    # NFe Attributes
    _chave_nfe: int = 0
    _destinatario: DestinatarioEmitente = DestinatarioEmitente()
    _emitente: DestinatarioEmitente = DestinatarioEmitente()
    _emissao: datetime = datetime.now()
    _motivo: str = ''
    _numero: int = 0
    _status: int = 0
    _total: Decimal = Decimal()
    _versao: str = ''

    _time_format: str = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, xml_str: str = None, xml_file: str = None):
        self._xml_content = xml_str
        self._xml_file = xml_file

        if xml_str is None and xml_file is None:
            raise ErroDeInicializacao('xml_str or xml_file need be informed.')
        elif xml_str is not None:
            self._fill_by_content()
        else:
            self._fill_by_file()

    def _fill_by_content(self):
        s_nfe_proc = 'nfeProc'
        s_versao = '@versao'
        s_nfe = 'NFe'
        s_prot_nfe = 'protNFe'
        xml_dict = x2d_parse(self._xml_content)

        if s_nfe_proc not in xml_dict.keys():
            self.raise_error('nfeProc')
        nfe_proc = xml_dict[s_nfe_proc]
        if s_versao not in nfe_proc.keys():
            self.raise_error(s_versao)
        if s_nfe not in nfe_proc.keys():
            self.raise_error(s_nfe)
        if s_prot_nfe not in nfe_proc.keys():
            self.raise_error(s_prot_nfe)
        self._versao = nfe_proc[s_versao]
        self._fill_nfe(nfe_proc[s_nfe])
        self._fill_proto_nfe(nfe_proc[s_prot_nfe])

    def _fill_by_file(self):
        file_open = open(self._xml_file)
        self._xml_content = file_open.read()
        file_open.close()
        self._fill_by_content()

    def _fill_nfe(self, nfe_dict: OrderedDict):
        s_nfe = 'NFe.'
        s_inf_nfe = 'infNFe'
        s_dest = 'dest'
        s_emit = 'emit'
        s_ide = 'ide'
        s_total = 'total'
        s_icms_tot = 'ICMSTot'
        s_vnf = 'vNF'
        if s_inf_nfe not in nfe_dict.keys():
            self.raise_error(s_nfe + s_inf_nfe)
        content = nfe_dict[s_inf_nfe]
        if s_dest not in content.keys():
            self.raise_error(s_nfe + s_dest)
        if s_emit not in content.keys():
            self.raise_error(s_nfe + s_emit)
        if s_ide not in content.keys():
            self.raise_error(s_nfe + s_ide)
        if s_total not in content.keys():
            self.raise_error(s_nfe + s_total)
        total = content[s_total]
        if s_icms_tot not in total.keys():
            self.raise_error(s_nfe + s_icms_tot)
        icms_tot = total[s_icms_tot]
        if s_vnf not in icms_tot.keys():
            self.raise_error(s_nfe + s_vnf)
        self._total = Decimal(icms_tot[s_vnf])
        self._fill_dest(content[s_dest])
        self._fill_emit(content[s_emit])
        self._fill_ide(content[s_ide])

    def _fill_dest(self, dest_dict: OrderedDict):
        s_dest = 'Destinatario.'
        s_cnpj = 'CNPJ'
        s_xnome = 'xNome'
        s_ender_dest = 'enderDest'
        s_uf = 'UF'
        if s_cnpj not in dest_dict.keys():
            self.raise_error(s_dest + s_cnpj)
        if s_xnome not in dest_dict.keys():
            self.raise_error(s_dest + s_xnome)
        if s_ender_dest not in dest_dict.keys():
            self.raise_error(s_dest + s_ender_dest)
        content = dest_dict[s_ender_dest]
        if s_uf not in content.keys():
            self.raise_error(s_dest + s_uf)
        self._destinatario.cnpj = dest_dict[s_cnpj]
        self._destinatario.nome = dest_dict[s_xnome]
        self._destinatario.uf = content[s_uf]

    def _fill_emit(self, emit_dict: OrderedDict):
        s_emit = 'Emitente.'
        s_cnpj = 'CNPJ'
        s_xnome = 'xNome'
        s_ender_emit = 'enderEmit'
        s_uf = 'UF'
        if s_cnpj not in emit_dict.keys():
            self.raise_error(s_emit + s_cnpj)
        if s_xnome not in emit_dict.keys():
            self.raise_error(s_emit + s_xnome)
        if s_ender_emit not in emit_dict.keys():
            self.raise_error(s_emit + s_ender_emit)
        content = emit_dict[s_ender_emit]
        if s_uf not in content.keys():
            self.raise_error(s_emit + s_uf)
        self._emitente.cnpj = emit_dict[s_cnpj]
        self._emitente.nome = emit_dict[s_xnome]
        self._emitente.uf = content[s_uf]

    def _fill_ide(self, ide_dict: OrderedDict):
        s_ide = 'Ide.'
        s_nnf = 'nNF'
        s_dh_emi = 'dhEmi'
        if s_nnf not in ide_dict.keys():
            self.raise_error(s_ide + s_nnf)
        if s_dh_emi not in ide_dict.keys():
            self.raise_error(s_ide + s_dh_emi)
        self._numero = int(ide_dict[s_nnf])
        self._emissao = datetime.strptime(ide_dict[s_dh_emi][0:19], self._time_format)

    def _fill_proto_nfe(self, prot_nfe_dict: OrderedDict):
        s_prot_nfe = 'ProtNFe.'
        s_inf_prot = 'infProt'
        s_ch_nfe = 'chNFe'
        s_c_stat = 'cStat'
        s_x_motivo = 'xMotivo'
        if s_inf_prot not in prot_nfe_dict.keys():
            self.raise_error(s_prot_nfe + s_inf_prot)
        content = prot_nfe_dict[s_inf_prot]
        if s_ch_nfe not in content.keys():
            self.raise_error(s_prot_nfe + s_ch_nfe)
        if s_c_stat not in content.keys():
            self.raise_error(s_prot_nfe + s_c_stat)
        if s_x_motivo not in content.keys():
            self.raise_error(s_prot_nfe + s_x_motivo)
        self._chave_nfe = int(content[s_ch_nfe])
        self._motivo = content[s_x_motivo]
        self._status = int(content[s_c_stat])

    def raise_error(self, field, reason='not found!'):
        raise DocumentoInvalido(f'Field {field} {reason}')

    @property
    def chave_nfe(self) -> int:
        return self._chave_nfe

    @property
    def destinatario(self) -> DestinatarioEmitente:
        return self._destinatario

    @property
    def emitente(self) -> DestinatarioEmitente:
        return self._emitente

    @property
    def emissao(self) -> datetime:
        return self._emissao

    @property
    def motivo(self) -> str:
        return self._motivo

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def status(self) -> int:
        return self._status

    @property
    def total(self) -> Decimal:
        return self._total

    @property
    def versao(self) -> str:
        return self._versao
