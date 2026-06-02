"""Make the demo modules importable when pytest runs from the repo root."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
