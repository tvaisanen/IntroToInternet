
from questions import answer
from features import Features
from connections import Connections
""" TODO: Implementation of extra features, Proxy mode... """

class ClientSession:
    """ TODO: implement added Connection class here so things doesn't get confusing """

    def __init__(self, udp_listener_port, target_host):
        """
        :param udp_listener_port: port for listening incoming UDP messages
        :param target_host: host to connect with tcp for exchanging udp ports
        :return: none
        initializes session parameters
        """
        self.connections = Connections(target_host)
        self.init_feature_statuses()
        self.exchange_port_information()

    def exchange_port_information(self):
        """
        TODO: ADD EXTRA FEATURES
        Get hosts port for udp-connection
        """
        # connect to the host
        self.connections.connect_tcp()

        # craft the message and send it
        self.connections.send_tcp_message(self.build_handshake_message())

        # receive answer and parse port from it
        received = self.connections.receive_tcp_message()
        self.connections.host_udp_port = int(received.decode('utf-8').split(' ')[1].split('\r')[0])

        # tell the user what's happening
        print("Received msg: {}.".format(received))
        print("Host listens on port: {}.".format(self.connections.host_udp_port))
        print("Clients UDP port: {} has been sent.\n\
               Closing TCP-socket..".format(self.connections.udp_server_port))

        # close connection
        self.connections.close_tcp()

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
    def __init__(self, host):
        self.connections = Connections(host)
        self.connections.bind_tcp_server_socket()
        self.start_proxy_service()
        # get features from this message

    def start_proxy_service(self):
        self.connections.start_proxy_server()

    def forward_tcp_message(self):
        print('forward tcp')
        pass

    def handle_tcp_message(self, socket):
        pass

    def forward_udp_message(self):
        pass

    def handle_forwarding(self):
        pass

""""
def build_handshake_message(self):

    #builds the init message which is sent with tcp to negotiate extra features
    #:return: built message in bytes encoded to 'utf-8'

    features = ('{} {} {} {}'.format(self.get_multipart_status()[1],
                                     self.get_confidentiality_status()[1],
                                     self.get_integrity_status()[1],
                                     self.get_availability_status()[1])).replace('None ', '').lstrip()

    message = 'HELO {} {}\r\n'.format(self.udp_listener_port, features)
    print(message)
    return bytes(message.encode('utf-8'))
"""

