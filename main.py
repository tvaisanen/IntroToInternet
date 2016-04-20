#!/usr/bin/env python3

import argparse
from connections import Connections
from sessions import ClientSession, ProxySession


""" TODO: handle errors if there's no arguments given """


def handle_arguments():
    """
    :return: commandline arguments
    """
    info = "usage: give port number and target host as commandline  arguments."
    parser = argparse.ArgumentParser(description=info)
    parser.add_argument("udp_port", help="Port to listen on client.", type=int)
    parser.add_argument("target_host", help="Target hosts address.")
    args = parser.parse_args()
    return args


def test_clientsession():
    session = ClientSession(udp_port, target_host)
    session.start_udp_messaging()

def test_connections():
    conn = Connections(target_host)
    conn.bind_tcp_server_socket()
    conn.bind_udp_server_socket()
    conn.start_tcp_server()

if __name__ == '__main__':
    args = handle_arguments()
    target_host = args.target_host
    udp_port = args.udp_port
