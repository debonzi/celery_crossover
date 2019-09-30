#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup

def long_desc_img_replacer(long_desc):
    replacements = (
        (
            '(docs/CeleryCrossoverUseCase.png)',
            '(https://raw.githubusercontent.com/debonzi/celery_crossover/master/docs/CeleryCrossoverUseCase.png)'
        ),
    )
    for f, t in replacements:
        long_desc = long_desc.replace(f, t)
    return long_desc


with open('README.md') as f:
    long_description = long_desc_img_replacer(f.read())


requires = [
    'celery[redis]>=3.1.20',
    'requests-celery-adapters>=2.0.13',
    'six>=1.11.0'
            ]

extras_require = {
    'test': [
        'pytest',
        'pytest-cov',
    ],
    'ci': [
        'python-coveralls',
    ]
}


setup(name='celery-crossover',
      version='1.1.11',
      description='Celery Crossover aims to make it really easy to execute tasks in another service.',
      long_description=long_description,
      long_description_content_type='text/markdown',

      author='Daniel Debonzi',
      author_email='debonzi@gmail.com',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Object Brokering',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6'
      ],
      install_requires=requires,
      extras_require=extras_require,
      url='https://github.com/debonzi/celery_crossover',
      packages=['crossover', 'examples'],
      )
