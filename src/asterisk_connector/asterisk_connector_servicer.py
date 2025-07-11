import asyncio
import logging
import os
import sys
from concurrent import futures
from typing import Any

import grpc
import pika

sys.path.append(os.path.join(os.path.dirname(__file__), '../../proto'))
import asterisk_service_pb2
import asterisk_service_pb2_grpc


class AsteriskConnectorServicer(asterisk_service_pb2_grpc.AsteriskConnectorServicer):
    def __init__(self):
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_pass = os.getenv("RABBITMQ_PASS", "guest")
        self.rabbitmq_conn = None
        self.rabbitmq_channel = None
        self._setup_rabbitmq()

    def _setup_rabbitmq(self):
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        parameters = pika.ConnectionParameters(host=self.rabbitmq_host, credentials=credentials)
        try:
            self.rabbitmq_conn = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_conn.channel()
            self.rabbitmq_channel.queue_declare(queue='outgoing_audio_chunks', durable=True)
        except Exception as e:
            logging.error(f"Error conectando a RabbitMQ: {e}\nVerifica usuario ('{self.rabbitmq_user}') y contraseña ('{self.rabbitmq_pass}') o la configuración del broker.")
            self.rabbitmq_conn = None
            self.rabbitmq_channel = None

    async def HandleCallStream(self, request_iterator, context):
        # En este ejemplo, solo consumimos mensajes de outgoing_audio_chunks y los "enviamos" a Asterisk (simulado)
        logging.info("HandleCallStream iniciado. Consumiendo de outgoing_audio_chunks...")
        if not self.rabbitmq_channel:
            logging.error("No hay canal RabbitMQ disponible.")
            return
        for method_frame, properties, body in self.rabbitmq_channel.consume('outgoing_audio_chunks', inactivity_timeout=1):
            if body:
                logging.info(f"Simulando envío a Asterisk: {body.decode() if hasattr(body, 'decode') else body}")
                self.rabbitmq_channel.basic_ack(method_frame.delivery_tag)
                # Aquí podrías enviar una respuesta al cliente gRPC si lo deseas
            await asyncio.sleep(0.1)  # Simula procesamiento
        logging.info("Fin de consumo de outgoing_audio_chunks.")
        # Aquí normalmente se respondería vía gRPC stream, pero este ejemplo es solo para simular el flujo.

# --- Servidor gRPC ---
def serve():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    async def main():
        server = grpc.aio.server()
        asterisk_service_pb2_grpc.add_AsteriskConnectorServicer_to_server(AsteriskConnectorServicer(), server)
        server.add_insecure_port('[::]:50051')
        logging.info("Servidor gRPC escuchando en el puerto 50051...")
        await server.start()
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            logging.info("Servidor detenido por el usuario.")

    asyncio.run(main())

if __name__ == "__main__":
    serve()
# NOTA: Para un servidor gRPC real, se debe registrar el servicer y arrancar el server.
# Este archivo es solo un esqueleto para la lógica solicitada.
