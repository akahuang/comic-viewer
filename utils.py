#!/usr/bin/env python
# -*- coding: utf-8 -*
'''Several helper functions.'''

import requests
import time
import traceback

def retry_requests(url):
    '''Retry the requests and handle the exception.'''
    _RETRY_TIME = 3 
    _DELAY_TIME = 0.1

    if url == '':
        return None
    if url[:7] != 'http://':
        url = 'http://' + url

    for i in range(_RETRY_TIME):
        try:
            return requests.get(url)
        except:
            print 'Exception'#, traceback.format_exc()
        time.sleep(_DELAY_TIME)
    return None
