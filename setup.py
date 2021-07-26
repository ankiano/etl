#!/usr/bin/env python3.8
# coding=utf-8

from setuptools import setup, find_packages
from pathlib import Path
from pkg_resources import parse_requirements

with Path('requirements.txt').open() as requirements_txt:
    requirements = [
        str(requirement) for requirement in parse_requirements(requirements_txt)
    ]

setup(
    name='etl',
    version='0.0.32',
    description='ETL CLI tool',
    long_description='Extract transform load CLI tool for extracting small '
                     'and middle data volume from sources (databases, '
                     'csv files, xls files, gspreadsheets) '
                     'to target (databases, csv files, xls files, '
                     'gspreadsheets) in free combination.',
    py_modules=['etl'],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='etl',
    entry_points={'console_scripts': ['etl=etl:cli']},
)
