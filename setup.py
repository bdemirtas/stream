#!/usr/bin/env python
"""Packaging logic for curent-stream."""

import versioneer  # noqa
from setuptools import setup  # noqa

setup(
    name='curent-stream',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="curent stream library",
    author='Burak Demirtas',
    author_email='demirtas.burakk@gmail.com',
    url='',
    packages=[
        'curent.stream'
    ],
    install_requires=[
        'attrs >= 18.1.0',
        'confluent-kafka >= 0.11.4',
        'redis >= 2.10.6',
    ],
    entry_points={
        'curent.stream': [
            'kafka = curent.stream.kafka:KafkaStream',
            'redis = curent.stream.redis:RedisStream',
        ],
    },
)
