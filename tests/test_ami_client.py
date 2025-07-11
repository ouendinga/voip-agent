import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from asterisk_connector.ami_client import AMIClient


@pytest.mark.asyncio
async def test_ami_client_connect(monkeypatch):
    """
    Prueba de conexión y autenticación del AMIClient.
    Esta prueba requiere que el servidor AMI esté disponible en las variables de entorno.
    """
    # Configura variables de entorno para la prueba (ajusta según tu entorno real)
    os.environ["ASTERISK_HOST"] = os.getenv("ASTERISK_HOST", "127.0.0.1")
    os.environ["ASTERISK_AMI_PORT"] = os.getenv("ASTERISK_AMI_PORT", "5038")
    os.environ["ASTERISK_AMI_USER"] = os.getenv("ASTERISK_AMI_USER", "admin")
    os.environ["ASTERISK_AMI_PASS"] = os.getenv("ASTERISK_AMI_PASS", "admin")

    client = AMIClient()
    # Intentar conectar y autenticar (timeout corto para evitar cuelgues)
    try:
        await asyncio.wait_for(client.connect(), timeout=10)
        assert client._authenticated.is_set(), "No se autenticó correctamente con el AMI"
    except asyncio.TimeoutError:
        pytest.skip("Timeout: No se pudo conectar al AMI. ¿Está el servidor disponible?")

    finally:
        await client.close()


@pytest.mark.asyncio
async def test_ami_client_handle_message_parsing(monkeypatch):
    """
    Prueba el parseo de eventos AMI en handle_message.
    """
    client = AMIClient()
    # Mockear el canal de RabbitMQ para evitar publicaciones reales
    client.rabbitmq_channel = None
    # Mensaje AMI simulado
    msg = "Event: Newchannel\r\nChannel: SIP/100-00000001\r\nUniqueid: 123456\r\n\r\n"
    await client.handle_message(msg.strip())
    # El evento debe estar en la cola interna
    event = await client.event_queue.get()
    assert event["Event"] == "Newchannel"
    assert event["Channel"] == "SIP/100-00000001"


@pytest.mark.asyncio
async def test_ami_client_rabbitmq_publish(monkeypatch):
    """
    Prueba que se publique en RabbitMQ al recibir un evento Newchannel.
    """
    client = AMIClient()
    published = {}
    class DummyChannel:
        def basic_publish(self, exchange, routing_key, body, properties):
            published["exchange"] = exchange
            published["routing_key"] = routing_key
            published["body"] = body
            published["properties"] = properties
    client.rabbitmq_channel = DummyChannel()
    msg = "Event: Newchannel\r\nChannel: SIP/200-00000002\r\nUniqueid: 654321\r\n\r\n"
    await client.handle_message(msg.strip())
    # Verifica que se haya publicado algo en RabbitMQ
    assert published["routing_key"] == "incoming_audio_chunks"
    assert "SIP/200-00000002" in published["body"]
