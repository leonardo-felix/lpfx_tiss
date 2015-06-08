#!/usr/bin/python
#  -*- coding: utf-8 -*-
import tissV3_02_01 as tiss
import os
import datetime
import cStringIO
import lxml.etree
import hashlib

conteudo_xml = tiss.mensagemTISS(
    cabecalho=tiss.cabecalhoTransacao(
        identificacaoTransacao=tiss.identificacaoTransacao(
            tipoTransacao="ENVIO_LOTE_GUIAS",
            sequencialTransacao='1',
            dataRegistroTransacao=datetime.date.today(),
            horaRegistroTransacao=datetime.datetime.now().time().strftime("%H:%M:%S")
        ),
        origem=tiss.origem(
            identificacaoPrestador=tiss.identificacaoPrestador(
                codigoPrestadorNaOperadora='99999999999999',
                CNPJ=None,
                CPF=None
            ),
        ),
        destino=tiss.destino(
            identificacaoPrestador=tiss.identificacaoPrestador(
                CNPJ='99999999999999',
                CPF=None,
                codigoPrestadorNaOperadora=None
            ),  # normalmente CNPJ
            registroANS=None,
        ),
        versaoPadrao="3.02.01"
    ),
    prestadorParaOperadora=tiss.prestadorOperadora(
        loteGuias=tiss.ctm_guiaLote(
            numeroLote='1',
            guiasTISS=tiss.guiasTISS(guiasMedicas=[
                tiss.ctm_consultaGuia(
                    cabecalhoConsulta=tiss.ct_guiaCabecalho(registroANS="999999",
                                                            numeroGuiaPrestador="2"),
                    numeroGuiaOperadora='1',
                    dadosBeneficiario=tiss.ct_beneficiarioDados(
                        numeroCarteira='00001',
                        atendimentoRN='S',
                        nomeBeneficiario='leonardo pires felix'.upper(),
                        numeroCNS=None,
                        identificadorBeneficiario=None,
                    ),
                    contratadoExecutante=tiss.contratadoExecutante(
                        cnpjContratado='99999999999999',
                        nomeContratado="leonardo pires felix - ME".upper(),
                        CNES='1123323'
                    ),
                    profissionalExecutante=tiss.ct_contratadoProfissionalDados(
                        nomeProfissional="SAUDE",
                        conselhoProfissional="2",
                        numeroConselhoProfissional="01",
                        UF="53",
                        CBOS='201115'
                    ),
                    indicacaoAcidente="0",
                    dadosAtendimento=tiss.ctm_consultaAtendimento(
                        dataAtendimento=datetime.date.today(),
                        tipoConsulta="1",
                        procedimento=tiss.procedimento(
                            codigoTabela="18",
                            codigoProcedimento="00000000",
                            valorProcedimento="2"
                        )
                    ),
                    observacao=None,
                    assinaturaDigitalGuia=None
                )
            ])

        )
    ),
    epilogo=tiss.epilogo(
        hash=''
    )
)
"""
NOME_ARQUIVO = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'arquivo.xml')
tiss_hash = hashlib.md5()


string_tiss = cStringIO.StringIO()
conteudo_xml.export(string_tiss, 1)
parser = lxml.etree.XMLParser(remove_blank_text=True)
obj_xml = lxml.etree.XML(string_tiss.getvalue(), parser=parser)
conteudo_xml = lxml.etree.tostring(obj_xml, method="text")
tiss_hash.update(conteudo_xml)
# Colocar a hash dentro do xml
obj_xml[2][0].text = tiss_hash.hexdigest()

arq_saida = open(NOME_ARQUIVO, 'w')
arq_saida.write(lxml.etree.tostring(obj_xml, encoding="utf-8", xml_declaration=True, pretty_print=True))
arq_saida.close()

print "XML gerado"
"""