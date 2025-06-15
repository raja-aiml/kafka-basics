import sys
from pathlib import Path

# Ensure stub confluent_kafka package is on the path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / "stubs"))
# Ensure src is on the path
sys.path.insert(0, str(root.parent / "src"))
