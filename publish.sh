#!/bin/bash

poetry publish --build -u $PYPI_USERNAME -p $PYPI_PASSWORD
