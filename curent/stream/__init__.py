from abc import (
    abstractmethod,
    ABC,
)
from pkg_resources import iter_entry_points

import attr

from curent.stream.async import Asynchronizable


class StreamError(Exception):
    """Raised when a stream error occurs."""


class StreamNotFound(StreamError):
    """Raised when a stream is not found."""


class StreamEmpty(StreamError):
    """Raised when a stream is empty."""


@attr.s(frozen=True, slots=True)
class StreamMessage:
    """Stream message sent by publishers and received by subscribers."""

    topic = attr.ib()
    payload = attr.ib()

    def change(self, **changes):
        """Create a new `StreamMessage` with changes."""
        return attr.evolve(self, **changes)


@attr.s(frozen=True, slots=True)
class StreamConnection(Asynchronizable):
    """Connection to a stream publisher or subscriber.

    When an instance is used as a context manager, the close method is
    called on exit.
    """

    loop = attr.ib()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close the connection."""


@attr.s(frozen=True, slots=True)
class StreamPublisher(StreamConnection):
    """Stream publisher for sending messages on topics."""

    @abstractmethod
    def send(self, msg):
        """Send a `StreamMessage` to subscribers."""


@attr.s(frozen=True, slots=True)
class StreamSubscriber(StreamConnection):
    """Stream subscriber for receiving messages on topics."""

    topics = attr.ib()

    @abstractmethod
    def receive(self, timeout=-1):
        """Receive a `StreamMessage` from publishers.

        :param timeout: Timeout in milliseconds, blocks with -1 by default.
        """


@attr.s(frozen=True, slots=True)
class Stream(ABC):
    """Stream for publishing and subscribing."""

    target = attr.ib()
    loop = attr.ib(default=None)

    @classmethod
    def by_name(cls, name, target, loop=None):
        """Get a stream by name."""
        factories = get_stream_factories()
        try:
            factory = factories[name]
        except KeyError:
            raise StreamNotFound(
                "Stream name {!r} not found in {}".format(
                    name, list(factories)))

        return factory(target, loop)

    @abstractmethod
    def publish(self):
        """Publish to a topic on a stream."""

    @abstractmethod
    def subscribe(self, topics):
        """Subscribe to topics on a stream."""


def get_stream_factories():
    """Get stream factories indexed by name from the entry points."""
    return {
        entry_point.name: entry_point.load(require=False) for entry_point in iter_entry_points('curent.stream')
    }
