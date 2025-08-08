# This file is deprecated in favor of pyproject.toml
# Please use: uv sync
# 
# For backward compatibility, you can still install with:
# pip install -e .
#
# But we recommend using uv for better performance and reliability.

import warnings
warnings.warn(
    "setup.py is deprecated. Please use 'uv sync' for installation.",
    DeprecationWarning,
    stacklevel=2
)

from setuptools import setup
setup()
