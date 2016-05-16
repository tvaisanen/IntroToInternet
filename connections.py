from socket import socket, gethostname
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, INADDR_ANY, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
import errno




class Connections:

    def __init__(self, host):

        # local sockets
        self.locally_reserved_ports = []
        self.host = host
        self.host_udp_port = None
        self.localhost = ''
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_server_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)

        # clients data
        self.client_tcp_socket = None
        self.client_address = None
        self.client_init_msg = None

        # available ports are scanned when binding
        self.tcp_server_port = self.scan_available_port_and_bind(self.tcp_server_socket, self.localhost)
        self.tcp_host_port = self.scan_available_port_and_bind(self.tcp_client_socket, self.host)
        self.udp_server_port = self.scan_available_port_and_bind(self.udp_server_socket, self.localhost)

    def scan_available_port_and_bind(self, mode):
        """
        :param socket: socket to bind
        :param host:  host to bind the socket
        :param mode: what mode to bind the socket
        :return: port
        """
        for port in range(100):

            port_to_try = 10000 + port
            local = (host == self.localhost)

            if local:
                if port_to_try in self.locally_reserved_ports:
                    port_to_try += 1
            try:
                print("Bind {} to port {}:{}".format(sock, host, port_to_try))

                if mode == 'udpserver':
                    self.udp_server_socket.bind((gethostname(), port_to_try))
                    self.udp_server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                    print('udp server binded')

                elif mode == 'tcpserver':
                    self.tcp_server_socket.bind((host, port_to_try))
                    print('tcp server binded')

                elif mode == 'udpclient':
                    print('udpclient init here')

                elif mode == 'tcpclient':
                    print('tcpclient init here')

                available_port = port_to_try
                return available_port
                break
            except Exception as e:
                print(str(e))

    def bind_tcp_server_socket(self):
        """
        binds tcp server socket used in proxy mode
        scans ports 10000-10100
        :return:
        """
        for port in range(100):
            try:
                tcp_port = 10000 + port
                print("Binding TCP-server socket on {}:{}".format(self.localhost, tcp_port))
                self.tcp_server_socket.bind((self.localhost, tcp_port))
                self.tcp_server_port = tcp_port
                break
            except Exception as e:
                print(str(e))

    def bind_udp_server_socket(self):
        """
        scans ports 10000-10100
        :return:
        """
        for port in range(100):
            try:
                udp_port = 10000 + port
                print("Binding UDP-server socket to {}:{}".format(self.localhost, udp_port))
                self.udp_server_socket.bind((str(INADDR_ANY), udp_port))
                self.udp_server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                self.udp_server_port = udp_port
                break
            except Exception as e:
                print(str(e))


    def get(self):
        pass

    def connect_tcp(self):
        self.tcp_client_socket.connect((self.host, self.tcp_host_port))

    def send_tcp_message(self, message):
        if type(message) != bytes:
            message = message.encode('utf-8')
        try:
            self.tcp_client_socket.send(message)
        except IOError as e:
            if e.errno == errno.EPIPE:
                self.connect_tcp()

    # Handle error

    def receive_tcp_message(self):
        return self.tcp_client_socket.recv(1024)

    def close_tcp(self):
        self.tcp_client_socket.close()

    def send_udp_message_to_host(self, message, sock):
        """
        :param message: message to sent
        :param sock: UDP socket to use

        """
        if type(message) != bytes:
            message = message.encode('utf-8')
        sock.sendto(message, (self.host, self.host_udp_port))


