#!/usr/bin/python
# -*- coding: utf-8 -*-
#contains global functions, useful for every class/file

if __name__ =='__main__':
    print('This file should not be called directly.\
           Use \'python main.py -h\' for help.')
    print('exiting...')
    quit()

#already been checked
import sys

def error(x, e = None):
    print(x)
    if e != None:
        print('Printing error stack:')
        print(e)
    print('exiting...')
    sys.exit(1)
