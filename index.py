#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
from flask import Flask, request, render_template
from Forms import SearchBarForm
from parse_html import parse_html

app = Flask(__name__)
app.debug = True
app.secret_key = 'lala development key'

@app.route('/')
def index():
    form = SearchBarForm()
    return render_template('index.html', form=form)

@app.route('/result/', methods=['GET'])
def result():
    query = request.args.get('query', '')
    form = SearchBarForm(query=query)
    result = parse_html(query)
    print '---- RESULT:' + str(result) + '----'
    return render_template('result.html', form=form, result=result)

def main(argv=sys.argv[:]):
    app.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())

