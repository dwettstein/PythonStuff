#!/usr/bin/env python
# -----------------------------------------------------------------------------
# This is a template for Python scripts.
#
#   File-Name:  template.py
#   Author:     David Wettstein
#   Version:    v0.0.1
#   License:    Copyright (c) 2018-2020 David Wettstein,
#               licensed under the MIT License
#               (https://dwettstein.mit-license.org/)
#   Link:       https://github.com/dwettstein
#
#   Changelog:
#               v0.0.1, yyyy-mm-dd, David Wettstein: First implementation.
# -----------------------------------------------------------------------------
import argparse
import configparser
import getpass
import os
import re
import sys
from string import Template


FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
# sys.path.insert(1, os.path.join(FILE_DIR, ".."))  # Add parent dir to path

# pylint: disable=import-error,wrong-import-position


def function(param, another_param):
    """
    Description

    Args:
        param: Whatever this parameter is.
        another_param: Bla bla bla.

    Returns:
        Description of what is returned and how it possibly looks like.

    Raises:
        IOError: An error occurred accessing the xy object.
    """
    pass


def process_arguments():
    _argparser = argparse.ArgumentParser(
        description="Describe what this script does.")
    _argparser.add_argument("-i", "--instance",
                            required=True,
                            help="The name of the API instance.")
    _argparser.add_argument("numbers",
                            metavar="n",
                            type=int,
                            nargs="+",
                            help="an integer for the accumulator")
    _argparser.add_argument("-s", "--sum",
                            action="store_const",
                            const=sum,
                            default=max,
                            dest="accumulate",
                            help="sum the integers (default: find the max)")
    _args = _argparser.parse_args()
    return _args


def get_credentials(args=None):
    if args and args.user:
        _user = args.user
    else:
        _user = getpass.getuser()
        _user_input = input("Please enter your username: [%s] " % _user)
        if _user_input:
            _user = _user_input
    print("Using username: %s" % _user)
    _pswd = getpass.getpass()
    return (_user, _pswd)


def load_config(path):
    _config = configparser.ConfigParser()
    _config.read(path)
    return _config


def confirm_execution():
    _confirmation = input("Are you sure you want to proceed? [y/N] ")
    if not re.search("^[yY]{1}(es)?$", _confirmation):
        print("Abort.")
        sys.exit()


def main():
    args = process_arguments()

    config = load_config(os.path.join(FILE_DIR, "template.ini"))
    base_url_draft = "%s://%s:%s" % (
        config.get("API", "protocol"),
        config.get("API", "fqdn"),
        config.get("API", "port"))
    base_url_template = Template(base_url_draft)
    base_url = base_url_template.substitute(subdomain=args.instance)
    print(base_url)

    (user, pswd) = get_credentials()

    confirm_execution()

    try:
        print(args.accumulate(args.numbers))
    except Exception as ex:
        # ex_type, ex_value, ex_traceback = sys.exc_info()
        print(repr(ex))
        raise


# Program entry point. Don't execute if imported.
if __name__ == "__main__":
    main()
