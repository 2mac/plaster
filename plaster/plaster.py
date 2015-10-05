#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) [2015-08-06], ISC license, [Ampling <plaster@ampling.com>]
#
'''
 ____  __      __    ___  ____  ____  ____ 
(  _ \(  )    /__\  / __)(_  _)( ___)(  _ \
 )___/ )(__  /(__)\ \__ \  )(   )__)  )   /
(__)  (____)(__)(__)(___/ (__) (____)(_)\_)

Plaster is an adaptable command-line paste-bin client.
'''

import argparse
import configparser
from sys import stdin
from os import path, isatty, stat
from importlib.machinery import SourceFileLoader

try:
    import magic
    import_magic = True
except Exception as e:
    import_magic = False
    print('e:', e)

try:
    ## requires xclip
    import pyperclip
    import_pyperclip = True
except Exception as e:
    import_pyperclip = False
    print('e:', e)

version = '0.0.7'

config_dir = path.join(path.expanduser('~'), '.config', 'plaster')
config_file = path.join(config_dir, 'config')
prefix = path.join(config_dir, 'plugins')

#
# options
#

## simpler than than getopts
parser = argparse.ArgumentParser(description=
        'plaster v{}, a data sharing utility'.format(version))
parser.add_argument('content', default='', nargs='?',
        help='path to file', type=str)
parser.add_argument('-l', '--login', 
        help='attempts authentication', action='store_true')
parser.add_argument('-s', '--secure', 
        help='use only https', action='store_true')
parser.add_argument('-v', '--verbose', 
        help='increase verbosity', action='count')
parser.add_argument('-x', '--xclip', 
        help='copy link to clipboard', action='store_true')
parser.add_argument('-X', '--Xclip', 
        help='publish your clipboard; *risky', action='store_true')
parser.add_argument('-f', '--force', 
        help='force risky behavior', action='store_true')
parser.add_argument('-e', '--expiry', nargs='?', default=0, type=int,
        help='expiry time; default')
parser.add_argument('-m', '--manual', default=0,
        help="set media type or list and exit")
args = parser.parse_args()

#
# BEGIN helper functions 
#

def _config():
    '''
    Parse configuration file, from top to bottom.
    Configuration location should be adjustable.
    '''
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        ## Measures file size for helpful message.
        if stat(config_file).st_size == 0:
            print('e: configuration appears empty')
            print('try adding a section')
            exit(config_file)
        if config.sections() == []:
            print('e: configuration needs sections')
            print('try uncommenting a section')
            exit(config_file)
        if args.verbose:
            print('INFO: config:    [PASS]')
        return config
    except Exception as e: 
        print('ERROR: config    [FAIL]')
        print('e:' , e)
        exit(1)

def _inlet():
    '''Reads all, returns content in bytes.'''
    try:
        if args.content:
            content_path = args.content
        ## Optional clipboard feature. Requires xclip
        elif args.Xclip:
            if import_pyperclip == False:
                exit('e: missing python-pyperclip')
            if import_pyperclip == True:
                if not args.force:
                    print('plaster your clipboard for all to see?')
                    exit('add -f')
                elif args.force: 
                    content = bytes(pyperclip.paste(), 'utf-8')
                    content_path = None
        ## measures no arguments or options.
        elif isatty(0):
            print('enter a file to plaster')
            content_path = input('$ ')
        ## OK for now
        else: 
            content = stdin.buffer.read()
            content_path = None
        if content_path is not None:
            with open(str(content_path), 'rb') as i:
                content = i.read()
        return content
    except KeyboardInterrupt:
        print()
        exit('for help, try: plaster -h')
    except Exception as e:
        print('e: inlet:', e)
        exit(1)

def _sniff(content):
    media_types = ['image', 'text']
    if args.manual and args.manual not in media_types:
        print('list of media types:')
        print(media_types)
        exit(1)
    if args.manual and args.manual in media_types:
        content_type = args.manual
        return content_type
    if not args.manual:
        if import_magic == False:
            print('e: python-magic missing')
            exit('please install or use manual mode -m')
        if import_magic == True:
            content_type = (magic.from_buffer(content, mime=True)).decode('utf-8')
    return content_type

def _command(content_type):
    '''
    Composes a dictionary to match specified parameters.
    Returns a dictionary.
    '''
    try:
        if args.verbose == 2:
            print(content_type)
        if 'text' in content_type:
            command = {'text': 'yes'}
        elif 'image' in content_type:
            command = {'image': 'yes'}
        else:
            if not args.force:
                if not args.verbose == 2:
                    print(content_type)
                exit('e: untested media types requre -f')
            command = {'image': 'yes'}
        ## Add other content types here.
    except Exception as e:
        if args.verbose == 2:
            print('e:', e)
    try:
        if args.login:
            command.update({'login': 'yes'})
            if args.verbose:
                print('authentication mode enabled')
        if args.secure:
            command.update({'tls': 'yes'})
            if args.verbose:
                print('tls mode enabled')
        if args.expiry:
            command.update({'time': 'yes'})
            if args.verbose:
                print('ephemeral mode enabled') 
        return command
    except Exception as e:
        if args.verbose == 2:
            print('ERROR: command:', e)

