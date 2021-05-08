# !/usr/bin/env python

__author__ = "Sebastien Creoff"

import pathlib

from setuptools import find_packages, setup

# Import information from version without import module.
about = {}
version_file = pathlib.Path(".") / "src" / "jesse_live" / "__version__.py"
exec(version_file.read_text(), about)

setup(
    name="jesse_live",
    author="Sebastien creoff",
    version=about["__version__"],
    author_email="sebastien.creoff@gmail.com",
    description="A free version of Jesse Trading",
    entry_points={"live_jesse": ["live_run = jesse_live.worker.__main__:main"]},
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={},
    install_requires=[
        "setuptools >= 46.0.0",
        # "binance-futures-1.1.0"
    ],
    python_requires='>=3.7',
)
