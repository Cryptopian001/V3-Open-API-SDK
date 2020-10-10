import os

import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cp-okex",  # Replace with your own username
    version="0.0.2",
    author="Han Wu",
    author_email="han.wu@cryptopian.io",
    description="Cryptopian version of OKEx RESTful and WebSocket API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cryptopian001/V3-Open-API-SDK",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'websocket-client'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
