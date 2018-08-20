
import os
from setuptools import setup

setup(name='databot',
      description='data flow programming framework with asyncio'
                  ' ',
      long_description='data flow programming framework with asyncio',
      version='0.1.0',
      url='https://github.com/guojianli/databot',
      author='Guojian Li',
      author_email='guojianlee@gmail.com',
      license='BSD',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3'
      ],
      packages=['databot'],
      install_requires=[
          'aiohttp>=3.3.2'

      ],

)



