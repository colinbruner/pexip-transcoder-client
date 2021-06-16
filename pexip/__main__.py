#!/usr/bin/env python
""" The main entry point. Invoke as `pexip' or `python -m pexip'.  """
import sys


def main():
    from .core import main
    main()

if __name__ == "__main__":
    main()
