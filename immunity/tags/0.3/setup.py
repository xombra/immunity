#!/usr/bin/python

from distutils.core import setup, Extension

immunity_module = Extension('immunity',
                            sources   = ['immunity.c'],
		            libraries = ['cap'])

setup (name        = 'Immunity',
       version     = '0.1',
       description = 'immunity python helper',
       ext_modules = [immunity_module])

