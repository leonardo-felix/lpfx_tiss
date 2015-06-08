# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('LPFX TISS'),
                  _class="navbar-brand", _href="http://lpfx.com.br")
response.title = "LPFX TISS"
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Leonardo Pires Felix <leonardo@piresfelix.com>'
response.meta.description = 'LPFX TISS, criador XML padrão TISS ANS'
response.meta.keywords = 'TISS, ANS, LPFX'

## your http://google.com/analytics id
response.google_analytics_id = None


response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]


if "auth" in locals(): auth.wikimenu()
