#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 13:25:50 2024

@author: 4vt
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--task', action = 'store', choices = ['download', 'search'], required = True,
                    help = 'Run download_eggnog_data.py or emapper.py, respectively.')
parser.add_argument('--options', action = 'store', required = True,
                    help = 'The options file to parse.')
parser.add_argument('--run_args', action = 'store', required = False, default = False,
                    help = 'Pass this string unaltered as the last part of the command line arguments.')
args = parser.parse_args()

import tomli
import subprocess

with open(args.options, 'rb') as toml:
    options = tomli.load(toml)

def flag_string(k,v):
    mark = '-' if len(k) == 1 else '--'
    return f'{mark}{k} {v}' if type(v) != bool else f'{mark}{k}'

def get_optstring(options):
    optstring = ' '.join(flag_string(k,v) for k,v in options.items())
    optstring += ' ' + args.run_args
    return optstring

if args.task == 'download':
    optstring = get_optstring(options['download_eggnog_data_params'])
    subprocess.run(f'download_eggnog_data.py {optstring}', shell = True)

if args.task == 'search':
    optstring = get_optstring(options['emapper_params'])
    subprocess.run(f'emapper.py {optstring}', shell = True)


