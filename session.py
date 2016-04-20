from questions import answer
from socket import socket, gethostname
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, INADDR_ANY, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
import argparse
# import struct

""" TODO: Implementation of extra features, Proxy mode... """


class Connections:

    def __init__(self,target_host):

        # local sockets
        self.target_host = target_host
        self.host_name = gethostname()
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_server_socket = socket(AF_INET, SOCK_DGRAM)

        # clients data
        self.client_tcp_socket = None
        self.client_address = None
        self.client_init_msg = None

        #  available ports are scanned when binding
        self.tcp_server_port = None
        self.udp_server_port = None



    def bind_tcp_server_socket(self):
        """
        scans ports 10000-10100
        :return:
        """
        for port in range(100):
            try:
                tcp_port = 10000 + port
                print("Binding TCP-server socket on {}:{}".format(self.host_name, tcp_port))
                self.tcp_server_socket.bind((self.host_name, tcp_port))
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
                print("Binding UDP-server socket on {}:{}".format(self.host_name, udp_port))
                self.udp_server_socket.bind((str(INADDR_ANY), udp_port))
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
        print('Starting proxy service on {}:{}'.format(self.host_name,self.tcp_server_port))
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


class ClientSession:
    """ TODO: implement added Connection class here so things doesn't get confusing """

    def __init__(self, udp_listener_port, target_host):
        """
        :param udp_listener_port: port for listening incoming UDP messages
        :param target_host: host to connect with tcp for exchanging udp ports
        :return: none
        initializes session parameters
        """
        self.init_feature_statuses()
        self.set_up_udp_sockets(udp_listener_port)
        self.connect_with_tcp_to_exchange_ports(target_host)

    def scan_ports_and_connect_tcp(self):
        """
        scans ports 10000-10100
        :return:
        """
        for port in range(100):
            try:
                print('connecting with scan_ports_and_connect()')
                print("connecting to {}:{}".format(target_host, 10000 + port))
                self.tcp_sock.connect((target_host, 10000 + port))
                break
            except Exception as e:
                print(str(e))

    def connect_with_tcp_to_exchange_ports(self, target_host):
        """
        TODO: ADD EXTRA FEATURES
        :param target_host: host to connect with tcp for exchanging udp ports
        :return: none
        Initializes session parameters involving TCP
        """
        # connect to the target host
        self.target_host = target_host
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.scan_ports_and_connect_tcp()

        # craft the message and send it
        self.init_msg = self.build_handshake_message()
        self.tcp_sock.send(self.init_msg)

        #receive answer and parse port from it
        recv = self.tcp_sock.recv(1024)
        self.target_port = int(recv.decode('utf-8').split(' ')[1].split('\r')[0])

        # tell the user what's happening
        print('Received msg: {}.'.format(recv))
        print('Host listens on port: {}.'.format(self.target_port))
        print('Clients UDP port: {} has been sent.\n\
               Closing TCP-socket..'.format(self.udp_listener_port))

        # close connection
        self.tcp_sock.close()

    def set_up_udp_sockets(self, udp_listener_port):
        """
        :param udp_listener_port: port for listening incoming UDP messages
        :return: none
        Initializes session parameters involving UDP
        """
        # initialize udp sockets
        self.udp_sender_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_listener_port = udp_listener_port
        self.udp_listener_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_listener_sock.bind((str(INADDR_ANY), udp_listener_port))
        self.udp_listener_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        print('listening on {}:{}'.format(gethostname(), self.udp_listener_port))

    def send_a_message(self, msg):
        """
        :param msg: message to be sent
        :return: none
        """
        self.udp_sender_sock.sendto(msg, (self.target_host, self.target_port))

    def build_handshake_message(self):
        """
        builds the init message which is sent with tcp to negotiate extra features
        :return: built message in bytes encoded to 'utf-8'
        """
        features = ('{} {} {} {}'.format(self.get_multipart_status()[1],
                                         self.get_confidentiality_status()[1],
                                         self.get_integrity_status()[1],
                                         self.get_availability_status()[1])).replace('None ', '').lstrip()

        message = 'HELO {} {}\r\n'.format(self.udp_listener_port, features)
        print(message)
        return bytes(message.encode('utf-8'))

    def init_feature_statuses(self):
        """
        initializes features OFF
        can be changed with setter methods
        :return:
        """
        self.multipart_status = False
        self.confidentiality_status = False
        self.integrity_status = False
        self.availability_status = False

    def set_multipart_status(self, status):
        self.multipart_status = status

    def get_multipart_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.multipart_status:
            return self.multipart_status, 'M'
        else:
            return self.multipart_status, None

    def set_confidentiality_status(self, status):
        self.confidentiality_status = status

    def get_confidentiality_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.confidentiality_status:
            return self.confidentiality_status, 'C'
        else:
            return self.confidentiality_status, None

    def set_integrity_status(self, status):
        self.integrity_status = status

    def get_integrity_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.integrity_status:
            return self.integrity_status, 'I'
        else:
            return self.integrity_status, None

    def set_availability_status(self, status):
        self.availability_status = status

    def get_availability_status(self):
        """
        :return: (boolean, flag) flag=None if false
        """
        if self.availability_status:
            return self.availability_status, 'A'
        else:
            return self.availability_status, None

    def start_udp_transaction(self):
        """
        starts udp transaction for exchanging questions/answers
        :return: none
        """
        opening_statement = "Ekki-ekki-ekki-ekki-PTANG".encode('utf-8')
        self.send_a_message(opening_statement)
        print('sent: {}.'.format(opening_statement))

        # listen and response
        while True:
            print('listening..')
            try:
                # get the received message and get the answer to the question
                msg_received = self.udp_listener_sock.recvfrom(1024)[0].decode('utf-8')
                answer_to_question = answer(msg_received)
                # tell the user what's happening
                print("Message received: {}".format(msg_received))
                print("Answer to the question: {}.".format(answer_to_question))
                # reply to the question
                self.send_a_message(answer_to_question.encode('utf-8'))

            except Exception as e:
                print(str(e))


class ProxySession:

    """ TODO: WHOLE CLASS, implement Connection class here so things doesn't get confusing """
    def __init__(self):
        pass

    def create_tcp_sockets(self):
        pass

    def create_udp_sockets(self):
        pass

    def forward_tcp_message(self):
        pass

    def handle_tcp_message(self, socket):
        pass

    def forward_udp_message(self):
        pass

    def handle_forwarding(self):
        pass



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



