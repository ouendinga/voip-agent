#!/usr/bin/env python3
"""
Asterisk Connector - Microservicio para conectar con Asterisk
"""


import asyncio
import logging
import os
import sys
import time
from datetime import datetime

import aio_pika
from ami_client import AMIClient


class AGIServer:
    def __init__(self, agi_port, ami_client, rabbitmq_channel):
        self.agi_port = agi_port
        self.ami_client = ami_client
        self.rabbitmq_channel = rabbitmq_channel
        self.logger = logging.getLogger("AGIServer")

    async def handle_agi(self, reader, writer):
        # Leer variables AGI
        agi_env = {}
        while True:
            line = await reader.readline()
            if not line or line == b'\n' or line == b'\r\n':
                break
            key, _, value = line.decode(errors="replace").partition(":")
            agi_env[key.strip()] = value.strip()
        call_id = agi_env.get("agi_channel", "unknown")
        self.logger.info(f"[AGI] Nueva conexión AGI para call_id={call_id}")

        # Lanzar tareas de audio bidireccional
        async def read_and_publish_audio():
            try:
                while True:
                    chunk = await reader.read(1024)
                    if not chunk:
                        break
                    msg = {
                        "call_id": call_id,
                        "audio": chunk,
                        "format": "pcm",
                        "agi_env": agi_env
                    }
                    await self.rabbitmq_channel.default_exchange.publish(
                        aio_pika.Message(body=chunk, headers={"call_id": call_id, "format": "pcm"}),
                        routing_key="incoming_audio_chunks"
                    )
            except Exception as e:
                self.logger.error(f"[AGI] Error leyendo audio: {e}")

        async def consume_and_write_audio():
            try:
                queue = await self.rabbitmq_channel.declare_queue("outgoing_audio_chunks", durable=True)
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            if message.headers.get("call_id") == call_id:
                                writer.write(message.body)
                                await writer.drain()
            except Exception as e:
                self.logger.error(f"[AGI] Error escribiendo audio: {e}")

        # Ejecutar ambas tareas concurrentemente
        await asyncio.gather(read_and_publish_audio(), consume_and_write_audio())
        self.logger.info(f"[AGI] Fin de llamada para call_id={call_id}")
        writer.close()
        await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_agi, host="0.0.0.0", port=self.agi_port)
        self.logger.info(f"AGI Server escuchando en el puerto {self.agi_port}")
        async with server:
            await server.serve_forever()


def main():

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    agi_port = int(os.getenv("ASTERISK_AGI_PORT", "4573"))

    async def async_main():
        # Inicializar AMIClient
        ami_client = AMIClient()
        await ami_client.connect()

        # Inicializar RabbitMQ async
        rabbitmq_url = f"amqp://{os.getenv('RABBITMQ_USER', 'guest')}:{os.getenv('RABBITMQ_PASS', 'guest')}@{os.getenv('RABBITMQ_HOST', 'localhost')}/"
        rabbitmq_conn = await aio_pika.connect_robust(rabbitmq_url)
        rabbitmq_channel = await rabbitmq_conn.channel()

        # Inicializar AGIServer
        agi_server = AGIServer(agi_port, ami_client, rabbitmq_channel)

        # Importar y lanzar gRPC server
        from asterisk_connector_servicer import serve as grpc_serve

        # Lanzar tareas concurrentes
        await asyncio.gather(
            ami_client.run(),
            agi_server.start(),
            grpc_serve()
        )

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logging.info("Deteniendo Asterisk Connector...")
        sys.exit(0)

if __name__ == "__main__":
    main()
