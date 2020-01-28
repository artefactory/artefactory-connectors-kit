#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = [el.strip() for el in requirements_file.readlines()]

setup_requirements = []

setup(
    author="Artefact",
    author_email='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="API connectors",
    entry_points={
        'console_scripts': [
            'nckrun=nck.entrypoint:cli_entrypoint',
        ],
    },
    install_requires=requirements,
    #  long_description=readme + '\n\n' + history,
    include_package_data=True,
    # keywords='nautilus_connectors',
    name='nck',
    packages=find_packages(),
    setup_requires=setup_requirements,
    url='https://github.com/artefactory/nautilus-connectors-kit',
    version='0.1.0',
    zip_safe=False,
)
