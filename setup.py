#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='yaphue',
    version='0.3.6',
    description='Yet Another Python / Philips Hue -library',
    author='Kimmo Huoman',
    author_email='kipenroskaposti@gmail.com',
    url='https://github.com/kipe/yaphue',
    packages=[
        'yaphue',
    ],
    install_requires=[
        'requests==2.12.4',
        'rgbxy==0.5.0',
    ])
