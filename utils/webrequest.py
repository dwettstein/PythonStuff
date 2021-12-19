#!/usr/bin/env python
__FILENAME__="webrequest.py"
__AUTHOR__="David Wettstein"
__VERSION__="2.0.4"
__COPYRIGHT__="Copyright (c) 2018-2021 %s" % (__AUTHOR__)
__LICENSE__="MIT License (https://dwettstein.mit-license.org/)"
__LINK__="https://github.com/dwettstein/PythonStuff"
__DESCRIPTION__=(
    "A module providing utility classes and functions for web request "
    "handling."
)
# Changelog:
# - v2.0.4, 2021-12-19, David Wettstein: Refactor header part and fix typos.
# - v2.0.3, 2020-11-29, David Wettstein: Improve linting.
# - v2.0.2, 2020-04-27, David Wettstein: Add attr _fqdn.
# - v2.0.1, 2019-08-08, David Wettstein: Return a tuple optionally.
# - v2.0.0, 2019-01-19, David Wettstein: Complete refactoring.
# - v1.0.0, 2018-11-24, David Wettstein: Initial module.


import logging
import re

import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests.exceptions import RequestException


class WebRequester(object):
    """
    A general helper class to create simple-to-use web API clients using the
    requests package (http://docs.python-requests.org).

    Args:
        base_url: str: The base URL of the web API.
        use_session: bool: If true, a requests session will be used.
        verify_ssl_certs: bool: If true, validate server certificates.
            Set to false to allow self-signed certificates.
        disable_warnings: bool: If true, disables all warning messages from
            urllib3 package.
        log_file: str: If file logging is needed, set a log file here.
        log_print: bool: If true, logging with print statements is enabled.
        log_requests: bool: If true, all requests will be logged.
        log_headers: bool: If true, all headers will be logged (pay attention
            with passwords).
        log_bodies: bool: If true, all bodies will be logged.

    Returns:
        The WebRequester instance for the given URL.
    """

    def __init__(self,
                 base_url: str,
                 use_session: bool = False,
                 verify_ssl_certs: bool = True,
                 disable_warnings: bool = False,
                 log_file: str = None,
                 log_print: bool = False,
                 log_requests: bool = False,
                 log_headers: bool = False,
                 log_bodies: bool = False):
        if base_url[-1] == "/":
            self._base_url = base_url[:-1]
        else:
            self._base_url = base_url
        self._fqdn = re.sub(r"^http(s)?://(www\.)?", "", self._base_url)
        if not re.search(r"^http(s)?://", self._base_url):
            self._base_url = "https://" + self._base_url
        self._username = None
        self._password = None
        self._auth = None
        self._token = None
        self._token_header = None
        self._headers = None
        self._use_session = use_session
        self._verify_ssl_certs = verify_ssl_certs
        self._disable_warnings = disable_warnings
        if self._use_session:
            self._session = requests.Session()
            self._session.verify = self._verify_ssl_certs
        else:
            self._session = None

        if self._disable_warnings:
            # from urllib3.exceptions import InsecureRequestWarning
            # requests.packages.urllib3.disable_warnings(
            #     category=InsecureRequestWarning)
            # pylint: disable=E1101
            requests.packages.urllib3.disable_warnings()

        self._logger = Logger(log_file=log_file,
                              log_print=log_print,
                              log_requests=log_requests,
                              log_headers=log_headers,
                              log_bodies=log_bodies)

    def set_default_headers(self,
                            headers: dict):
        """
        Set the default headers to use with every request
        (previously set headers will be replaced).

        Args:
            headers: dict: All headers to set as a dict.
        """
        self._headers = headers
        if self._use_session:
            self._session.headers = self._headers

    def set_authorization(self,
                          auth_type: str,
                          username: str = None,
                          password: str = None,
                          token: str = None,
                          token_header: str = "Authorization"):
        """
        Set the authorization to use with every request.

        Args:
            auth_type: str: The kind of authorization to use
                (one of `Basic`, `Digest` or `Token`).
            username: str: The username for Basic or Digest authorization.
            password: str: The password for Basic or Digest authorization.
            token: str: The token for Token authorization.
            token_header: str: The header name used for Token authorization
                (default is `Authorization`).
        """
        self._username = username
        self._password = password
        self._token = token
        self._token_header = token_header

        if auth_type.lower() == "basic":
            self._auth = HTTPBasicAuth(self._username, self._password)
        elif auth_type.lower() == "digest":
            self._auth = HTTPDigestAuth(self._username, self._password)
        elif auth_type.lower() == "token":
            self._headers.update({self._token_header: self._token})

        if self._use_session:
            if self._auth:
                self._session.auth = self._auth
            elif self._token:
                self._session.headers.update({self._token_header: self._token})

    def close_session(self):
        """Close the session if one was used."""
        if self._session:
            self._session.close()
            self._session = None

    def invoke(self,
               method: str,
               endpoint: str,
               headers: dict = None,
               params: dict = None,
               data: str = None,
               json=None) -> requests.Response:
        """
        Invoke an endpoint of the web API with given HTTP method.

        Args:
            method: str: The HTTP method for the request.
            endpoint: str: The endpoint to request.
            headers: dict: A dict of additional headers for this request
                (e.g. `{"Accept": "application/json"}`), default is `None`.
            params: dict: A dict of URL query string data
                (e.g. `{"key": "value"}`), default is `None`.
            data: str: The request body as string, use either data or json,
                default is `None`.
            json: object: The request body as object, use either data or json,
                default is `None`.

        Returns:
            The response of the request as `requests.Response` object.

        Raises:
            requests.exceptions.RequestException:
                An ambiguous exception raised by requests package.
        """

        if endpoint.startswith("/"):
            url = self._base_url + endpoint
        else:
            url = self._base_url + "/" + endpoint

        request_headers = self._headers.copy() if self._headers else {}
        if headers:
            request_headers.update(headers)

        self._logger.log_request(url=url,
                                 method=method,
                                 headers=request_headers,
                                 body=(data if data else json))

        if self._session:
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json)
        else:
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                json=json)

        self._logger.log_response(response=response)

        return response

    def invoke_and_handle(self,
                          method: str,
                          endpoint: str,
                          headers: dict = None,
                          params: dict = None,
                          data: str = None,
                          json=None,
                          decode_response: bool = True,
                          as_tuple: bool = False):
        """
        Invoke an endpoint of the web API with given HTTP method and handle
        the response.

        Args:
            method: str: The HTTP method for the request.
            endpoint: str: The endpoint to request.
            headers: dict: A dict of additional headers for this request
                (e.g. `{"Accept": "application/json"}`), default is `None`.
            params: dict: A dict of URL query string data
                (e.g. `{"key": "value"}`), default is `None`.
            data: str: The request body as string, use either data or json,
                default is `None`.
            json: object: The request body as JSON, use either data or json,
                default is `None`.
            decode_response: bool: If true, decodes the response content,
                else the content will be returned as is (e.g. for XML),
                default is `True`.
            as_tuple: bool: If true, returns the response as a tuple in
                the following format: `(status_code, headers, data)`,
                default is `False`.

        Returns:
            The response content as an object or if not possible as text.
            If argument `decode_response` is set to `False`, the content is
            returned as is (e.g. for XML).

            If argument `as_tuple` is set to `True`,
            a tuple `(status_code, headers, data)` is returned.

        Raises:
            requests.exceptions.RequestException:
                An ambiguous exception raised by requests package.
            webrequest.WebRequestResponseException:
                An ambiguous exception depending on the response status code.
        """
        response = self.invoke(method=method,
                               endpoint=endpoint,
                               headers=headers,
                               params=params,
                               data=data,
                               json=json)
        if response.ok:
            response_data = ""
            if response.status_code != 204:
                if decode_response:
                    try:
                        response_data = response.json()
                    except Exception:
                        response_data = response.text
                else:
                    response_data = response.content
            if as_tuple:
                return response.status_code, response.headers, response_data
            return response_data
        else:
            status_code_to_exception(response.status_code, response=response)


