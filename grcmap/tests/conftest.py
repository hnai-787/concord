import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORKS_DIR = REPO_ROOT / "frameworks"
MAPPINGS_DIR = REPO_ROOT / "mappings"
EXAMPLE_DIR = REPO_ROOT / "examples" / "meridian-bank"
