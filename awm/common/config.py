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
The config module is responsible to creating a config
dict from an available configuration file.
The configuration file needs to contain valid json.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict

from .exception import AwmConfigError


logger = logging.getLogger(__name__)


def get_config(config_path: Path) -> Dict:
    """Get a config dict from a configuration file
    The configuration file must be valid json

    :param config_path: the path to the config file
    :type config_path: Path

    :raises AwmConfigError: Raised when the file is not found or accessable or in an invalid format

    :return: the configuration dict
    :rtype: dict
    """
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            try:
                data = json.loads(f.read())
                logger.info(f'using config {config_path}')
                return data
            except Exception as e:
                logger.exception(e)
                raise AwmConfigError(f'unable to read config {config_path}')

    raise AwmConfigError(f'config file {config_path} not found')
