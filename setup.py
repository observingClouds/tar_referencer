#!/usr/bin/env python

"""The setup script."""


from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().strip().split("\n")

test_requirements = [
    "pytest>=3",
    "xarray",
    "zarr",
]


setup(
    author="Hauke Schulz",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Creating parquet file reference system for tar archives.",
    entry_points={
        "console_scripts": [
            "tar_referencer=tar_referencer.referencer:main",
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    include_package_data=True,
    keywords="tar_referencer",
    name="tar_referencer",
    packages=find_packages(include=["tar_referencer", "tar_referencer.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/observingClouds/tar_referencer",
    version="0.0.1",
    zip_safe=False,
)
