#!/usr/bin/python
#  -*- coding: utf-8 -*-
import excecoes
import lxml.etree
import datetime
import hashlib
import cStringIO
import gluon
import lpfx.tissV3_02_01 as tiss


def banco():
    return gluon.current.db


class CriarXML(object):
    def __init__(self, guias, prestador, registro_ans):
        if not isinstance(guias, list):
            raise TypeError("Guias não é uma lista!")
        db = banco()
        self.guias = guias
        self.prestador = db.prestador(prestador)
        self.registro_ans = registro_ans

    def __call__(self):
        db = banco()
        id_lote = db.lote.insert()
        for guia in self.guias:
            db.lote_guia.insert(id_lote=id_lote, id_guia=guia)
        xml_str = self.pegarXML(lote=id_lote)
        return xml_str

    def criar_guias(self):
        db = banco()
        lista_guias = []
        for id_guia in self.guias:
            guia = db.guiaConsulta(id_guia)
            ben = db.beneficiario(guia.beneficiario)
            cont = db.prestador(guia.contratado)
            prof = db.prestador_profissional(guia.profissional)
            obj_guia = tiss.ctm_consultaGuia(
                cabecalhoConsulta=tiss.ct_guiaCabecalho(registroANS=guia.registroANS,
                                                        numeroGuiaPrestador=guia.numeroGuiaPrestador),
                numeroGuiaOperadora=guia.numeroGUiaOperadora or None,
                dadosBeneficiario=tiss.ct_beneficiarioDados(
                    numeroCarteira=ben.numeroCarteira,
                    atendimentoRN='S' if ben.atendimentoRN else 'N',
                    nomeBeneficiario=ben.nomeBeneficiario,
                    numeroCNS=ben.numeroCNS,
                    identificadorBeneficiario=ben.identificadorBeneficiario,
                ),
                contratadoExecutante=tiss.contratadoExecutante(
                    cnpjContratado=cont.CNPJ,
                    nomeContratado=cont.nome,
                    CNES=cont.CNES
                ),
                profissionalExecutante=tiss.ct_contratadoProfissionalDados(
                    nomeProfissional=prof.nome,
                    conselhoProfissional=prof.conselho,
                    numeroConselhoProfissional=prof.numeroConselho,
                    UF=prof.UF,
                    CBOS=prof.CBOS
                ),
                indicacaoAcidente=str(guia.indicacaoAcidente),
                dadosAtendimento=tiss.ctm_consultaAtendimento(
                    dataAtendimento=guia.dataAtendimento,
                    tipoConsulta=guia.tipoConsulta,
                    procedimento=tiss.procedimento(
                        codigoTabela=guia.codigoTabela,
                        codigoProcedimento=guia.codigoProcedimento,
                        valorProcedimento=str(guia.valorProcedimento)
                    )
                ),
                observacao=guia.observacao or None,
                assinaturaDigitalGuia=None
            )
            lista_guias.append(obj_guia)
        return lista_guias

    def pegarXML(self, lote):
        pre = self.prestador
        conteudo_xml = tiss.mensagemTISS(
            cabecalho=tiss.cabecalhoTransacao(
                identificacaoTransacao=tiss.identificacaoTransacao(
                    tipoTransacao="ENVIO_LOTE_GUIAS",
                    sequencialTransacao=str(lote),
                    dataRegistroTransacao=datetime.date.today(),
                    horaRegistroTransacao=datetime.datetime.now().time().strftime("%H:%M:%S")
                ),
                origem=tiss.origem(
                    identificacaoPrestador=tiss.identificacaoPrestador(
                        codigoPrestadorNaOperadora=pre.codigoPrestadorNaOperadora,
                        CNPJ=None if pre.codigoPrestadorNaOperadora else pre.CNPJ or None,
                        CPF=None if (pre.codigoPrestadorNaOperadora or pre.CNPJ) else pre.CPF or None
                    ),
                ),
                destino=tiss.destino(
                    identificacaoPrestador=tiss.identificacaoPrestador(
                        CNPJ=pre.CNPJ or None,
                        CPF=pre.CPF or None,
                        codigoPrestadorNaOperadora=None
                    ),
                    registroANS=None if (pre.CNPJ or pre.CPF) else self.registro_ans,
                ),
                versaoPadrao="3.02.01"
            ),
            prestadorParaOperadora=tiss.prestadorOperadora(
                loteGuias=tiss.ctm_guiaLote(
                    numeroLote=str(lote),
                    guiasTISS=tiss.guiasTISS(guiasMedicas=self.criar_guias())

                )
            ),
            epilogo=tiss.epilogo(
                hash=''
            )
        )
        tiss_hash = hashlib.md5()
        string_tiss = cStringIO.StringIO()
        conteudo_xml.export(string_tiss, 1)
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        obj_xml = lxml.etree.XML(string_tiss.getvalue(), parser=parser)
        string_tiss.close()
        conteudo_xml = lxml.etree.tostring(obj_xml, method="text")
        tiss_hash.update(conteudo_xml)
        # Colocar a hash dentro do xml
        obj_xml[2][0].text = tiss_hash.hexdigest()
        return lxml.etree.tostring(obj_xml, encoding="utf-8", xml_declaration=True, pretty_print=True)
