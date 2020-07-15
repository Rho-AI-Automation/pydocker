from setuptools import setup,find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
from glob import glob
import os
import sys

setup(
    name='pydocker',
    version='2.0',
    packages=['pydocker'],
    entry_points ={'console_scripts': ['drun = pydocker.pydocker:docrun',
                                        'dcreate=pydocker.pydocker:docreate',
                                        'doscraper=pydocker.pydocker:gscraper_run',
                                        'dupload=pydocker.uploader:keep_update_loop',
                                        'fupload=pydocker.uploader:do_force_upload',
                                        'uchecker=pydocker.pydocker:bulk_ucheck',
                                        'urender=pydocker.pydocker:uchecker_render',
                                        'keepsplash=pydocker.splashim:keep_splash_running',
                                        'stopsplash=pydocker.splashim:stop_all_splash',
                                        'uploadthis=pydocker.uploader:upload_current_folder',
                                        'gscrape_google=pydocker.pydocker:bulk_gscrape_google',
                                        'gscrape_jsdom=pydocker.pydocker:bulk_gscrape_jsdom',
                                        'gscrape_chdriver=pydocker.pydocker:bulk_gscrape_chdriver',
                                        'dsnooper=pydocker.pydocker:doc_snoop',
                                        'dsjsdom=pydocker.pydocker:doc_jsdom']}
)
