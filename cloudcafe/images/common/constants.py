"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class HTTPResponseCodes(object):
    OK = 200
    FORBIDDEN = 403


class ImageProperties(object):
    ID_REGEX = ('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                '[0-9a-fA-F]{12}$')


class Messages(object):
    ERROR_MSG = 'Unexpected {0} value received. Expected: {1}, Received: {2}'
