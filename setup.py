
import os
from setuptools import setup

import codecs

def read(fname):

    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='databot',
      description='data flow programming framework with asyncio'
                  ' ',
      long_description=read("README.rst"),
      version='0.1.0',
      url='https://github.com/guojianli/databot',
      author='Guojian Li',
      author_email='guojianlee@gmail.com',
      license='BSD',
     python_requires=">=3.6.5",
      classifiers=[
          'Development Status :: 1 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3'
      ],
      packages=['databot'],
      install_requires=[
          'aiohttp>=3.3.0'

      ],

)



