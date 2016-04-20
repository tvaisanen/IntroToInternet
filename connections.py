from socket import socket, gethostname
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, INADDR_ANY, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR


class Connections:

    def __init__(self, host):

        # local sockets
        self.locally_reserved_ports = []
        self.host = host
        self.host_udp_port = None
        self.local_host = gethostname()
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_server_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)

        # clients data
        self.client_tcp_socket = None
        self.client_address = None
        self.client_init_msg = None

        # available ports are scanned when binding
        self.tcp_server_port = self.scan_available_port_and_bind(self.tcp_server_socket, self.local_host)
        self.tcp_host_port = self.scan_available_port_and_bind(self.tcp_client_socket, self.host)
        self.udp_server_port = self.scan_available_port_and_bind(self.udp_server_socket, self.local_host)

    def scan_available_port_and_bind(self, sock, host):
        """
        :param socket: socket to bind
        :param host:  host to bind the socket
        :return: port
        """
        for port in range(100):

            port_to_try = 10000 + port
            local = (host==self.local_host)

            if local:
                if port_to_try in self.locally_reserved_ports:
                    port_to_try += 1
            try:
                print("Bind {} to port {}:{}".format(sock, host, port_to_try))

                if sock.type == self.udp_server_socket:
                    self.udp_server_socket.bind((host, port_to_try))
                    self.udp_server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

                elif sock.type == self.tcp_server_socket:
                    self.tcp_server_socket.bind((host, port_to_try))

                if local:
                    self.locally_reserved_ports.append(port_to_try)

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
                print("Binding TCP-server socket on {}:{}".format(self.local_host, tcp_port))
                self.tcp_server_socket.bind((self.local_host, tcp_port))
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
                print("Binding UDP-server socket to {}:{}".format(self.local_host, udp_port))
                self.udp_server_socket.bind((str(INADDR_ANY), udp_port))
                self.udp_server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                self.udp_server_port = udp_port
                break
            except Exception as e:
                print(str(e))

    def start_tcp_server(self):
        """
        start tcp server needed in proxy mode
        :return:
        """
        # enable reuse address/port
        self.tcp_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        print('Starting proxy service on {}:{}'.format(self.local_host,self.tcp_server_port))
        self.tcp_server_socket.listen(1)
        while True:
            print('Waiting connections to be forwarded')
            print(self.tcp_server_socket.type)
            self.client_tcp_socket, self.client_address = self.tcp_server_socket.accept()
            msg = self.client_tcp_socket.recv(1024).decode('utf-8')
            if msg:
                print('Received message: {} from {}'.format(msg, self.client_address))
                self.client_init_msg = msg
            self.client_tcp_socket.close()

    def get(self):
        pass

    def connect_tcp(self):
        self.tcp_client_socket.connect((self.host, self.tcp_host_port))

    def send_tcp_message(self, message):
        if type(message) != bytes:
            msg = message.encode('utf-8')
        self.tcp_client_socket.send(message)

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


