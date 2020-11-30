from setuptools import setup,find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
from glob import glob
import os
import sys

setup(
    name='pydocker',
    version='3.0',
    packages=['pydocker'],
    entry_points ={'console_scripts': ['drun = pydocker.pydocker:docrun',
                                        'dupload=pydocker.uploader:keep_update_loop',
                                        'fupload=pydocker.uploader:do_force_upload',
                                        'pyuchecker=pydocker.pydocker:bulk_ucheck',
                                        'bulkucheck=pydocker.pydocker:bulk_ucheck_run',
                                        'bulkpcheck=pydocker.pydocker:bulk_pcheck_run',
                                        'gscrape_google=pydocker.pydocker:bulk_gscrape_google',
                                        'bulkucheck_all=pydocker.pydocker:bulk_ucheck_run_allclient',
                                        'bulkucheck_k=pydocker.pydocker:bulk_ucheck_run_allclient_komal',
                                        ]}
)
