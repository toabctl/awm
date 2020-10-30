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


from enum import Enum
from typing import Optional, List, Tuple
import json
import datetime
from dateutil import parser


class ResultStatus(str, Enum):
    #: the crawler got a result. The response of that result can be any status
    #: code (including 404 and friends)
    SUCCESSFUL = 'SUCCESSFUL'
    #: the crawler ran into a timeout
    TIMEOUT = 'TIMEOUT'
    #: the crawler http client raised an error
    CLIENT_ERROR = 'CLIENT_ERROR'
    #: the crawler ran into an unknown error
    UNKNOWN_ERROR = 'UNKNOWN_ERROR'


class Result:
    """
    a crawler result

    :param url: the url the result is for
    :type url: str
    :param start_dt: the start datetime when the result collection started
    :type start_dt: datetime
    :param end_dt: the end datetime when the result collection finished
    :type end_dt: datetime or None
    :param response_status: the http response status code
    :type response_status: int or None
    :param response_regex_status: the status of the response regex check
    :type response_regex_status: bool or None
    :param status: the crawler result status
    :type status: :class:`ResultStatus`
    :param status_message: optional status message. Only used when status is not :attr:`ResultStatus.SUCCESSFUL`
    :type status_message: str or None
    """
    def __init__(self, url: str, start_dt: datetime.datetime, end_dt: Optional[datetime.datetime],
                 response_status: Optional[int], response_regex_status: Optional[bool],
                 status: ResultStatus, status_message: Optional[str]):
        self._url = url
        self._start_dt = start_dt
        self._end_dt = end_dt
        self._response_status = response_status
        self._response_regex_status = response_regex_status
        self._status = status
        self._status_message = status_message

    @property
    def url(self) -> str:
        return self._url

    @property
    def start_dt(self) -> datetime.datetime:
        return self._start_dt

    @property
    def end_dt(self) -> Optional[datetime.datetime]:
        return self._end_dt

    @property
    def duration(self) -> Optional[datetime.timedelta]:
        if self._start_dt and self._end_dt:
            return self._end_dt - self._start_dt
        return None

    @property
    def response_status(self):
        return self._response_status

    @property
    def response_regex_status(self):
        return self._response_regex_status

    @property
    def status(self) -> ResultStatus:
        return self._status

    @property
    def status_message(self) -> Optional[str]:
        return self._status_message

    @staticmethod
    def from_json(d):
        """create a :class:`Result` from json data
        :param d: the json data

        :return: a :class:`Result` instance
        :rtype: :class:`Result`
        """
        start_dt = parser.parse(d['start_dt'])
        end_dt = None
        if d['end_dt']:
            end_dt = parser.parse(d['end_dt'])

        return Result(d['url'], start_dt, end_dt,
                      d['response_status'], d['response_regex_status'],
                      d['status'], d['status_message'])

    def as_json(self) -> str:
        """serialize :class:`Result` as json

        :return: a json string
        :rtype: str
        """
        return json.dumps({
            'url': self._url,
            'start_dt': self._start_dt,
            'end_dt': self._end_dt,
            'duration': self.duration,
            'response_status': self.response_status,
            'response_regex_status': self.response_regex_status,
            'status': self._status,
            'status_message': self._status_message,
        }, default=str)

    def sql(self) -> Tuple[str, List]:
        """get a SQL statement and the needed arguments

        :return: a tuple with the sql statement and the needed arguments
        :rtype: (str, list)
        """
        # INFO: remember https://www.psycopg.org/docs/usage.html#the-problem-with-the-query-parameters
        if self.status == ResultStatus.SUCCESSFUL:
            sql = """INSERT INTO crawler_results(url, start_time, end_time, response_time, response_status, response_regex_status, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s);"""
            sql_args = [self.url, self.start_dt, self.end_dt, self.duration,
                        self.response_status, self.response_regex_status, self.status]
            return (sql, sql_args)
        else:
            sql = """INSERT INTO crawler_results(url, start_time, status, status_message)
            VALUES (%s, %s, %s, %s);"""
            sql_args = [self.url, self.start_dt, self.status, self.status_message or '']
            return (sql, sql_args)

    def __repr__(self):
        msg = f'{self._url} ({self._status})'
        if self._status == ResultStatus.SUCCESSFUL:
            msg += f' took {self.duration} s'
        else:
            msg += f': {self._status_message}'
        return msg

    def __eq__(self, other):
        if isinstance(other, Result):
            return self.url == other.url and \
                self.start_dt == other.start_dt and \
                self.end_dt == other.end_dt and \
                self.response_status == other.response_status and \
                self.response_regex_status == other.response_regex_status and \
                self.status == other.status and \
                self.status_message == other.status_message
        return False
