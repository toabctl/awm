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
import aiohttp
import pytest
from aioresponses import aioresponses

from awm import crawler
from awm.common import result


@pytest.mark.parametrize(
    'mock_response_code,mock_body,mock_raise,expected_result_status',
    [
        (200, None, None, result.ResultStatus.SUCCESSFUL),
        (200, 'some body', None, result.ResultStatus.SUCCESSFUL),
        (404, None, None, result.ResultStatus.SUCCESSFUL),
        (404, 'こんにちは', None, result.ResultStatus.SUCCESSFUL),
        (200, None, aiohttp.client_exceptions.ClientConnectorError(
            aiohttp.client_reqrep.ConnectionKey("localhost", 80, False, None, None, None, None), OSError()),
         result.ResultStatus.CLIENT_ERROR),
        (200, None, Exception(), result.ResultStatus.UNKNOWN_ERROR),
        (200, None, OSError(), result.ResultStatus.UNKNOWN_ERROR),
        (200, None, asyncio.exceptions.TimeoutError(), result.ResultStatus.TIMEOUT),
    ]
)
@pytest.mark.asyncio
async def test__fetch_url(mock_response_code, mock_body, mock_raise, expected_result_status):
    mock_args = {}
    if mock_response_code:
        mock_args['status'] = mock_response_code
    if mock_raise:
        mock_args['exception'] = mock_raise
    if mock_body:
        mock_args['body'] = mock_body

    url = 'https://localhost'
    with aioresponses() as m:
        m.get(url, **mock_args)
        async with aiohttp.ClientSession() as session:
            res = await crawler._fetch_url(session, url, None)
            assert res.status == expected_result_status
            # do some extra checks depending on the CrawlerResultStatus
            if res.status == result.ResultStatus.SUCCESSFUL:
                assert res.start_dt is not None
                assert res.duration is not None
                assert res.status_message is None
            else:
                # there was an exception, status_message should be there
                assert res.status_message is not None


@pytest.mark.parametrize(
    'regex,text,expected_result',
    [
        (None, '', None),
        ('', '', None),
        ('.*', 'foobar', True),
        ('.*foobar.*', 'foobar', True),
        ('.*にち.*', 'こんにちは', True),
        ('test', 'foobar', False),
        ('^foobar.*', 'bar foobar', False),
    ])
def test__response_regex_status(regex, text, expected_result):
    assert crawler._response_regex_status(regex, text) == expected_result
