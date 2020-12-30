#!/usr/bin/env bash
set -e

my_dir="$(dirname "$0")"
pushd "$my_dir"
rm -rf ./*.egg-info build dist
source ./venv/bin/activate
python3 -m pip install --upgrade setuptools wheel twine
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository-url http://nexus.cryptopian.io:8081/repository/pypi-hosted/ dist/*
rm -rf spool_api.egg-info build dist
popd