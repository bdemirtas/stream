"""Redis stream.

Uses Redis Python client.
"""

import logging

import attr

import redis
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
)

from burak.stream import (
    Stream,
    StreamEmpty,
    StreamError,
    StreamMessage,
    StreamPublisher,
    StreamSubscriber,
)
from burak.stream.async import asynchronize


@attr.s(frozen=True, slots=True)
class RedisPublisher(StreamPublisher):
    """Redis publisher."""

    _producer = attr.ib()

    @asynchronize
    def send(self, msg):
        """Produce a message on the Redis producer.
        """
        logging.debug("Producing message on Redis producer to %(topic)s", {
            'topic': msg.topic,
        })
        try:
            self._producer.publish(msg.topic, msg.payload)
        except (ConnectionError, TimeoutError) as error:
            raise StreamError("Failed to produce {!r}".format(msg.payload)) from error


@attr.s(frozen=True, slots=True)
class RedisSubscriber(StreamSubscriber):
    """Redis subscriber."""

    _consumer = attr.ib()

    @asynchronize
    def receive(self, timeout=2):
        """Poll for the next available message on the Redis consumer."""
        while True:
            logging.debug("Polling Redis consumer for %(timeout)d ms", {
                'timeout': timeout,
            })
            response = self._consumer.get_message(timeout=timeout)
            if response:
                return StreamMessage(
                    topic=response['channel'],
                    payload=response['data']
                )

    def close(self):
        """Close the Redis consumer."""
        self._consumer.unsubscribe()


@attr.s(frozen=True, slots=True)
class RedisStream(Stream):
    """Redis stream."""

    def publish(self):
        """Publish to a Redis producer."""
        logging.info("Producing to Redis at %(target)s", {
            'target': self.target,
        })
        return RedisPublisher(self.loop, redis.StrictRedis(self.target))

    def subscribe(self, topics):
        """Subscribe to topics on a Redis consumer."""
        logging.info("Consuming from Redis at %(target)s", {
            'target': self.target,
        })
        logging.info("Subscribing Redis consumer to %(topics)s", {
            'topics': topics,
        })
        pubsub = redis.StrictRedis(self.target).pubsub()
        pubsub.subscribe(topics)
        return RedisSubscriber(self.loop, topics, pubsub)

