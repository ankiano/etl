#!/usr/bin/env python3.10
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
    version='1.0.14',
    description='ETL CLI tool',
    long_description='Extract transform load CLI tool for extracting small '
                     'and middle data volume between sources (databases, '
                     'csv files, xls files, gspreadsheets).',
    py_modules=['etl'],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='etl',
    entry_points={'console_scripts': ['etl=etl:cli']},
)
