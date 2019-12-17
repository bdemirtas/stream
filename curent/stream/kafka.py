"""Kafka stream.

Uses Confluent's Kafka Python client.
"""

import logging

import attr

from confluent_kafka import (
    Consumer,
    KafkaError,
    Producer,
)

from curent.stream import (
    Stream,
    StreamEmpty,
    StreamError,
    StreamMessage,
    StreamPublisher,
    StreamSubscriber,
)

from curent.stream.helper import asynchronize

@attr.s(frozen=True, slots=True)
class KafkaPublisher(StreamPublisher):
    """Kafka publisher."""

    _producer = attr.ib()

    @asynchronize
    def send(self, msg):
        """Produce a message on the Kafka producer.
        """

        def callback(err, _):
            if err is not None:
                raise StreamError(err)

        logging.debug("Producing message on Kafka producer to %(topic)s", {
            'topic': msg.topic,
        })
        try:
            self._producer.produce(
                msg.topic, msg.payload, callback=callback)
        except TypeError as error:
            raise StreamError(
                "Failed to produce {!r}".format(msg.payload)) from error

        self._producer.flush()


@attr.s(frozen=True, slots=True)
class KafkaSubscriber(StreamSubscriber):
    """Kafka subscriber."""

    _consumer = attr.ib()

    @asynchronize
    def receive(self, timeout=-1):
        """Poll for the next available message on the Kafka consumer."""
        while True:
            logging.debug("Polling Kafka consumer for %(timeout)d ms", {
                'timeout': timeout,
            })
            response = self._consumer.poll(timeout)

            if response is None:
                raise StreamEmpty(
                    "Topics {} were empty for {:d} ms".format(
                        self.topics, timeout))
            elif response.error():
                if response.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise StreamError(response.error())
            else:
                return StreamMessage(
                    topic=response.topic(),
                    payload=response.value()
                )

    def close(self):
        """Close the Kafka consumer."""
        self._consumer.close()


@attr.s(frozen=True, slots=True)
class KafkaStream(Stream):
    """Kafka stream."""

    def publish(self):
        """Publish to a Kafka producer."""
        logging.info("Producing to Kafka at %(target)s", {
            'target': self.target,
        })
        producer = Producer({
            'bootstrap.servers': self.target,
            'default.topic.config': {
                'acks': 'all',
            },
        })
        return KafkaPublisher(self.loop, producer)

    def subscribe(self, topics):
        """Subscribe to topics on a Kakfa consumer."""
        logging.info("Consuming from Kafka at %(target)s", {
            'target': self.target,
        })
        consumer = Consumer({
            'bootstrap.servers': self.target,
            'group.id': 'mygroup',
            'default.topic.config': {
                'auto.offset.reset': 'smallest',
            },
        })

        logging.info("Subscribing Kafka consumer to %(topics)s", {
            'topics': topics,
        })
        consumer.subscribe(topics)
        return KafkaSubscriber(self.loop, topics, consumer)
