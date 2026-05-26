import os
import sys

# Reuse the edge_dev3 implementation — only DEVICE_ID and window title differ.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_EDGE_DEV3 = os.path.join(_THIS_DIR, "..", "edge_dev3")
sys.path.insert(0, _EDGE_DEV3)

from dotenv import load_dotenv

load_dotenv(os.path.join(_THIS_DIR, ".env"))
os.environ.setdefault("DEVICE_ID", "edge_dev2")

from main import run  # noqa: E402  (edge_dev3/main.py)


if __name__ == "__main__":
    run(window_title="Edge Dev 2 - Person Detection")
