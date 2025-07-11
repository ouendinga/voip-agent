import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from asterisk_connector.asterisk_connector_servicer import serve


def test_serve_exists():
    assert callable(serve)

@pytest.mark.asyncio
async def test_handle_callstream_stub():
    # Test de stub para asegurar que el método existe y es coroutine
    from asterisk_connector.asterisk_connector_servicer import \
        AsteriskConnectorServicer
    servicer = AsteriskConnectorServicer()
    assert hasattr(servicer, 'HandleCallStream')
    assert asyncio.iscoroutinefunction(servicer.HandleCallStream)
