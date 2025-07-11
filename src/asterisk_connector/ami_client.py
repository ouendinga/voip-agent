import asyncio
import logging
import os
from typing import Any, Dict, Optional

import pika


class AMIClientProtocol(asyncio.Protocol):
    def __init__(self, client):
        self.client = client
        self.transport = None
        self.buffer = ""

    def connection_made(self, transport):
        self.transport = transport
        logging.info("AMI: Conexión establecida con el servidor AMI.")
        asyncio.create_task(self.client.authenticate())

    def data_received(self, data):
        text = data.decode(errors="replace")
        self.buffer += text
        while "\r\n\r\n" in self.buffer:
            msg, self.buffer = self.buffer.split("\r\n\r\n", 1)
            asyncio.create_task(self.client.handle_message(msg))

    def connection_lost(self, exc):
        logging.warning("AMI: Conexión perdida con el servidor AMI.")
        asyncio.create_task(self.client.on_connection_lost(exc))

    def send(self, data: str):
        if self.transport:
            self.transport.write(data.encode())

class AMIClient:
    def __init__(self, loop=None):
        self.host = os.getenv("ASTERISK_HOST", "127.0.0.1")
        self.port = int(os.getenv("ASTERISK_AMI_PORT", "5038"))
        self.username = os.getenv("ASTERISK_AMI_USER", "admin")
        self.password = os.getenv("ASTERISK_AMI_PASS", "admin")
        self.loop = loop or asyncio.get_event_loop()
        self.protocol: Optional[AMIClientProtocol] = None
        self.transport = None
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self._connected = asyncio.Event()
        self._authenticated = asyncio.Event()
        self._reconnect_delay = 3
        self._action_id = 0
        self._pending_actions = {}
        self._running = False

        # RabbitMQ connection setup
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
            self.rabbitmq_channel.queue_declare(queue='incoming_audio_chunks', durable=True)
        except Exception as e:
            logging.error(f"AMI: Error conectando a RabbitMQ: {e}")
            self.rabbitmq_conn = None
            self.rabbitmq_channel = None

    async def connect(self):
        self._running = True
        while self._running:
            try:
                logging.info(f"AMI: Intentando conectar a {self.host}:{self.port}")
                transport, protocol = await self.loop.create_connection(
                    lambda: AMIClientProtocol(self), self.host, self.port
                )
                self.transport = transport
                self.protocol = protocol
                await self._connected.wait()
                await self._authenticated.wait()
                logging.info("AMI: Cliente autenticado y listo.")
                break
            except Exception as e:
                logging.error(f"AMI: Error de conexión: {e}. Reintentando en {self._reconnect_delay}s...")
                await asyncio.sleep(self._reconnect_delay)

    async def authenticate(self):
        self._connected.set()
        action = {
            "Action": "Login",
            "Username": self.username,
            "Secret": self.password,
            "Events": "on"
        }
        resp = await self.send_action(action, wait_response=True)
        if resp and resp.get("Response", "") == "Success":
            logging.info("AMI: Autenticación exitosa.")
            self._authenticated.set()
        else:
            logging.error(f"AMI: Fallo de autenticación: {resp}")
            self._authenticated.clear()
            await self.close()

    async def send_action(self, action_dict: Dict[str, Any], wait_response: bool = False, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Envía una acción AMI. Si wait_response=True, espera la respuesta y la retorna."""
        if not self.protocol:
            raise RuntimeError("AMI: No conectado.")
        self._action_id += 1
        action_id = f"copilot-{self._action_id}"
        action_dict["ActionID"] = action_id
        lines = [f"{k}: {v}" for k, v in action_dict.items()]
        msg = "\r\n".join(lines) + "\r\n\r\n"
        fut = None
        if wait_response:
            fut = self.loop.create_future()
            self._pending_actions[action_id] = fut
        self.protocol.send(msg)
        if wait_response:
            try:
                resp = await asyncio.wait_for(fut, timeout=timeout)
                return resp
            except asyncio.TimeoutError:
                logging.error(f"AMI: Timeout esperando respuesta para ActionID {action_id}")
                return None
            finally:
                self._pending_actions.pop(action_id, None)
        return None

    async def handle_message(self, msg: str):
        # Parse AMI message into dict
        lines = msg.split("\r\n")
        data = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()

        if "ActionID" in data and data["ActionID"] in self._pending_actions:
            fut = self._pending_actions[data["ActionID"]]
            if not fut.done():
                fut.set_result(data)
        elif "Event" in data:
            event_type = data.get("Event")
            # El call_id debe ser SIEMPRE el Channel de Asterisk (ej: SIP/mi_ext-00000001)
            call_id = data.get("Channel")
            if not call_id:
                logging.warning("No se encontró Channel en el evento AMI; no se puede establecer call_id único para la llamada.")
                return
            # Usar call_id (Channel) como identificador único en todos los mensajes
            if event_type == "Newchannel":
                logging.info(f"AMI: Nueva llamada iniciada para call_id={call_id} (Channel)")
                # Simular transcripción inicial
                simulated_transcript = {
                    "call_id": call_id,  # Channel como call_id
                    "text": "El usuario dice: 'Hola, ¿en qué puedo ayudarle?'"
                }
                # Publicar en RabbitMQ
                if self.rabbitmq_channel:
                    try:
                        self.rabbitmq_channel.basic_publish(
                            exchange='',
                            routing_key='incoming_audio_chunks',
                            body=str(simulated_transcript),
                            properties=pika.BasicProperties(delivery_mode=2)
                        )
                        logging.info(f"Publicado en RabbitMQ: {simulated_transcript}")
                    except Exception as e:
                        logging.error(f"Error publicando en RabbitMQ: {e}")
            elif event_type == "Hangup":
                logging.info(f"AMI: Llamada finalizada para call_id={call_id} (Channel)")
                # Publicar fin de llamada si se desea
                end_msg = {"call_id": call_id, "event": "call_ended"}
                if self.rabbitmq_channel:
                    try:
                        self.rabbitmq_channel.basic_publish(
                            exchange='',
                            routing_key='incoming_audio_chunks',
                            body=str(end_msg),
                            properties=pika.BasicProperties(delivery_mode=2)
                        )
                        logging.info(f"Publicado fin de llamada en RabbitMQ: {end_msg}")
                    except Exception as e:
                        logging.error(f"Error publicando fin de llamada en RabbitMQ: {e}")
            # Poner el evento en la cola interna también
            await self.event_queue.put(data)
            logging.info(f"AMI: Evento recibido: {event_type}")
        else:
            # Mensaje no identificado
            await self.event_queue.put(data)
            logging.info(f"AMI: Mensaje recibido: {data}")

    async def on_connection_lost(self, exc):
        self._connected.clear()
        self._authenticated.clear()
        self.protocol = None
        self.transport = None
        if self._running:
            logging.warning("AMI: Intentando reconectar...")
            await asyncio.sleep(self._reconnect_delay)
            await self.connect()

    async def close(self):
        self._running = False
        if self.transport:
            self.transport.close()
        self.protocol = None
        self.transport = None
        self._connected.clear()
        self._authenticated.clear()

    async def get_event(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        try:
            return await asyncio.wait_for(self.event_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def run(self):
        await self.connect()
        # Mantener vivo
        while self._running:
            await asyncio.sleep(1)

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    async def main():
        client = AMIClient()
        await client.run()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
