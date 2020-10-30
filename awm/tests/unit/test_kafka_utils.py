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


from unittest.mock import patch
import pytest
from awm.common import kafka_utils


@pytest.mark.parametrize(
    'sslconf,expected',
    [
        ({'enabled': True, 'cafile': 'cafile', 'certfile': 'certfile', 'keyfile': 'keyfile', 'password': 'password'},
         {'security_protocol': 'SSL', 'ssl_context': 'None'}),
        ({}, {}),
        ({'enabled': False}, {})
    ])
@patch('awm.common.kafka_utils.create_ssl_context', return_value='None')
def test__kafka_ssl(create_ssl_context_patch, sslconf, expected):
    assert kafka_utils._kafka_ssl(sslconf) == expected