class Logger(object):
    """
    A helper class for logging web requests and responses.

    Args:
        log_file: str: If file logging is needed, set a log file here.
        log_print: bool: If true, logging with print statements is enabled.
        log_requests: bool: If true, all requests will be logged.
        log_headers: bool: If true, all headers will be logged (pay attention
            with passwords).
        log_bodies: bool: If true, all bodies will be logged.
    """

    def __init__(self,
                 log_file: str = None,
                 log_print: bool = False,
                 log_requests: bool = False,
                 log_headers: bool = False,
                 log_bodies: bool = False):
        self._log_file = log_file
        self._log_print = log_print
        self._log_requests = log_requests
        self._log_headers = log_headers
        self._log_bodies = log_bodies

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        # This makes sure that we don't append a new handler to the logger
        # every time we create a new client.
        if not self._logger.handlers:
            if log_file is not None:
                handler = logging.FileHandler(log_file)
            else:
                handler = logging.NullHandler()
            formatter = logging.Formatter("%(asctime)s | "
                                          "%(levelname)s | "
                                          "%(name)s | "
                                          "%(module)s | "
                                          "%(funcName)s | "
                                          "%(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def log_request(self,
                    url: str,
                    method: str,
                    headers: dict = None,
                    body=None):
        if not self._log_requests:
            return

        self._log("Invoking %s %s" % (method, url))

        if self._log_headers:
            self._log("Request headers: %s" % (str(headers)))

        if self._log_bodies and body:
            if isinstance(body, bytes):
                body = body.decode(errors="ignore")
            self._log("Request body: %s" % (str(body)))

    def log_response(self,
                     response: requests.Response,
                     skip_body: bool = False):
        if not self._log_requests:
            return

        self._log("Response status code: %s" % (response.status_code))

        if self._log_headers:
            self._log("Response headers: %s" % (response.headers))

        if self._log_bodies and not skip_body and response.text:
            self._log("Response body: %s" % (response.text))

    def _log(self, msg: str):
        if self._log_print:
            print(msg)
        self._logger.debug(msg)


