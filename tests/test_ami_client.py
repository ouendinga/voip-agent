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
