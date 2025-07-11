import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from asterisk_connector.ami_client import AMIClient, AMIClientProtocol


@pytest.mark.asyncio
async def test_send_action_mock():
    client = AMIClient()
    # Mock protocol and transport
    client.protocol = MagicMock()
    client.protocol.send = MagicMock()
    # Llama send_action y luego simula la llegada de la respuesta AMI
    send_action_task = asyncio.create_task(client.send_action({'Action': 'Ping'}, wait_response=True, timeout=1))
    await asyncio.sleep(0.05)  # Da tiempo a que el future se cree
    # Busca el action_id generado
    action_id = next(iter(client._pending_actions.keys()))
    # Simula la llegada de la respuesta AMI
    await client.handle_message(f'Response: Success\r\nActionID: {action_id}\r\n')
    resp = await send_action_task
    assert resp is not None
    assert resp.get('Response') == 'Success'
    assert 'ActionID' in resp

@pytest.mark.asyncio
async def test_event_queue_mock():
    client = AMIClient()
    event = {'Event': 'TestEvent', 'Data': 'ok'}
    await client.event_queue.put(event)
    result = await client.get_event(timeout=1)
    assert result == event
