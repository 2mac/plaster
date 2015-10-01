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
    time = 'no'
    nick = 'no'
    form = {'txt': txt, 'img': img, 'tls': tls, 'time': time, 'nick': nick}
    return form  

def post(url, data):
    '''alt plugin for clbin'''
    try:
        c_data = {'clbin': data}
        r = requests.post(url, c_data)
        link = r.content
        code = r.status_code
        reason = r.reason
        response = {'link': link, 'code': code, 'reason': reason} 
    except Exception as e:
        response = {'link': None, 'code': None, 'reason': e}
    finally:
        return response
