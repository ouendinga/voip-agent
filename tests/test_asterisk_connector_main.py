import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from asterisk_connector import main as asterisk_main


def test_main_exists():
    assert hasattr(asterisk_main, 'main')
    assert callable(asterisk_main.main)

@pytest.mark.asyncio
async def test_start_stub():
    # Solo verifica que la función start existe y es coroutine
    if hasattr(asterisk_main, 'AsteriskApp'):
        app = asterisk_main.AsteriskApp(agi_port=4573, ami_client=None, rabbitmq_channel=None)
        assert hasattr(app, 'start')
        assert asyncio.iscoroutinefunction(app.start)
