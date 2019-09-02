#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import aws_ssh_sync

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-ssh-sync",
    version=aws_ssh_sync.__version__,
    author="Szymon Biliński",
    author_email="szymon.bilinski@gmail.com",
    description="Generate 'ssh_config' files, based on current Amazon EC2 state.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sbilinski/aws-ssh-sync",
    packages=setuptools.find_packages(),
    scripts=["aws_ssh_sync.py"],
    install_requires=["boto3>=1.9"],
    classifiers=[
        "Topic :: System :: Networking",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX"
    ],
    python_requires='>=3.6',
)
