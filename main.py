from burak.stream import get_stream_factories


def listen():
    streams = get_stream_factories()
    stream = streams['redis']('127.0.0.1')
    with stream.subscribe(['test']) as subscriber:
        while True:
            message = subscriber.receive()
            print(message)


if __name__ == "__main__":
    listen()
