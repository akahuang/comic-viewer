#!/usr/bin/env python
# -*- coding: utf-8 -*
'''Input the comic url and return the list of the comic.'''

import sys
import re
import traceback
from urllib import urlencode
import lxml.html as HTML
from utils import retry_requests

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
        traceback.print_exc()
        return QueryResult(False, err='Error occurs...' + e.__doc__)

def parse_sfacg(text):
    BASE_URL = 'http://comic.sfacg.com'

    # Find the javascript and get the content
    try:
        root = HTML.document_fromstring(text)
        js_list = root.xpath('head/script/@src')
        js_url = BASE_URL + filter(lambda x:x[-3:]=='.js', js_list)[0]
    except IndexError:
        return QueryResult(False, err='javascript file is not found')

    r = retry_requests(js_url)
    if r.ok is False:
        return QueryResult(False, err=r.error_msg)
    text = r.text.encode('utf8')

    # Get the image list
    urls_pattern = 'picAy\[\d+\] = "(.*?)"'
    urls = re.findall(urls_pattern, text)
    urls = [BASE_URL + url for url in urls]

    # Get the comic name
    name_pattern = 'comicName = "(.*?)"'
    name = re.findall(name_pattern, text)[0]

    # Get the links of prev/next chapter
    def _get_url(pattern):
        url = re.findall(pattern, text)[0]
        if 'javascript' in url:
            return None
        return urlencode({'query' : BASE_URL + url})

    prev_pattern = 'preVolume="(.*?)"'
    next_pattern = 'nextVolume="(.*?)"'
    prev_url = _get_url(prev_pattern)
    next_url = _get_url(next_pattern)

    comic_data = {
        'urls' : urls,
        'name' : name.decode('utf8'),
        'prev_url' : prev_url,
        'next_url' : next_url,
    }
    print type(name), type(prev_url), type(next_url)
    print (name), (prev_url), (next_url)
    return QueryResult(True, data=comic_data)



class QueryResult():
    """The object returned by parse_html function."""
    def __init__(self, ok, data={}, err=''):
        self.ok = ok
        self.data = data
        self.error_msg = err

    def __str__(self):
        if self.ok is True:
            return 'Status: OK ' + str(self.data)
        return 'Status: FAIL "{0}"'.format(self.error_msg)

def main(argv=sys.argv[:]):
    url = 'http://comic.sfacg.com/HTML/WDMM/001/'
    print parse_html(url)
    return 0

if __name__ == '__main__':
    sys.exit(main())

