#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
from flask import Flask, request, render_template
from parse_html import parse_html

app = Flask(__name__)
app.debug = True
app.secret_key = 'lala development key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result/', methods=['GET'])
def result():
    query = request.args.get('query', '')
    result = parse_html(query)
    return render_template('result.html', query=query, result=result)

def main(argv=sys.argv[:]):
    app.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())

