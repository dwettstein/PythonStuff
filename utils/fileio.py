#!/usr/bin/env python
# -----------------------------------------------------------------------------
# This module contains utility functions for file IO handling.
#
#   File-Name:  fileio.py
#   Author:     David Wettstein
#   Version:    v1.0.1
#   License:    Copyright (c) 2018-2020 David Wettstein,
#               licensed under the MIT License
#               (https://dwettstein.mit-license.org/)
#   Link:       https://github.com/dwettstein
#
#   Changelog:
#               v1.0.1, 2020-11-29, David Wettstein: Improve linting.
#               v1.0.0, 2018-11-26, David Wettstein: Initial module.
# -----------------------------------------------------------------------------
import base64
import csv


LOG = True
DEBUG = False


def write_file(filename: str, content: str) -> str:
    """
    Write content to a given file.

    Args:
        filename: The path to the file you want to write.

    Returns:
        The file content as a string.

    Raises:
        ValueError
    """
    try:
        with open(filename, "w") as opened_file:
            _content = content.rstrip("\n")  # Remove empty line at the end.
            _content = opened_file.write(_content)
        return True
    except Exception as ex:
        if LOG:
            print("Failed to write file %s. Exception: %s" % (
                filename, str(ex)))
        raise  # Re-throw catched exception.


def read_file(filename: str) -> str:
    """
    Read a given file.

    Args:
        filename: The path to the file you want to read.

    Returns:
        The file content as a string.

    Raises:
        ValueError
    """
    try:
        with open(filename, "r") as opened_file:
            _content = opened_file.read()
            _content = _content.rstrip("\n")  # Remove empty line at the end.
        return _content
    except Exception as ex:
        if LOG:
            print("Failed to read file %s. Exception: %s" % (
                filename, str(ex)))
        raise  # Re-throw catched exception.


def read_base64_content(filename: str) -> str:
    """
    Read and decode the Base64 content of a given file.

    An example file can be created with the following Bash code:
    (echo "changeme" | base64) > your_filename

    Args:
        filename: The path to the file you want to read.

    Returns:
        The decoded file content as a string.

    Raises:
        ValueError
        binascii.Error
    """
    try:
        _content_b64 = read_file(filename)
        _content = base64.b64decode(_content_b64).decode("utf-8")
        _content = _content.rstrip("\n")  # Remove empty line at the end.
        return _content
    except Exception as ex:
        if LOG:
            print("Failed to read file %s. Exception: %s" % (
                filename, str(ex)))
        raise  # Re-throw catched exception.


def read_csv(path: str,
             newline: str = "",
             delimiter: str = ",",
             quotechar: str = None) -> list:
    """
    Read a CSV file.

    Args:
        path: The path to the file you want to read.
        newline: The newline character, default is ''.
        delimiter: The CSV content delimiter, default is ','.
        quotechar: A char used to quote fields containing special characters,
            default is None.

    Returns:
        A list containing each CSV row as a list of strings.

    Raises:
    """
    items = []
    with open(path, newline=newline) as csvfile:
        csv_reader = csv.reader(csvfile,
                                delimiter=delimiter,
                                quotechar=quotechar)
        for row in csv_reader:
            items.append(row)
    return items
