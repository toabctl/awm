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
Periodically monitor website status and publish to kafka
"""


from pathlib import Path
import argparse
import datetime
import logging
import time
import asyncio
import aiohttp
import re
from typing import Optional

from ..common import config
from ..common import kafka_utils
from ..common.result import Result, ResultStatus

logger = logging.getLogger(__name__)


def _response_regex_status(regex: Optional[str], response_text: str) -> Optional[bool]:
    response_regex_status = None
    if regex:
        match = re.search(r'{}'.format(regex), response_text)
        if match:
            response_regex_status = True
        else:
            response_regex_status = False
    return response_regex_status


async def _fetch_url(session: aiohttp.ClientSession, url: str, response_regex: Optional[str]) -> Result:
    """
    Fetch the given url and get status
    """
    start = datetime.datetime.now(datetime.timezone.utc)
    try:
        async with session.get(url) as response:
            response_text = await response.text()
    except aiohttp.client_exceptions.ClientConnectorError as e:
        logger.warning(f'{url}: connection error: {str(e)}')
        return Result(url, start, None, None, None, ResultStatus.CLIENT_ERROR, str(e))
    except asyncio.exceptions.TimeoutError as e:
        logger.warning(f'{url}: timeout after {session.timeout}s')
        return Result(url, start, None, None, None, ResultStatus.TIMEOUT, str(e))
    except Exception as e:
        logger.exception(e)
        return Result(url, start, None, None, None, ResultStatus.UNKNOWN_ERROR, str(e))
    else:
        end = datetime.datetime.now(datetime.timezone.utc)

        return Result(url, start, end, response.status, _response_regex_status(response_regex, response_text),
                      ResultStatus.SUCCESSFUL, None)


async def _handle_url(conf, kafka_producer, session: aiohttp.ClientSession, url: str):
    # allow to override the check interval on a url base
    interval = conf['crawler']['urls'][url].get('interval', conf['crawler']['interval'])
    while True:
        start = time.time()
        try:
            res = await asyncio.create_task(_fetch_url(session, url, conf['crawler']['urls'][url].get('regex')))
            await kafka_producer.send(conf['kafka']['topic_name'], res.as_json().encode())
        except Exception as e:
            logging.exception(e)
        else:
            logger.info(res)
        wait_for = max(0, interval - (time.time() - start))
        logger.info(f'waiting {wait_for:.2f} s before checking {url} again...')
        await asyncio.sleep(wait_for)


async def _crawl(conf):
    async with kafka_utils.kafka_producer(conf['kafka']['servers'], conf['kafka']['ssl']) as producer:
        # make sure the check doesn't need longer than configured check interval
        timeout = aiohttp.ClientTimeout(total=conf['crawler']['interval'])
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for url, url_conf in conf['crawler']['urls'].items():
                tasks.append(asyncio.create_task(_handle_url(conf, producer, session, url), name=url))
            logger.info(f'scheduled {len(tasks)} tasks...')
            await asyncio.gather(*tasks)


def _parser():
    parser = argparse.ArgumentParser(
        description='Periodically monitor website status and publish to kafka')
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
    asyncio.run(_crawl(conf))


# for debugging
if __name__ == "__main__":
    main()
