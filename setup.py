from os import path
from codecs import open
from setuptools import setup, find_packages


NAME = 'xtouchqusb'
VERSION = '0.0.0'
DESCRIPTION = 'Operate Allen & Heath QuSB mixer with Behringer's X-Touch and a Raspberry Pi'
AUTHOR = 'Frangitron'
AUTHOR_EMAIL = 'contact@frangitron.com'


_here = path.abspath(path.dirname(__file__))
_requirements_filepath = path.join(_here, 'requirements.txt')

if path.isfile(_requirements_filepath):
    with open(_requirements_filepath) as requirements_file:
        _requirements = requirements_file.readlines()
else:
    _requirements = list()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description="",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(exclude=['tests']),
    install_requires=_requirements,
    include_package_data=True,
    python_requires='>3.10',
)
