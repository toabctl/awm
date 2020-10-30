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


import datetime
import pytest
import json
from awm.common import result


start_dt = datetime.datetime(2020, 11, 1, 0, 0, 0)
end_dt = datetime.datetime(2020, 11, 1, 0, 0, 1)


@pytest.mark.parametrize(
    'url,start_dt,end_dt,response_status,response_regex_status,status,status_message',
    [
        ('http://localhost', start_dt, end_dt, None, None, result.ResultStatus.SUCCESSFUL, None)
    ])
def test_result_basics(url, start_dt, end_dt, response_status, response_regex_status, status, status_message):
    r = result.Result(url, start_dt, end_dt, response_status, response_regex_status, status, status_message)
    data = r.as_json()
    r_new = result.Result.from_json(json.loads(data))
    assert r == r_new


@pytest.mark.parametrize(
    'start_dt,end_dt,expected_duration',
    [
        (start_dt, end_dt, datetime.timedelta(seconds=1)),
        (start_dt, start_dt, datetime.timedelta(seconds=0)),
        (start_dt, None, None)
    ])
def test_result_duration(start_dt, end_dt, expected_duration):
    r = result.Result("http://localhost", start_dt, end_dt, None, None, result.ResultStatus.SUCCESSFUL, None)
    assert r.duration == expected_duration


def test_result_ro_properties():
    r = result.Result("http://localhost", start_dt, end_dt, None, None, result.ResultStatus.SUCCESSFUL, None)
    with pytest.raises(AttributeError):
        r.url = None
        r.start_dt = None
        r.end_date = None
        r.response_status = None
        r.response_regex_status = None
        r.status = None
        r.status_message = None
        r.duration = None
