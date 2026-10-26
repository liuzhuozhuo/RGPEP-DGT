import os
import sys

# Use a backend without a window, the tests never show figures
os.environ.setdefault("MPLBACKEND", "Agg")

# Make tests/wick_reference.py importable from the test files
sys.path.insert(0, os.path.dirname(__file__))
