from setuptools import setup
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='TSBVMIP',
    version='0.0.1',
    description='tiny Stackbased-Virtual-Machine-in-Python',
    long_description=long_description,
    url='https://github.com/lukleh/Tiny-Stackbased-Virtual-Machine-in-Python',
    author='Lukas Lehher',
    author_email='lehner.lukas@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Interpreters',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    tests_require=['pytest'],
    keywords='virtual machine stack',
    packages=['TSBVMIP'],
)
