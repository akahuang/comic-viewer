#!/usr/bin/env python
# -*- coding: utf-8 -*

import unittest
import parse_html

class TestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_html(self):
        pass

    def test_parse_sfacg_ok(self):
        ok_url = 'http://comic.sfacg.com/HTML/XFGJ/001j/'
        r = parse_html.parse_html(ok_url)
        self.assertTrue(r.ok)

    def test_parse_sfacg_fail(self):
        fail_url = 'http://comic.sfacg.com/HTML/XFGJ/001jsdf/'
        r = parse_html.parse_html(fail_url)
        self.assertFalse(r.ok)

    def test_parse_sfacg_head(self):
        head_url = 'http://comic.sfacg.com/HTML/XFGJ/001j/'
        r = parse_html.parse_html(head_url)
        self.assertIsNone(r.data['prev_url'])
        self.assertIsNotNone(r.data['next_url'])

    def test_parse_sfacg_name(self):
        ok_url = 'http://comic.sfacg.com/HTML/XFGJ/001j/'
        r = parse_html.parse_html(ok_url)
        self.assertEqual(unicode, type(r.data['name']))

    def test_parse_8comic_ok(self):
        ok_url = 'http://new.comicvip.com/show/cool-7340.html?ch=54'
        r = parse_html.parse_html(ok_url)
        self.assertTrue(r.ok)
