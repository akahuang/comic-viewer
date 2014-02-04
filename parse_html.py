#!/usr/bin/env python
# -*- coding: utf-8 -*
'''Input the comic url and return the list of the comic.'''

import sys
import re
import requests
import lxml.html as HTML

def parse_html(url):
    '''The delegator function.'''
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        return QueryResult(False, 'Error:{0}{1}'.format(r.status_code, r.reason))

    if 'sfacg' in url:
        return parse_sfacg(r.text)
    return QueryResult(False, 'The url is not supported comic website')

def parse_sfacg(text):
    BASE_URL = 'http://comic.sfacg.com'

    # Find the javascript
    root = HTML.document_fromstring(text)
    js_list = root.xpath('head/script/@src')
    js_url = BASE_URL + filter(lambda x:x[-3:]=='.js', js_list)[0]

    # Get the image list
    r = requests.get(js_url)
    if r.status_code != requests.codes.ok:
        return QueryResult(False, 'Error:{0}{1}'.format(r.status_code, r.reason))
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
        return 'Status: FAIL ' + self.error_msg

def main(argv=sys.argv[:]):
    url = 'http://comic.sfacg.com/HTML/WDMM/001/'
    print parse_html(url)
    return 0

if __name__ == '__main__':
    sys.exit(main())

