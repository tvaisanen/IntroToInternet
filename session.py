from questions import answer
from socket import socket, gethostname
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, INADDR_ANY, SOL_SOCKET, SO_BROADCAST
import argparse
# import struct



class Session:

    def __init__(self, udp_listener_port, target_host):
        """
        :param udp_listener_port: port for listening incoming UDP messages
        :param target_host: host to connect with tcp for exchanging udp ports
        :return: none
        initializes session parameters
        """
        self.set_up_udp_sockets(udp_listener_port)
        self.connect_with_tcp_to_exchange_ports(target_host)

        # create socket for sending UDP now when the target port is known

    def scan_ports_and_connect_tcp(self):
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
        :param target_host: host to connect with tcp for exchanging udp ports
        :return: none
        Initializes session parameters involving TCP
        """
        self.target_host = target_host
        self.init_msg = bytes(
            'HELO {}\r\n'.format(self.udp_listener_port).encode('utf-8'))
        # create TCP socket for sending the information
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.scan_ports_and_connect_tcp()
        self.tcp_sock.send(self.init_msg)
        recv = self.tcp_sock.recv(1024)

        # next line is a quick fix to clean up received message from escapes
        self.target_port = int(
            recv.decode('utf-8').split(' ')[1].split('\r')[0])
        print('Received msg: {}.'.format(recv))
        print('Host listens on port: {}.'.format(self.target_port))
        # close connection
        self.tcp_sock.close()
        print(
            'Clients UDP port: {} has been sent.\nClosing TCP-socket..'.format(self.udp_listener_port))

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
        print('listening on {}:{}'.format(
            gethostname(), self.udp_listener_port))

    def send_a_message(self, msg):
        """
        :param msg: message to be sent
        :return: none
        """
        self.udp_sender_sock.sendto(msg, (self.target_host, self.target_port))

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


if __name__ == '__main__':
    args = handle_arguments()
    target_host = args.target_host
    udp_port = args.udp_port
    session = Session(udp_port, target_host)
    session.start_udp_messaging()