def status_code_to_exception(status_code, *args, **kwargs):
    """
    Raise a proper exception depending on the HTTP status code.

    Args:
        status_code: The HTTP status code for the exception.

    Raises:
        webrequest.WebRequestResponseException:
            An ambiguous exception depending on the response status code.
    """
    if status_code == 400:
        raise BadRequestException(status_code, *args, **kwargs)
    if status_code == 401:
        raise UnauthorizedException(status_code, *args, **kwargs)
    if status_code == 403:
        raise AccessForbiddenException(status_code, *args, **kwargs)
    if status_code == 404:
        raise NotFoundException(status_code, *args, **kwargs)
    if status_code == 405:
        raise MethodNotAllowedException(status_code, *args, **kwargs)
    if status_code == 406:
        raise NotAcceptableException(status_code, *args, **kwargs)
    if status_code == 408:
        raise RequestTimeoutException(status_code, *args, **kwargs)
    if status_code == 409:
        raise ConflictException(status_code, *args, **kwargs)
    if status_code == 415:
        raise UnsupportedMediaTypeException(status_code, *args, **kwargs)
    if status_code == 416:
        raise InvalidContentLengthException(status_code, *args, **kwargs)
    if status_code == 500:
        raise InternalServerException(status_code, *args, **kwargs)
    if status_code == 503:
        raise ServiceUnavailableException(status_code, *args, **kwargs)
    raise WebRequestResponseException(status_code, *args, **kwargs)


class WebRequestException(RequestException):
    """Base class for all webrequest exceptions."""


class WebRequestResponseException(WebRequestException):
    """Base class for all webrequest response related exceptions."""

    def __init__(self, status_code, *args, **kwargs):
        self.status_code = status_code
        self.response = kwargs.get("response", None)
        self.request = kwargs.get("request", None)
        if (self.response is not None and not self.request and
                hasattr(self.response, "request")):
            self.request = self.response.request
        super(WebRequestResponseException, self).__init__(*args, **kwargs)

    def __str__(self):
        if self.response is not None and self.response.text:
            msg = "%d - %s" % (self.status_code, self.response.text)
        else:
            msg = str(self.status_code)
        return msg


class BadRequestException(WebRequestResponseException):
    """Raised when response status code was 400."""


class UnauthorizedException(WebRequestResponseException):
    """Raised when response status code was 401."""


class AccessForbiddenException(WebRequestResponseException):
    """Raised when response status code was 403."""


class NotFoundException(WebRequestResponseException):
    """Raised when response status code was 404."""


class MethodNotAllowedException(WebRequestResponseException):
    """Raised when response status code was 405."""


class NotAcceptableException(WebRequestResponseException):
    """Raised when response status code was 406."""


class RequestTimeoutException(WebRequestResponseException):
    """Raised when response status code was 408."""


class ConflictException(WebRequestResponseException):
    """Raised when response status code was 409."""


class InvalidContentLengthException(WebRequestResponseException):
    """Raised when response status code was 411."""


class UnsupportedMediaTypeException(WebRequestResponseException):
    """Raised when response status code was 415."""


class InternalServerException(WebRequestResponseException):
    """Raised when response status code was 500."""


class ServiceUnavailableException(WebRequestResponseException):
    """Raised when response status code was 503."""
