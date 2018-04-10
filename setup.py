#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup

requires = [
    'celery[redis]>=3.1.20',
    'requests-celery-adapters>=2.0.7',
    'six>=1.11.0'
            ]

extras_require = {
    'test': [
        'pytest>=3.2.2'
    ],
}


setup(name='celery-crossover',
      version='1.1.6',
      description='Celery Crossover aims to make it really easy to execute tasks in another service.',
      author='Daniel Debonzi',
      author_email='debonzi@gmail.com',
      install_requires=requires,
      extras_require=extras_require,
      url='https://github.com/debonzi/celery_crossover',
      packages=['crossover', 'examples'],
      )
