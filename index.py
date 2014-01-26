#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
from flask import Flask
from flask import render_template
from Forms import SearchBarForm

app = Flask(__name__)
app.debug = True
app.secret_key = 'lala development key'

@app.route('/')
def index():
    form = SearchBarForm()
    print 'TEST: ', form.query.label
    return render_template('index.html', form=form)

def main(argv=sys.argv[:]):
    app.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())

