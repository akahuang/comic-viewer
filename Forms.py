#!/usr/bin/env python
# -*- coding: utf-8 -*
'''Implement every forms.'''

from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired

WTF_CSRF_SECRET_KEY = 'lala random string.'

class SearchBarForm(Form):
    '''The search bar form.'''

    query = TextField('query', validators=[DataRequired()])
