#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Julian Garratt",
    author_email='jgarratt01@icloud.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Overkill lets you run parallel processes accross computers",
    entry_points={
        'console_scripts': [
            'overkill=overkill.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='overkill',
    name='overkill',
    packages=find_packages(include=['overkill', 'overkill.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/millenniumForce/overkill',
    version='0.4.3',
    zip_safe=False,
)
