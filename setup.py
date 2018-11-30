#!/usr/bin/env python
"""Packaging logic for burak-stream."""

import versioneer  # noqa
from setuptools import setup  # noqa

setup(
    name='burak-stream',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="burak stream library",
    author='Burak Demirtas',
    author_email='demirtas.burakk@gmail.com',
    url='',
    packages=[
        'burak.stream'
    ],
    install_requires=[
        'attrs >= 18.1.0',
        'confluent-kafka >= 0.11.4',
        'redis >= 2.10.6',
    ],
    entry_points={
        'imagia.stream': [
            'kafka = burak.stream.kafka:KafkaStream',
            'redis = burak.stream.redis:RedisStream',
        ],
    },
)
