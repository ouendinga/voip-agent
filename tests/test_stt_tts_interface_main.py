import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from stt_tts_interface import main as stt_main


def test_main_exists():
    assert hasattr(stt_main, 'main')
    assert callable(stt_main.main)
