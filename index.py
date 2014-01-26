#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, world.'

@app.route('/lala')
def lala():
    return 'Lala, this is my first web app.'
