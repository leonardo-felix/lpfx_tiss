# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

from lpfx.integracao import CriarXML


def index():
    return dict()


def beneficiario():
    grid = SQLFORM.grid(db.beneficiario,
                        user_signature=False)  # TODO: Remover em produção, somente permitir para logados
    return dict(grid=grid)


def guia():
    grid = SQLFORM.grid(db.guiaConsulta,
                        user_signature=False)  # TODO: Remover em produção, somente permitir para logados
    return dict(grid=grid)


def prestador():
    grid = SQLFORM.smartgrid(db.prestador,
                             user_signature=False)  # TODO: Remover em produção, somente permitir para logados
    return dict(grid=grid)


def gerar_xml():
    form = SQLFORM.factory(
        Field("registro_ans", length=6, notnull=True, requires=IS_LENGTH(6, 6)),
        Field("guias", "list:reference guiaConsulta", notnull=True, required=True,
              requires=IS_IN_DB(db, db.guiaConsulta.id, "%(numeroGuiaPrestador)s", multiple=True))
    )
    if form.process().accepted:
        fake_prestador = 1  # será o login do prestador ativo posteriormente
        b = CriarXML(form.vars.guias, prestador=fake_prestador, registro_ans=form.vars.registro_ans)
        xml = b()
        response.headers['Content-Type'] = 'text/xml'
        return xml
    return dict(grid=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


