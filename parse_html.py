#!/usr/bin/env python
# -*- coding: utf-8 -*
'''Input the comic url and return the list of the comic.'''

import sys
import re
from utils import retry_requests
import lxml.html as HTML

def parse_html(url):
    '''The delegator function.'''
    try:
        r = retry_requests(url)
        if r.ok is False:
            return QueryResult(False, err=r.error_msg)

        if 'sfacg' in url:
            return parse_sfacg(r.text)
        return QueryResult(False, err='The url is not supported comic website')
    except Exception as e:
        return QueryResult(False, err='Error occurs...' + e.__doc__)

def parse_sfacg(text):
    BASE_URL = 'http://comic.sfacg.com'

    # Find the javascript
    try:
        root = HTML.document_fromstring(text)
        js_list = root.xpath('head/script/@src')
        js_url = BASE_URL + filter(lambda x:x[-3:]=='.js', js_list)[0]
    except IndexError:
        return QueryResult(False, err='javascript file is not found')

    # Get the image list
    r = retry_requests(js_url)
    if r.ok is False:
        return QueryResult(False, err=r.error_msg)
    re_pattern = 'picAy\[\d+\] = "(.*?)"'
    urls = re.findall(re_pattern, r.text.encode('utf8'))

    # Add base url
    urls = [BASE_URL + url for url in urls]
    return QueryResult(True, urls=urls)



class QueryResult():
    """The object returned by parse_html function."""
    def __init__(self, ok, urls=[], err=''):
        self.ok = ok
        self.urls = urls
        self.error_msg = err

    def __str__(self):
        if self.ok is True:
            return 'Status: OK ' + str(self.urls)
        return 'Status: FAIL "{0}"'.format(self.error_msg)

def main(argv=sys.argv[:]):
    url = 'http://comic.sfacg.com/HTML/WDMM/00111/'
    print parse_html(url)
    return 0

if __name__ == '__main__':
    sys.exit(main())

