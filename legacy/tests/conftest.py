import os
import sys

os.environ.setdefault("MPLBACKEND", "Agg")

# tests/wick_reference.py is shared with the main tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tests"))
