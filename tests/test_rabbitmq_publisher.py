from unittest.mock import MagicMock

import pytest

from asterisk_connector.rabbitmq_publisher import RabbitMQPublisher


class DummyChannel:
    def __init__(self):
        self.published = []
        self.raise_error = False
    def basic_publish(self, exchange, routing_key, body, properties):
        if self.raise_error:
            raise Exception("Publish error")
        self.published.append((exchange, routing_key, body, properties))

def test_publish_success(monkeypatch):
    channel = DummyChannel()
    publisher = RabbitMQPublisher(channel)
    publisher.publish('test_queue', 'hello')
    assert len(channel.published) == 1
    exchange, routing_key, body, properties = channel.published[0]
    assert exchange == ''
    assert routing_key == 'test_queue'
    assert body == 'hello'
    assert hasattr(properties, 'delivery_mode')

def test_publish_error(monkeypatch, caplog):
    channel = DummyChannel()
    channel.raise_error = True
    publisher = RabbitMQPublisher(channel)
    with caplog.at_level('ERROR'):
        publisher.publish('test_queue', 'fail')
    assert 'Error publicando en RabbitMQ' in caplog.text
