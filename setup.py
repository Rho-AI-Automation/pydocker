from setuptools import setup,find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
from glob import glob
import os
import sys



setup(
    name='pydocker',
    version='1.0',
    packages=['pydocker'],
    entry_points ={'console_scripts': ['dcreate = pydocker.pydocker:docrun']}
)
