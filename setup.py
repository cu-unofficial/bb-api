from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

import bb_api

setup(
    name="bb-api",
    packages=["bb_api"],
    version=bb_api.__version__,
    install_requires=[
        "requests >= 2.21.0",
        "beautifulsoup4 >= 4.6.3",
    ],
    description="A Python library to access information via https://cuchd.blackboard.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ritiek Malhotra",
    author_email="ritiekmalhotra123@gmail.com",
    license="GPLv3",

    # We support only Python 3, but we don't want to force users to avoid Python 2
    # Things might not work as expected on Python 2. Better use Python 3.
    # python_requires=">=3.4",

    url="https://github.com/cu-unofficial/bb-api",
    keywords=[
        "blackboard",
        "chandigarh university",
        "api",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
)
