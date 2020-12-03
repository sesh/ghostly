#!/usr/bin/env python

from setuptools import setup

setup(
    name='ghostly',
    version='0.7.1',
    description='Create simple browser tests',
    author='Brenton Cleeland',
    url='https://github.com/sesh/ghostly',
    install_requires=['click', 'colorama', 'pillow', 'PyYAML', 'selenium'],
    py_modules=['ghostly', 'fright'],
    entry_points={
        'console_scripts': [
            'ghostly=ghostly:run_ghostly',
            'fright=fright:run_fright',
        ]
    },
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    )
)
