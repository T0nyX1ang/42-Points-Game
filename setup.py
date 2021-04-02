"""
Package setup.

This file is used to package the whole project.
"""

import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='42Points',
    version='1.2.7',
    author='Tony Xiang',
    author_email='tonyxfy@qq.com',
    description='Python implementation of the fourty-two points game.',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/T0nyX1ang/42-Points-Game',
    packages=setuptools.find_packages(include=['ftptsgame']),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.5',
)
