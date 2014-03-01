#!/usr/bin/env python
# -*- coding: utf-8 -*
'''Input the comic url and return the list of the comic.'''

import sys
import re
from flask import session
from urllib import urlencode
import lxml.html as HTML
from utils import retry_requests

def parse_html(url):
    '''The delegator function.'''

    # Determine the comic website
    if 'sfacg' in url:
        parser = SfacgParser()
    elif 'comicvip' in url:
        parser = Site8ComicParser()
    elif '99770' in url:
        parser = Site99770Parser()
    else:
        error_msg = '''
            The url is not supported comic website.
            Now the supported websites are sfacg, 8comic, and 99770.'''
        return QueryResult(False, err=error_msg)

    return parser.parse_url(url)


class ComicSiteParser(object):
    """Base class of parser """

    def __init__(self):
        self.urls = []
        self.name = u'Untitled'
        self.prev_url = None
        self.next_url = None

    def _request_data(self):
        '''Request the content of query_url and return the status'''
        self.url_response = retry_requests(self.query_url)
        return self.url_response.ok

    def _parse_data(self):
        pass

    def parse_url(self, url):
        '''Parse the url and return the comic list.'''
        self.query_url = url
        if not self._request_data():
            return QueryResult(False, err=self.url_response.error_msg)

        ret = self._parse_data()
        if ret is not None:
            return ret

        comic_data = {
            'urls' : self.urls,
            'name' : self.name.decode('utf8'),
            'prev_url' : self.prev_url,
            'next_url' : self.next_url,
        }
        return QueryResult(True, data=comic_data)


class SfacgParser(ComicSiteParser):
    """docstring for SfacgParser"""

    BASE_URL = 'http://comic.sfacg.com'

    def __init__(self):
        super(SfacgParser, self).__init__()

    def _parse_data(self):
        # Find the javascript and get the content
        try:
            text = self.url_response.text
            root = HTML.document_fromstring(text)
            js_list = root.xpath('head/script/@src')
            js_url = self.BASE_URL + filter(lambda x:x[-3:]=='.js', js_list)[0]
        except IndexError:
            return QueryResult(False, err='javascript file is not found')

        r = retry_requests(js_url)
        if r.ok is False:
            return QueryResult(False, err=r.error_msg)
        text = r.text.encode('utf8')

        # Get the image list
        urls_pattern = 'picAy\[\d+\] = "(.*?)"'
        urls = re.findall(urls_pattern, text)
        self.urls = [self.BASE_URL + comic_url for comic_url in urls]

        # Get the comic name
        name_pattern = 'comicName = "(.*?)"'
        self.name = re.findall(name_pattern, text)[0]

        # Get the links of prev/next chapter
        def _get_url(pattern):
            url = re.findall(pattern, text)[0]
            if 'javascript' in url:
                return None
            return self.BASE_URL + url

        prev_pattern = 'preVolume="(.*?)"'
        next_pattern = 'nextVolume="(.*?)"'
        self.prev_url = _get_url(prev_pattern)
        self.next_url = _get_url(next_pattern)


class Site8ComicParser(ComicSiteParser):
    """docstring for site"""

    def __init__(self):
        super(Site8ComicParser, self).__init__()

    def _request_data(self):
        try:
            ch_pattern = 'ch=(\d*)'
            self.ch = re.findall(ch_pattern, self.query_url)[0]
        except:
            self.ch = -1

        if 'url' in session and session['url'] == self.query_url.split('?')[0]:
            self.item_id = session['item_id']
            self.allcodes = session['allcodes']
        else:
            # Parse the html
            ok = super(Site8ComicParser, self)._request_data()
            if not ok:
                return False

            text = self.url_response.text
            item_id_pattern = 'var itemid=(\d*?);'
            self.item_id = re.findall(item_id_pattern, text)[0]
            allcodes_pattern = 'var allcodes="(.*?)";'
            self.allcodes  = re.findall(allcodes_pattern, text)[0]

            session['url'] = self.query_url.split('?')[0]
            session['item_id'] = self.item_id
            session['allcodes'] = self.allcodes
        return True

    def _parse_data(self):
        # Get the current num and the num list
        nums = []
        links = self.allcodes.split('|')
        for link in links:
            objs = link.split(' ')
            temp_num = objs[0]
            nums.append(temp_num)
            if temp_num == self.ch or (self.ch == -1 and len(nums) == 1):
                num, sid, did, pages, code = link.split(' ')
                idx = len(nums) - 1

        # Generate comic url list
        self.urls = []
        for page in range(1, int(pages) + 1):
            m = ((page-1)/10)%10 + (((page-1)%10)*3)
            img = '%03d_%s' % (page, code[m:m+3])
            url = "http://img%s.8comic.com/%s/%s/%s/%s.jpg" % (sid, did, self.item_id, num, img)
            self.urls.append(url)

        # Generate prev/next url
        print idx, len(nums)
        prev_num = nums[idx-1] if idx-1 >= 0 else None
        next_num = nums[idx+1] if idx+1 <= len(nums)-1 else None
        pattern = re.compile('ch=\d*')
        self.prev_url = pattern.sub('ch={0}'.format(prev_num), self.query_url) if prev_num else None
        self.next_url = pattern.sub('ch={0}'.format(next_num), self.query_url) if next_num else None


class Site99770Parser(ComicSiteParser):
    """docstring for Site99770Parser"""

    BASE_DOMAINS = 'http://58.215.241.39:9728/dm01/|http://58.215.241.39:9728/dm02/|http://58.215.241.39:9728/dm03/|http://58.215.241.206:9728/dm04/|http://58.215.241.39:9728/dm05/|http://58.215.241.39:9728/dm06/|http://58.215.241.39:9728/dm07/|http://58.215.241.39:9728/dm08/|http://58.215.241.206:9728/dm09/|http://58.215.241.39:9728/dm10/|http://58.215.241.39:9728/dm11/|http://58.215.241.206:9728/dm12/|http://58.215.241.39:9728/dm13/|http://173.231.57.238/dm14/|http://58.215.241.206:9728/dm15/|http://142.4.34.102/dm16/'.split('|')

    def __init__(self):
        super(Site99770Parser, self).__init__()

    def _parse_data(self):
        text = self.url_response.text
        urls_pattern = 'var sFiles="(.*?)";'
        urls = re.findall(urls_pattern, text)[0].split('|')
        spath_pattern = 'var sPath="(\d*)"'
        spath = int(re.findall(spath_pattern, text)[0]) - 1
        self.urls = [self.BASE_DOMAINS[spath] + comic_url for comic_url in urls]


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
    url = 'http://comic.sfacg.com/HTML/WDMM/001sdf/'
#   url = 'http://new.comicvip.com/show/cool-7340.html?ch=23'
#   url = 'http://mh.99770.cc/comic/6643/141228/'
    print parse_html(url)
    return 0

if __name__ == '__main__':
    sys.exit(main())

