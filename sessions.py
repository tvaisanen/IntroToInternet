
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, gethostname
from socket import SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
from questions import answer
from features import Features
import errno, struct, sys
from random import randint


class Session:

    def __init__(self, local_udp_port, host_address, mode='client'):
        if mode == 'client':
            self.mode = mode
            self.locally_reserved_ports = []
            self.local_udp_port = local_udp_port
            self.host_address = host_address
            self.features = Features()
            self.add_features()
            self.udp_server_socket = socket(AF_INET, SOCK_DGRAM)
            self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)
            self.tcp_connection_socket = socket(AF_INET, SOCK_STREAM)
            self.init_connections()
            self.start_udp_communication()
        if mode == 'proxy':
            pass

    def init_connections(self):
        if self.mode == 'client':
            self.scan_available_port_and_bind(type='udpserver')
            # udp client has no neet to bind
            # self.scan_available_port_and_bind(type='')
            self.scan_available_port_and_bind(type='tcpclient')
            message = self.build_handshake_message()
            self.exchange_port_information()

    def start_udp_communication(self):
        """
        starts udp transaction for exchanging questions/answers
        :return: none
        """
        opening_statement = "Ekki-ekki-ekki-ekki-PTANG.".encode('utf-8')
        packed_statement = struct.pack('!??HH64s', True, True, len(opening_statement), 0, opening_statement)
        self.send_udp_message_to_host(packed_statement)

        # listen and response
        EOM = False
        multip = False
        while not EOM:
            print('listening..')
            if EOM:
                break
            try:
                
                while True:
                    question = ''
                    msg_received, addr = self.udp_server_socket.recvfrom(70)
                    unpacked_msg = struct.unpack('!??HH64s', msg_received)
                    print("received: {}".format(unpacked_msg))
                    EOM = unpacked_msg[0]
                    ACK = unpacked_msg[1]
                    content_length = unpacked_msg[2]
                    data_remaining = unpacked_msg[3]
                    question = str(unpacked_msg[4].decode('utf-8'))
                    if multip == True:
                        question = firstprt + question
                        multip = False
                    if content_length < 64:
                        break
                    else:
                        one, two, three = question.rpartition("?")
                        question = one + two
                        firstprt = three
                        multip = True
                        break
                # TODO: looppa tässä jos content_length > 0

                answer_to_question = answer(question)
                 # tell the user what's happening
                print("----------------------------------------")
                print("Question received: {}".format(question))
                print("Answer to the question: {}".format(answer_to_question))
                print("----------------------------------------")
                # reply to the question
                byte_answer = answer_to_question.encode('utf-8')
                #self.host_address = ''
                packed_answer = struct.pack('!??HH64s', EOM, True, len(byte_answer), 0, byte_answer)

                self.send_udp_message_to_host(packed_answer)

            except KeyboardInterrupt as KI:
                print(msg_received)
                if (input('Q?') == 'y'):
                    sys.exit(1)

            except Exception as e:
                print("ex. "+str(e))

    def scan_available_port_and_bind(self, type):
        """
        :param socket: socket to bind
        :param host:  host to bind the socket
        :param type: what mode to bind the socket
        :return: port
        """
        for port in range(100):

            port_to_try = 10000 + port

            try:
                if type == 'udpserver':
                    print("Bind {} to port {}:{}".format(self.udp_server_socket, gethostname(), port_to_try))
                    self.udp_server_socket.bind(('', port_to_try))
                    self.udp_server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                    self.local_udp_port = port_to_try
                    if port_to_try in self.locally_reserved_ports:
                        port_to_try += 1
                    print('udp server binded')

                elif type == 'tcpserver':
                    print("Bind {} to port {}:{}".format(self.tcp_server_socket, gethostname(), port_to_try))
                    self.tcp_server_socket.bind((host, port_to_try))
                    if port_to_try in self.locally_reserved_ports:
                        port_to_try += 1
                    print('tcp server binded')

                elif type == 'tcpclient':
                    self.tcp_connection_socket.connect((self.host_address, port_to_try))
                    print("Bind {} to port {}:{}".format(self.tcp_connection_socket, self.host_address, port_to_try))
                    self.host_tcp_port = port_to_try
                    print('tcpclient init here')

                available_port = port_to_try
                return available_port
                break
            except Exception as e:
                print(str(e))

    def build_handshake_message(self):

        # builds the init message which is sent with tcp to negotiate extra features
        #:return: built message in bytes encoded to 'utf-8'

        features = ('{} {} {} {}'.format(self.features.get_multipart_status()[1],
                                         self.features.get_confidentiality_status()[1],
                                         self.features.get_integrity_status()[1],
                                         self.features.get_availability_status()[1]))

        features = features.replace('None', '').lstrip()
        message = 'HELO {} {}\r\n'.format(self.local_udp_port, features)
        print(message)
        return bytes(message.encode('utf-8'))

    def exchange_port_information(self):
        """
        TODO: ADD EXTRA FEATURES
        Get hosts port for udp-connection
        """
        # craft the message and send it
        self.send_tcp_message(self.build_handshake_message())

        # receive answer and parse port from it
        received = self.tcp_connection_socket.recv(1024)
        try:
            self.host_udp_port = int(received.decode('utf-8').split(' ')[1].split('\r')[0])
        except ValueError as VE:
            print('uusiksi portin parse')

        # tell the user what's happening
        print("Received msg: {}.".format(received))
        print("Host listens on port: {}.".format(self.host_udp_port))
        print("Clients UDP port: {} has been sent.\n\
               Closing TCP-socket..".format(self.local_udp_port))

        # close connection
        self.tcp_connection_socket.close()

    def send_tcp_message(self, message):
        if type(message) != bytes:
            message = message.encode('utf-8')
        try:
            self.tcp_connection_socket.send(message)
        except IOError as e:
            if e.errno == errno.EPIPE:
                self.tcp_connection_socket.connect((self.host_address, self.host_tcp_port))
        print('message sent')

    def send_udp_message_to_host(self, message):
        """
        :param message: message to sent
        :param sock: UDP socket to use
        """
        if type(message) != bytes:
            message = message.encode('utf-8')
        print("sent: {}".format(struct.unpack('!??HH64s', message)))
        self.udp_server_socket.sendto(message, (self.host_address,self.host_udp_port))
        #print("sent: {} to {}:{}".format(message, self.host_address, self.host_udp_port))

    def add_features(self):
        ## allow only one feature
        if input('Add features? [y/n]') == 'y':
            if input('Add multipart feature? [y/n]: ') == 'y':
                self.features.set_multipart_status(True)
            if input('Add confidentiality feature? [y/n]: ') == 'y':
                self.features.set_confidentiality_status(True)
            if input('Add ingegrity to feature? [y/n]: ') == 'y':
                self.features.set_integrity_status(True)
            if input('Add availability feature? [y/n]: ') == 'y':
                self.features.set_availability_status(True)
        else:
            print('No features to add.')

    def random_decryption_key(self):
        keys = []
        for i in range(20):
            keys.append(str(randint(0, 9)))
        keys_as_string = "".join(keys)
        self.decryption_key = keys_as_string

    def encrypt_message(self, message_to_encrypt):
        crypted = []
        for i in range(len(message_to_encrypt)):
            encrypted_char = ord(message_to_encrypt[i]) + ord(self.decryption_key[i])
            crypted.append(chr(encrypted_char))
        crypted = "".join(crypted)
        return crypted

    def decrypt_message(self, message_to_decrypt):
        decrypted = []
        for i in range(len(message_to_decrypt)):
            decrypted_char = ord(message_to_decrypt[i]) - ord(self.decryption_key[i])
            decrypted.append(chr(decrypted_char))
        decrypted = "".join(decrypted)
        return decrypted

    def unpack_udp_message(self, msg):
        data = struct.unpack(msg)
