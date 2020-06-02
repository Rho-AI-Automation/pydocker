from setuptools import setup,find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
from glob import glob
import os
import sys



setup(
    name='pydocker',
    version='1.7',
    packages=['pydocker'],
    entry_points ={'console_scripts': ['drun = pydocker.pydocker:docrun',
                                        'dcreate=pydocker.pydocker:docreate',
                                        'doscraper=pydocker.pydocker:gscraper_run',
                                        'dupload=pydocker.uploader:keep_update_loop',
                                        'fupload=pydocker.uploader:do_force_upload',
                                        'uchecker=pydocker.pydocker:bulk_ucheck']}
)
