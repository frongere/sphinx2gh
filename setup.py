"""Setup script for sphinx2gh."""
from __future__ import print_function
from setuptools import setup, find_packages
import codecs
import os

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Return multiple read calls to different readable objects as a single
    string."""
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(HERE, *parts), 'r').read()

LONG_DESCRIPTION = read('README.rst')

setup(
    name='sphinx2gh',
    version='0.1',
    url='https://',  # TODO : A completer
    author='Francois Rongere',
    author_email='franrongere@gmail.com',
    description="""A python command line tool to automate building and deployment of Sphinx documentation on GitHub""",
    long_description=LONG_DESCRIPTION,
    license='BSD',
    keywords='Documentation, Sphinx, Git, GitHub',
    packages=find_packages(exclude=['contrib', 'doc', 'tests*']),
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest', 'pytest-cov'],
    install_requires=['gitpython', 'argcomplete'],
    entry_points={
        'console_scripts': [
            'sphinx2gh=sphinx2gh:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Version Control',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
)
