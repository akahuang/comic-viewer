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
    if result.ok:
        return render_template('result.html', query=query, result=result)
    else:
        return render_template('error.html', query=query, error_msg=result.error_msg)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_msg='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_msg='Internal Server Error'), 500


def main(argv=sys.argv[:]):
    app.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())

