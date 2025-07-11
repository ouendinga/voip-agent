import logging

import pika


class RabbitMQPublisher:
    def __init__(self, channel):
        self.channel = channel

    def publish(self, routing_key, message_body):
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logging.info(f"[RabbitMQPublisher] Publicado en {routing_key}: {message_body}")
        except Exception as e:
            logging.error(f"[RabbitMQPublisher] Error publicando en RabbitMQ: {e}")
