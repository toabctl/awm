#!/usr/bin/python3
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


"""
Persist awm messages from a kafka topic in a database
"""

import asyncio
import argparse
from pathlib import Path
import logging
import aiopg
import json

from ..common import config
from ..common import kafka_utils
from ..common import result

logger = logging.getLogger(__name__)


async def _db_create_table(cur):
    """create the DB table if it does not already exist"""
    sql = f"""
    DO $$ BEGIN
    CREATE TYPE result_status AS ENUM (
    '{result.ResultStatus.SUCCESSFUL}',
    '{result.ResultStatus.TIMEOUT}',
    '{result.ResultStatus.CLIENT_ERROR}',
    '{result.ResultStatus.UNKNOWN_ERROR}');
    EXCEPTION
    WHEN duplicate_object THEN null;
    END $$;
    """
    await cur.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS crawler_results (
    url VARCHAR(255) NOT NULL,
    start_time timestamp NOT NULL,
    end_time timestamp,
    response_time interval,
    response_status SMALLINT,
    response_regex_status BOOLEAN,
    status result_status NOT NULL,
    status_message text
    );"""
    await cur.execute(sql)
    logger.info('database table setup done')


async def _consume(conf):
    async with aiopg.create_pool(conf['persister']['postgres']['uri']) as pool:
        async with pool.acquire() as conn:
            # prepare database first
            async with conn.cursor() as cur:
                await _db_create_table(cur)

            async with kafka_utils.kafka_consumer(
                    conf['kafka']['servers'], [conf['kafka']['topic_name']],
                    'awm-group-1', conf['kafka']['ssl']) as consumer:
                # FIXME: make this more rubust - in case there is an exception, the whole persister crashs
                async for msg in consumer:
                    logger.debug(f'consumed kafka msg: {msg.topic}, partition: {msg.partition}, '
                                 f'offset: {msg.offset}, key: {msg.key}, val: {msg.value}, offset: {msg.offset}')
                    res = result.Result.from_json(json.loads(msg.value.decode()))
                    sql, sql_args = res.sql()
                    async with conn.cursor() as cur:
                        logger.debug(f'executing sql: {cur.mogrify(sql, (sql_args))}')
                        await cur.execute(sql, (sql_args))


def _parser():
    parser = argparse.ArgumentParser(
        description='Persist messages from kafka to the database')
    parser.add_argument('-d', '--debug', help="set loglevel to DEBUG",
                        action="store_const", dest="loglevel", const=logging.DEBUG,
                        default=logging.WARNING)
    parser.add_argument('-v', '--verbose', help="set loglevel to INFO",
                        action="store_const", dest="loglevel", const=logging.INFO)
    parser.add_argument('-c', '--config', help="path to the config file. Default: %(default)s",
                        default=f'{Path.home()}/.config/awm/config.json')
    return parser


def main():
    """main entry point for the persister service.
    This is used by the executable `awm-persister`
    """
    parser = _parser()
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    conf = config.get_config(args.config)
    asyncio.run(_consume(conf))


# for debugging
if __name__ == "__main__":
    main()
