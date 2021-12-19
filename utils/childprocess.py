#!/usr/bin/env python
__FILENAME__="childprocess.py"
__AUTHOR__="David Wettstein"
__VERSION__="1.0.2"
__COPYRIGHT__="Copyright (c) 2018-2021 %s" % (__AUTHOR__)
__LICENSE__="MIT License (https://dwettstein.mit-license.org/)"
__LINK__="https://github.com/dwettstein/PythonStuff"
__DESCRIPTION__=(
    "This module contains utility functions for child process handling."
)
# Changelog:
# - v1.0.2, 2021-12-19, David Wettstein: Refactor header part.
# - v1.0.1, 2018-11-29, David Wettstein: Add stdin to subprocess.
# - v1.0.0, 2018-11-26, David Wettstein: Initial module.


import subprocess


def execute(process_args: list) -> tuple:
    """
    Open a new child process and execute the given arguments.

    Args:
        process_args: A list of process arguments
            (e.g. [powershell_exe_path, script_path]).

    Returns:
        A tuple containing the process output, error and return code.
        If no output or error is available, empty strings will be sent.

        (_out, _err, _ret)

    Raises:
        OSError: An OS error happend, e.g. the file was not found.
        ValueError: The function was called with invalid arguments.
        subprocess.SubprocessError: Another error occurred.
    """
    _process = subprocess.Popen(
        process_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    _out, _err = _process.communicate()

    if not _out:
        _out = ""
    if not _err:
        _err = ""
    _ret = _process.returncode
    return (_out, _err, _ret)
