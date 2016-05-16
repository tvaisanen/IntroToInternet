from socket import socket, gethostname
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, INADDR_ANY, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR


class Client:

    def __init__(self, local_udp_port, host_address):
        self.host_address = host_address
        self.local_udp_port = local_udp_port
        self.udp_listener = socket(AF_INET, SOCK_DGRAM)
        self.tcp_to_host = socket(AF_INET, SOCK_STREAM)
        pass

    def start_client(self):
        self.initConnectionToHost()

        #start udp listener


    def init_connection_to_host(self):
        # tcp handshake
        pass





