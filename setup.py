# GNU Lesser General Public License v3.0 only
# Copyright (C) 2020 Artefact
# licence-information@artefact.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""The setup script."""

from setuptools import setup, find_packages


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
    include_package_data=True,
    name='nck',
    packages=find_packages(),
    setup_requires=setup_requirements,
    url='https://github.com/artefactory/nautilus-connectors-kit',
    version='0.1.0',
    zip_safe=False,
)
