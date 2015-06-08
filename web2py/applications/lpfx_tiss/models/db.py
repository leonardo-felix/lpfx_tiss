# -*- coding: utf-8 -*-
from gluon import current

from gluon.contrib.appconfig import AppConfig
# once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

# Banco de dados
db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])


# Acessar somente os patterns definidos
response.generic_patterns = []

response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


# (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
# (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

# create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=True)

# configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

# configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


class PlaceHolder():
    def __init__(self, placeholder):
        self.placeholder = placeholder

    def __call__(self, field, value):
        return SQLFORM.widgets.string.widget(field,
                                             value,
                                             _placeholder=self.placeholder)
db.define_table("prestador",
                Field("nome", notnull=True),
                Field("ehpj", "boolean", notnull=True),
                Field("CNPJ", length=14),
                Field("CPF", length=11),
                Field("CNES", notnull=True, length=7),
                Field("codigoPrestadorNaOperadora", notnull=True, default="19018080000130", length=14))

db.define_table("prestador_profissional",
                Field("prestador", db.prestador, notnull=True, readable=False, writable=False),
                Field("nome", length=70),
                Field("conselho", "integer", requires=IS_IN_SET({1: "CRAS - Conselho Regional de Assistência Social",
                                                                 2: "COREN - Conselhor Regional de Enfermagem",
                                                                 3: "CRF - Conselho Regional de Farmácia",
                                                                 4: "CRFA - Conselho Regional de Fonoaudiologia",
                                                                 5: "CREFITO - Conselho Regional de Fisioterapia e Terapia Ocupacional",
                                                                 6: "CRM - Conselho Regional de Medicina",
                                                                 7: "CRN - Conselho Regional de Nutrição",
                                                                 8: "CRO - Conselho Regional de Odontologia",
                                                                 9: "CRP - Conselho Regional de Psicologia",
                                                                 10: "Outros Conselhos"})),
                Field("numeroConselho", length=15),
                Field("UF", "integer", notnull=True,
                      requires=IS_IN_SET({11: "Rondônia - RO", 12: "Acre - AC", 13: "Amazonas - AM",
                                          14: "Roraima - RR", 15: "Pará - PA", 16: "Amapá - AP",
                                          17: "Tocantins - TO", 21: "Maranhão - MA", 22: "Piauí - PI",
                                          23: "Ceará - CE", 24: "Rio Grande do Norte - RN",
                                          25: "Paraíba - PB", 26: "Pernambuco - PE",
                                          27: "Alagoas - AL", 28: "Sergipe - SE", 29: "Bahia - BA",
                                          31: "Minas Gerais - MG", 32: "Espírito Santo - ES",
                                          33: "Rio de Janeiro - RJ", 35: "São Paulo - SP",
                                          41: "Paraná - PR", 42: "Santa Catarina - SC",
                                          43: "Rio Grande do Sul - RS", 50: "Mato Grosso do Sul - MS",
                                          51: "Mato Grosso - MT", 52: "Goiás - GO",
                                          53: "Distrito Federal - DF", 98: "Países Estrangeiros"})),
                Field("CBOS", "integer", requires=IS_IN_SET({201115: "Geneticista",
                                                             203015: "Pesquisador em biologia de microorganismos e parasitas"})))

db.define_table("beneficiario",
                Field('numeroCarteira', notnull=True, length=20, label="Numero carteira",
                      widget=PlaceHolder("123456"),
                      requires=IS_EXPR("value.isdigit()",
                                       error_message="Valor não é somente números")),
                Field('atendimentoRN', "boolean", notnull=True, label="Atendimento em RN"),
                Field('nomeBeneficiario', notnull=True, length=70, label="Nome do beneficiário",
                      widget=PlaceHolder("Nome")),
                Field('numeroCNS', length=15, label="Numero CNS", widget=PlaceHolder("123456"),
                      requires=IS_NULL_OR(IS_EXPR("value.isdigit()", error_message="Valor não é somente números"))),
                Field('identificadorBeneficiario', label="Identificador Beneficiário"))


db.define_table("guiaConsulta",
                Field("registroANS", notnull=True, length=6, label="Registro da ANS",
                      requires=IS_EXPR("value.isdigit()", error_message="Valor não é somente números")),
                Field("numeroGuiaPrestador", notnull=True, length=20, label="Nº Guia Prestador"),
                Field("numeroGUiaOperadora", length=20, label="Nº Guia Operadora"),
                Field("beneficiario", db.beneficiario, notnull=True, label='Beneficiário',
                      requires=IS_IN_DB(db, db.beneficiario.id, "%(nomeBeneficiario)s")),
                Field("contratado", db.prestador, notnull=True, label="Contratado executor",
                      requires=IS_IN_DB(db, db.prestador.id, "%(nome)s")),
                Field("profissional", db.prestador_profissional, notnull=True, label="Profissional Executante",
                      requires=IS_IN_DB(db, db.prestador_profissional.id, "%(nome)s - %(numeroConselho)s")),
                Field("indicacaoAcidente", "integer", label="Indicação de Acidente", notnull=True,
                      requires=IS_IN_SET({0: "Trabalho", 1: "Trânsito", 2: "Outros Acidentes", 9: "Não Acidentes"})),
                Field("dataAtendimento", "date", notnull=True, label="Data do atendimento"),
                Field("tipoConsulta", "integer", notnull=True, requires=IS_IN_SET({1: "Primeira",
                                                                                   2: "Seguimento",
                                                                                   3: "Pré-Natal",
                                                                                   4: "Por encaminhamento"})),
                Field("codigoTabela", length=2, notnull=True, requires=IS_IN_SET({"18": "TUSS - Taxas hospitalares, diárias e gases medicinais",
                                                                                  "19": "TUSS - Materiais",
                                                                                  "20": "TUSS - Medicamentos",
                                                                                  "22": "TUSS - Procedimentos e eventos em saúde (medicina, odonto e demais áreas de saúde)",
                                                                                  "90": "Sem descrição",
                                                                                  "98": "Sem descrição",
                                                                                  "00": "Tabela Própria das Operadoras"})),
                Field("codigoProcedimento", length=10, notnull=True, label="Código Procedimento"),
                Field("valorProcedimento", "decimal(8,2)", notnull=True, label="Valor procedimento", widget=SQLFORM.widgets.decimal.widget),
                Field("observacao", "text", length=500)
                )

db.define_table("lote",
                Field("data_hora", "datetime", notnull=True, default=request.now))

db.define_table("lote_guia",
                Field("id_lote", db.lote, notnull=True),
                Field("id_guia", db.guiaConsulta, notnull=True))

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

current.db = db