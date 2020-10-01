"""PySerum."""

import sys

__import__("pkg_resources").declare_namespace("pyserum")  # type: ignore

if sys.version_info < (3, 7):
    raise EnvironmentError("Python 3.7 or above is required.")
