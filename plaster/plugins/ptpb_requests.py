# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) [2015-08-06], ISC, [Ampling <post@ampling.com>]
#
##############################################################################

import requests


def formula():
    '''Availability'''
    txt = 'yes'
    img = 'yes'
    tls = 'yes'
    time = 'yes'
    nick = 'no'
    form = {'txt': txt, 'img': img, 'tls': tls, 'time': time, 'nick': nick}
    return form 

def post(url, data):
    '''alt plugin for ptpb'''
    try:
        # r = requests.post(url, files={'file': open(data,'rb')})
        brick = {'c': open(data, 'rb')}
        r = requests.post(url, files=brick)
        # code = r.status_code
        # OK = r.status_code == requests.codes.ok
        link = r.content
        response = {'link': link} # 'code': code, 'reason': reason}
        return response
    except Exception as e:
        response = {'link': 'na', 'code': None, 'reason': e}
        return response
