import os
import shutil

import setuptools

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup = dict(
    name="ArduinoCodeCreator",
    version="0.1",
    author="Julian Kimmig",
    author_email="julian-kimmig@gmx.net",
    description="python code creator for creating arduino code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JulianKimmig/ArduinoCodeCreator",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
if __name__ == "__main__":
    shutil.rmtree(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist"),
        ignore_errors=True,
    )
    shutil.rmtree(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"),
        ignore_errors=True,
    )
    setuptools.setup(**setup)
