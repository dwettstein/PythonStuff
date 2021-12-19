#!/usr/bin/env python
__FILENAME__="template_api_client.py"
__AUTHOR__="David Wettstein"
__VERSION__="0.0.1"
__COPYRIGHT__="Copyright (c) 2018-2021 %s" % (__AUTHOR__)
__LICENSE__="MIT License (https://dwettstein.mit-license.org/)"
__LINK__="https://github.com/dwettstein/PythonStuff"
__DESCRIPTION__=("This is a template for Python API clients.")
# Changelog:
# - v0.0.1, yyyy-mm-dd, David Wettstein: First implementation.


from enum import Enum
import os
import sys


FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
sys.path.insert(1, os.path.join(FILE_DIR, ".."))  # Add parent dir to path

# pylint: disable=import-error,wrong-import-position
from utils.webrequest import WebRequester
from utils.webrequest import UnauthorizedException


class Endpoints(Enum):
    AUTHENTICATION = "/api/api-token-auth/"
    AUTHENTICATION_REFRESH = "/api/api-token-refresh/"
    RESOURCE = "/api/resource/"


class Client(object):
    """
    A simple client for an API.

    Args:
        base_url: str: The base URL of the API.
        username: str: The username used for authentication.
        password: str: The password used for authentication.
        verify_ssl_certs: bool: If true, validate server certificates.
            Set to false to allow self-signed certificates.

    Returns:
        The API client for the given URL.
    """

    def __init__(self,
                 base_url: str,
                 username: str,
                 password: str,
                 use_session: bool = True,
                 verify_ssl_certs: bool = True,
                 disable_warnings: bool = False,
                 log_file: str = None,
                 log_print: bool = False,
                 log_requests: bool = False,
                 log_headers: bool = False,
                 log_bodies: bool = False):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._token = None
        self._log_print = log_print
        self._webrequester = WebRequester(self._base_url,
                                          use_session=use_session,
                                          verify_ssl_certs=verify_ssl_certs,
                                          disable_warnings=disable_warnings,
                                          log_file=log_file,
                                          log_print=log_print,
                                          log_requests=log_requests,
                                          log_headers=log_headers,
                                          log_bodies=log_bodies)
        self._webrequester.set_default_headers({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        })

    def _get_token(self) -> str:
        return self.__get_or_refresh_token(Endpoints.AUTHENTICATION)

    def _refresh_token(self) -> str:
        return self.__get_or_refresh_token(Endpoints.AUTHENTICATION_REFRESH)

    def __get_or_refresh_token(self, endpoint: Endpoints):
        if endpoint.value == Endpoints.AUTHENTICATION.value:
            json_body = {
                "username": self._username,
                "password": self._password,
            }
        elif endpoint.value == Endpoints.AUTHENTICATION_REFRESH.value:
            json_body = {
                "token": self._token,
            }
        else:
            raise Exception("Unknown token endpoint: %s" % (endpoint.value))
        _output = self._webrequester.invoke_and_handle(
            "POST",
            endpoint.value,
            json=json_body)
        if "token" not in _output:
            raise Exception("Failed to get or refresh token: %s\n" % (_output))
        self._token = _output["token"]
        self._webrequester.set_authorization("Token",
                                             username=self._username,
                                             password=self._password,
                                             token=("Bearer " + self._token))
        return self._token

    def get_resource(self,
                     resource="",
                     params: dict = None,
                     as_dict: bool = False) -> object:
        """
        Get all or a specific resource.

        Args:
            resource: int/str: An optional resource id or URL suffix to
                request.
            params: str: Optional URL query string params.
            as_dict: bool: If true, return resources as a dict.

        Returns:
            The existing resources as a list (default) or as a
            dict.
        """
        if not self._token:
            self._token = self._get_token()
        _output = None
        try:
            _output = self._webrequester.invoke_and_handle(
                "GET",
                Endpoints.RESOURCE.value + str(resource),
                params=params)
        except Exception as ex:
            if self._log_print:
                print("Failed to get resource(s) "
                      "using params `%s`. Exception: %s"
                      % (str(params) if params else "", repr(ex)))
            if isinstance(ex, UnauthorizedException):
                self._token = None  # Likely, the token has expired.
            raise
        if as_dict:
            _output = {(_item["key"] if "key" in _item else _item["name"]):
                       _item for _item in _output}
        return _output
