#!/usr/bin/env python
# -*- coding: utf-8 -*
'''Several helper functions.'''

import requests
import time

class RequestStatus():
    '''Contain the request is ok or not.
    If the request is ok, then record the text.
    If not ok, then record the error message.'''

    def __init__(self, ok, message):
        self.ok = ok
        if self.ok is True:
            self.text = message
        else:
            self.error_msg = message


def retry_requests(url):
    '''Retry the requests and handle the exception.'''
    _RETRY_TIME = 3
    _DELAY_TIME = 0.1

    if url == '':
        return RequestStatus(False, 'The url is empty')
    if url[:7] != 'http://':
        url = 'http://' + url

    for i in range(_RETRY_TIME):
        try:
            r = requests.get(url)
            return RequestStatus(True, r.text)
        except Exception as e:
            error_msg = e.__doc__
            print 'Exception', e.__doc__
            time.sleep(_DELAY_TIME)
    return RequestStatus(False, error_msg)
