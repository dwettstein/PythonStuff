#!/usr/bin/env python
# -----------------------------------------------------------------------------
# This module contains utility functions for executing PowerShell scripts or
# code.
#
#   File-Name:  powershell.py
#   Author:     David Wettstein
#   Version:    v1.0.1
#   License:    Copyright (c) 2018-2020 David Wettstein,
#               licensed under the MIT License
#               (https://dwettstein.mit-license.org/)
#   Link:       https://github.com/dwettstein
#
#   Changelog:
#               v1.0.1, 2020-11-29, David Wettstein: Use -Command not -File.
#               v1.0.0, 2018-11-26, David Wettstein: Initial module.
# -----------------------------------------------------------------------------
import os

from . import childprocess


LOG = True
DEBUG = False


def execute_script(script_path: str,
                   script_inputs: list = None,
                   powershell_exe_path: str =
                   "C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\"
                   "powershell.exe",
                   execution_policy: str = "RemoteSigned") -> tuple:
    """
    Execute a PowerShell script.

    See also: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe

    Args:
        script_path: A string with the full path to a script.
        script_inputs: A list containing input parameters for the script
            (be aware of the order), default is None.
        powershell_exe_path: The path to the PowerShell exe, default is
            "C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe"
        execution_policy: The execution policy for PowerShell (only for
            Windows), default is "RemoteSigned". See here for more information:
            https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies

    Returns:
        A tuple containing the script output, error and return code.
        If no output or error is available, empty strings will be sent.

        (_out, _err, _ret)

    Raises:
    """
    if LOG:
        if DEBUG:
            print("Executing %s with inputs %s" % (
                script_path, str(script_inputs)))
        else:
            print("Executing %s" % (script_path))

    _process_args = [
        powershell_exe_path,
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
    ]
    if os.name == "nt":
        _process_args.extend(["-ExecutionPolicy", execution_policy])

    # Use -Command as -File doesn't work properly with begin, process, end blocks.
    _process_args.extend(["-Command", script_path])

    if script_inputs:
        # Add script inputs if any.
        # Surround with quotes if the input contains spaces and escape quotes within it.
        _process_args.extend(
            ["\"%s\"" % str(i).replace('"', '`"') if " " in i else i for i in script_inputs]
        )

    # Preserve a possible script specific exit code.
    _process_args.extend(["; exit $LASTEXITCODE"])

    try:
        if LOG and DEBUG:
            print(_process_args)
        (_out, _err, _ret) = childprocess.execute(_process_args)
        _out = _out.rstrip("\n")  # Remove empty line at the end.
        _err = _err.rstrip("\n")  # Remove empty line at the end.
    except Exception as ex:
        err_msg = ("Failed to execute PowerShell script with "
                   "args %s. Exception: %s" % (_process_args, str(ex)))
        if LOG:
            print(err_msg)
        _out = ""
        _err = err_msg

    if _err != "":
        _ret = 1

    if LOG and DEBUG:
        print("Script %s ended with exit code %s and result %s" % (
            script_path, _ret, (_err if _err else _out)))
    return (_out, _err, _ret)