def _cull(command, mark): 
    '''
    Accepts command as a dictionary and mark as it's starting point.
    Returns the name of a suitable paste-bin and mark as it's place 
    in the loop.
    '''
    sections = len(config.sections())
    for mark in range(mark, sections):
        try:
            name = config.sections()[mark]
            if args.verbose:
                print(mark + 1, '/', sections, ' >>>', name)
            formula = _load(name).tell_form()
        except Exception as e:
            name = 'null'
            if args.verbose:
                print('WARNING: cull     [FAIL]')
            if args.verbose == 2:
                print('e:', e)
            continue
        try:  
            diff = set(formula.keys()) - set(command.keys())
            sim = set(command.items()) & set(formula.items())
            if len(sim) is len(command):
                if args.verbose:
                    print('INFO: cull       [PASS]')
                break
            if len(sim) is not len(command):
                if args.verbose:
                    print('INFO: cull       [FAIL]')
                name = None
                continue
        except Exception as e:
            if args.verbose == 2:
                print('ERROR: cull:', e)
    return (name, mark)

def _load(name):
    '''Import a module by name.'''
    try:
        plugin_path = path.join(prefix, '.'.join([name, 'py']))
        spec = SourceFileLoader(name, plugin_path)
        module = spec.load_module()
        if args.verbose == 2:
            print('INFO: load       [PASS]')
        return module
    except Exception as e:
        if args.verbose == 2:
            print('e:', e)

def push(name, data):
    '''
    * This is the fuction which intereacts with plugins.
    Accepts name of past-bin and data in bytes.
    Example: push("clbin", "b'Hello, World!'")
    Returns a dictionary with keys link, code and reason. 
    '''
    try:
        if args.login:
            login = (config[name]['username'], config[name]['password'])
        else:
            login = (None, None)
        ## url and data are required, the rest are optional
        request_chain = {
                'url': config[name]['url'], 
                'data': data, 
                'time': args.expiry, 
                'login': login
                }
        response = 'null'
        response = _load(name).tell_post(request_chain)
        if 'http' not in str(response['link']):
            if response['reason']:
                if args.verbose:
                    print('ERROR: plugin    [FAIL]')
                if args.verbose == 2:
                    print('e:', response['reason'])
        else:
            if args.verbose == 2:
                print('INFO: push       [PASS]')
    except Exception as e:
        if args.verbose:
            print('WARNING: push    [FAIL]')
        if args.verbose == 2:
            print('e:', e)
    finally: 
        return response

def plaster(command, data):
    '''
    Accepts command as a dictionary and data in bytes.
    example: plaster({'txt': 'yes'}, "b'Hello, World!'") 
    Return value is a dicionary with keys link, code and reason.
    '''
    sections = (len(config.sections()))
    i, mark = 0, 0
    response = 'null'
    for i in range(0, sections):
        try:
            ## mark should equal i.
            cull = _cull(command, mark)
            name = cull[0]
            mark = cull[1] + 1
            i = cull[1] + 1
            if name is 'null':
                continue
            response = push(name, data)
            try:
                link = str(response['link'])
            except Exception as e:
                if args.verbose:
                    print('WARNING: plugin  [FAIL]')
                if args.verbose == 2:
                    print('e:', e) 
                continue
            if 'http' in link: 
                break
            if mark <= sections:
                if args.verbose == 2:
                    print('####')
        except Exception as e:
            response = 'null'
            mark = mark + 1
            i = i + 1
            if args.verbose:
                print('WARNING: plaster [FAIL]')
            if args.verbose == 2:
                print('e:', e)
            continue
    return response

#
# main
#

config = _config()

def __main__():
    content = _inlet()
    content_type = _sniff(content)
    command = _command(content_type)
    try:
        ## Command is a dictionary.
        response = plaster(command, content)
        if response is 'null':
            if args.verbose:
                print('done')
            exit(1)
        link = 'null'
        link = str(response['link'])
        try:
            if link != 'null' and 'http' in link:
                if args.verbose == 2:
                    print('INFO: main       [PASS]')
                print(str(link).rstrip())
        except:
            if args.verbose:
               print('ERROR: main      [FAIL]')
            if not args.verbose:
               print('to debug, try plaster -v')
        ## Optional clipboard feature. Requires xclip.
        if args.xclip:
            if import_pyperclip == False:
                exit('e: missing python-pyperclip')
            if import_pyperclip == True:
                pyperclip.copy(link)
    except Exception as e:
        if args.verbose == 2:
            print('ERROR: main:', e)
        raise
		
def __test__(): 
    print('debug mode [ON]')
    ###
    try:
        '''run test here'''
    except Exception as e:
        raise
        print('ERROR: test:', e)
    
if __name__ == '__main__':
    __main__()
    # __test__()
