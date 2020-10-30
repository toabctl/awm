# Copyright (c) 2020 Thomas Bechtold <thomasbechtold@jpberlin.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context


logger = logging.getLogger(__name__)


def _kafka_ssl(sslconf: Dict):
    ret = {}
    if sslconf.get('enabled', False):
        context = create_ssl_context(
            cafile=sslconf['cafile'],
            certfile=sslconf['certfile'],
            keyfile=sslconf['keyfile'],
            password=sslconf['password'],
        )
        ret['security_protocol'] = 'SSL'
        ret['ssl_context'] = context
    return ret


@asynccontextmanager
async def kafka_producer(servers: str, sslconf: Dict):
    kwargs = {
        'loop': asyncio.get_event_loop(),
        'bootstrap_servers': servers,
        'client_id': 'awm'
    }
    kwargs.update(_kafka_ssl(sslconf))

    producer = AIOKafkaProducer(**kwargs)
    try:
        await producer.start()
        logging.info(f'kafka producer started ({servers})')
        yield producer
    finally:
        await producer.stop()


@asynccontextmanager
async def kafka_consumer(servers: str, topics: List[str], group_id: str, sslconf: Dict):
    kwargs = {
        'loop': asyncio.get_event_loop(),
        'bootstrap_servers': servers,
        'client_id': 'awm',
        'group_id': group_id,
    }
    kwargs.update(_kafka_ssl(sslconf))
    consumer = AIOKafkaConsumer(*topics, **kwargs)
    try:
        await consumer.start()
        logging.info(f'kafka consumer started ({servers})')
        yield consumer
    finally:
        await consumer.stop()
