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

    # Determine the comic website
    if 'sfacg' in url:
        parse_func = parse_sfacg
    elif 'comicvip' in url:
        parse_func = parse_8comic
    elif '99770' in url:
        parse_func = parse_99770
    else:
        return QueryResult(False, err='The url is not supported comic website')

    # Parse the html
    try:
        r = retry_requests(url)
        if r.ok is False:
            return QueryResult(False, err=r.error_msg)
        return parse_func(r)
    except Exception as e:
        traceback.print_exc()
        return QueryResult(False, err='Error occurs...' + e.__doc__)

def parse_sfacg(r):
    BASE_URL = 'http://comic.sfacg.com'
    text = r.text

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
        return BASE_URL + url

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
    return QueryResult(True, data=comic_data)

def parse_8comic(r):
    text = r.text

    # Retrive the importent variable
    ch_pattern = 'ch=(\d*)'
    ch = re.findall(ch_pattern, r.url)[0]
    item_id_pattern = 'var itemid=(\d*?);'
    item_id = re.findall(item_id_pattern, text)[0]
    allcodes_pattern = 'var allcodes="(.*?)";'
    allcodes  = re.findall(allcodes_pattern, text)[0]

    # Get the current num and the num list
    nums = []
    links = allcodes.split('|')
    for link in links:
        objs = link.split(' ')
        temp_num = objs[0]
        nums.append(temp_num)
        if temp_num == ch:
            num, sid, did, pages, code = link.split(' ')
            idx = len(nums) - 1

    # Generate comic url list
    urls = []
    for page in range(1, int(pages) + 1):
        m = ((page-1)/10)%10 + (((page-1)%10)*3)
        img = '%03d_%s' % (page, code[m:m+3])
        url = "http://img%s.8comic.com/%s/%s/%s/%s.jpg" % (sid, did, item_id, num, img)
        urls.append(url)

    # Generate prev/next url
    prev_num = nums[idx-1] if idx > 0 else None
    next_num = nums[idx+1] if idx < len(nums) else None
    print prev_num, next_num
    pattern = re.compile('ch=\d*')
    prev_url = pattern.sub('ch={0}'.format(prev_num), r.url) if prev_num else None
    next_url = pattern.sub('ch={0}'.format(next_num), r.url) if next_num else None
    print prev_url, next_url

    comic_data = {
        'urls' : urls,
        'name' : 'Untitled',
        'prev_url' : prev_url,
        'next_url' : next_url,
    }
    return QueryResult(True, data=comic_data)

#   name_pattern = '<title>(.*?)</title>'
#   name = re.findall(name_pattern, text)[0]

def parse_99770(r):
    BASE_DOMAINS = 'http://58.215.241.39:9728/dm01/|http://58.215.241.39:9728/dm02/|http://58.215.241.39:9728/dm03/|http://58.215.241.206:9728/dm04/|http://58.215.241.39:9728/dm05/|http://58.215.241.39:9728/dm06/|http://58.215.241.39:9728/dm07/|http://58.215.241.39:9728/dm08/|http://58.215.241.206:9728/dm09/|http://58.215.241.39:9728/dm10/|http://58.215.241.39:9728/dm11/|http://58.215.241.206:9728/dm12/|http://58.215.241.39:9728/dm13/|http://173.231.57.238/dm14/|http://58.215.241.206:9728/dm15/|http://142.4.34.102/dm16/'.split('|')
    text = r.text

    urls_pattern = 'var sFiles="(.*?)";'
    urls = re.findall(urls_pattern, text)[0].split('|')
    spath_pattern = 'var sPath="(\d*)"'
    spath = int(re.findall(spath_pattern, text)[0]) - 1
    urls = [BASE_DOMAINS[spath] + url for url in urls]

    comic_data = {
        'urls' : urls,
        'name' : 'untitled',
        'prev_url' : None,
        'next_url' : None,
    }
    return QueryResult(True, data=comic_data)

class QueryResult():
    """The object returned by parse_html function."""
    def __init__(self, ok, data={}, err=''):
        self.ok = ok
        if self.ok:
            self.data = data
            self.data['prev_url'] = self.generate_query_url(self.data['prev_url'])
            self.data['next_url'] = self.generate_query_url(self.data['next_url'])
        else:
            self.error_msg = err

    def generate_query_url(self, url):
        return urlencode({'query' : url}) if url is not None else None

    def __str__(self):
        if self.ok is True:
            return 'Status: OK ' + str(self.data)
        return 'Status: FAIL "{0}"'.format(self.error_msg)

def main(argv=sys.argv[:]):
#   url = 'http://comic.sfacg.com/HTML/WDMM/001/'
#   url = 'http://new.comicvip.com/show/cool-7340.html?ch=23'
    url = 'http://mh.99770.cc/comic/6643/141228/'
    print parse_html(url)
    return 0

if __name__ == '__main__':
    sys.exit(main())

