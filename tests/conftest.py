import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DEMO_PATH = PROJECT_ROOT / "examples" / "demo_transcript.json"


@pytest.fixture(scope="session")
def transcript():
    return json.loads(DEMO_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def segments(transcript):
    return transcript["segments"]
