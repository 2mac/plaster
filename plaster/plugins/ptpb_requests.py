# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) [2015-08-06], ISC, [Ampling <post@ampling.com>]
#
########################################################################

import requests


def tell_form():
    '''Availability'''
    formula = {
            'text': 'yes', 
            'image': 'yes', 
            'tls': 'yes', 
            'time': 'yes', 
            'login': 'no'
            }
    return formula 

def tell_post(request_chain):
    '''alt plugin for ptpb'''
    try:
        url = request_chain['url']
        data = request_chain['data'] 
        time = request_chain['time']
        login = request_chain['login']
        payload = {'c': data}
        if time != 0:
            payload.update({'s': str(time)})
        r = requests.post(url, files=payload)
        response = {
                'link': r.content.decode("utf-8").rpartition(' ')[-1], 
                'code': r.status_code, 
                'reason': r.reason
                }
    except Exception as e:
        response = {'link': None, 'code': None, 'reason': e}
    finally:
        return response
