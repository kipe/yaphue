#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='yaphue',
    version='0.0.1',
    description='Yet Another Python / Philips Hue -library',
    author='Kimmo Huoman',
    author_email='kipenroskaposti@gmail.com',
    url='https://github.com/kipe/yaphue',
    packages=[
        'yaphue',
    ],
    install_requires=[
        'requests==2.12.4',
    ])
