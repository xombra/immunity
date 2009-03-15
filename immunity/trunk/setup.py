#!/usr/bin/python

from distutils.core import setup, Extension

module1 = Extension('immunity',
                    sources = ['immunity.c'])

setup (name = 'Immunity',
       version = '0.1',
       description = 'immunity python helper',
       ext_modules = [module1])

