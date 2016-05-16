#!/usr/bin/env python3

import argparse
from sessions import Session

""" TODO: handle errors if there's no arguments given """


def handle_arguments():
    """
    :return: commandline arguments
    """
    info = "usage: give port number and target host as commandline  arguments."
    parser = argparse.ArgumentParser(description=info)
    parser.add_argument("mode", help="Usage mode", type=str)
    parser.add_argument("udp_port", help="Port to listen on client.", type=int)
    parser.add_argument("target_host", help="Target hosts address.")
    args = parser.parse_args()
    return args


def test_clientsession(udp_port, target_host):
    session = Session(udp_port, target_host)


def test_proxysession(host):
    proxy = Session(host)


if __name__ == '__main__':
    args = handle_arguments()
    mode = args.mode
    host = args.target_host
    udp_port = args.udp_port
    test_clientsession(udp_port, host)
