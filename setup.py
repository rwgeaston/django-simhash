import os
from setuptools import setup
from setuptools import find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-simhash',
    version='1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Simhash as django app',
    long_description=README,
    url='https://github.com/rwgeaston/',
    author='Robert Easton',
    author_email='rwgeaston@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    dependency_links=['https://github.com/scrapinghub/python-simhash/tarball/master']
)
