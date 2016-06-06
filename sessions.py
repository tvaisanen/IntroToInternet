from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, gethostname, gethostbyname
from socket import SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
from questions import answer
from features import Features
import errno, struct, sys


class Session:

    def __init__(self, host_tcp_port, host_address, mode):
        self.mode = mode
        self.locally_reserved_ports = []
        self.local_udp_port = 0
        self.client_ip = ""
        self.client_udp_port = 0
        self.client_address = (self.client_ip, self.client_udp_port)
        self.host_ip = host_address
        self.host_tcp_port = host_tcp_port
        self.host_udp_port = 0
        self.host_address = (self.host_ip, self.host_udp_port)
        self.server_udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_connection_socket = socket(AF_INET, SOCK_STREAM)
        self.multipart_message_buffer = ""
        self.multipart_message_handling_over = True
        self.features = Features()
        if mode == 'client':
            self.   add_multipart()
            self.init_connections()
            #self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)
            self.start_udp_communication()
        if mode == 'proxy':
            self.init_connections()
            self.start_proxy_service()
            self.client_ip = ('', 0)


    def init_connections(self):
        if self.mode == 'client':
            self.scan_available_port_and_bind(type='udpserver')
            # udp client has no neet to bind
            # self.scan_available_port_and_bind(type='')
            self.scan_available_port_and_bind(type='tcpclient')
            message = self.build_handshake_message()
            self.exchange_port_information()
        elif self.mode == 'proxy':
            self.scan_available_port_and_bind(type='tcpclient')
            self.scan_available_port_and_bind(type='tcpserver')
            self.scan_available_port_and_bind(type='udpserver')

    def start_proxy_service(self):
        self.wait_tcp_connection_and_init()
        self.start_udp_proxy()

    def wait_tcp_connection_and_init(self):

        print("Waiting for tcp connection..")
        print("Proxy supports only one client at the time")
        # listen to clients, backlog argument specifies the max no. of queued conns
        self.server_tcp_socket.listen(20)

        while True:
            try:
                print('\nWaiting to receive message from client')
                self.client_tcp_socket, address = self.server_tcp_socket.accept()
                client_ip, client_port = address
                data = self.client_tcp_socket.recv(70)
                # modify self.client address so that the port is same as used by udp
                clients_message_in_parts = data.decode("utf-8").split(" ")
                self.client_udp_port = clients_message_in_parts[1]
                self.client_address = (client_ip, int(self.client_udp_port))

                print(" ".join(clients_message_in_parts))
                modified_message_in_parts = clients_message_in_parts
                modified_message_in_parts[1] = " " + str(self.local_udp_port) + " "
                print("in parts: {}".format(modified_message_in_parts))

                modified_message = " ".join(modified_message_in_parts).encode('utf-8')
                modified_message_as_bytes  = bytes("".join(modified_message_in_parts).encode('utf-8'))


                print("clients udp port: {}".format(self.client_udp_port))
                if data:
                    print("\nData: {}.".format(data))
                    print("Client type: {}".format(type(self.client_tcp_socket)))
                    print("Client address: {}".format(self.client_ip))
                    try:
                        print("\nHost address: {}:{}".format(self.host_ip, self.host_tcp_port))
                        self.tcp_connection_socket.sendto(modified_message_as_bytes, (self.host_ip, self.host_tcp_port))
                        print("sent: {}\nto: {}".format(modified_message_as_bytes, (self.host_ip, self.host_tcp_port)))
                        server_response = self.tcp_connection_socket.recv(1024)
                        print(server_response)
                    except Exception as e:
                        print(str(e))
                        #print('sent %s bytes back to %s' % (data, address))
                    hosts_response_in_parts = server_response.decode("utf-8").split(" ")
                    print("host_response_in_parts: {}".format(server_response))
                    print("self.host_udp_port = hosts_response_in_parts[1]")
                    print("self.host_udp_port = {}".format(hosts_response_in_parts[1]))
                    self.host_udp_port = int(hosts_response_in_parts[1].strip('\x00'))

                    # save hosts upd address as a tuple
                    self.host_address = (self.host_ip, self.host_udp_port)
                    print("self.host_address: {}.".format(self.host_address))
                    print("response:")
                    print("".join(hosts_response_in_parts))


                    modified_response_in_parts = hosts_response_in_parts
                    modified_response_in_parts[1] = str(self.local_udp_port)
                    modified_response_as_bytes = bytes(" ".join(modified_response_in_parts).encode('utf-8'))
                    self.client_tcp_socket.send(modified_response_as_bytes)

                self.client_tcp_socket.close()

            except ValueError as e:
                print(str(e))
            if (server_response == b'Invalid command.\r\n'):
                print("Invalid command.")
            else:
                break

    def start_udp_proxy(self):
        EOM = False
        while not EOM:
            print("Listening udp traffic to forward..\n")
            try:
                msg_received, sender_address = self.server_udp_socket.recvfrom(70)
                print("Message received")
                print("from: {}".format(sender_address))
                self.pretty_print_packed_msg(msg_received)
                print("client: {}".format(self.client_address))
                print("host: {}".format(self.host_address))

                print(sender_address == self.host_address or sender_address == gethostbyname(self.host_ip))
                if sender_address == self.client_address:
                    self.server_udp_socket.sendto(msg_received, self.host_address)
                    print("sent to: {}.\n".format(self.host_address))
                elif sender_address == self.host_address or sender_address == (str(gethostbyname(self.host_ip)),self.host_udp_port):
                    EOM = struct.unpack('!??HH64s', msg_received)[0]
                    self.server_udp_socket.sendto(msg_received, self.client_address)
                    print("sent to: {}.".format(self.client_address))
            except Exception as e:
                print(str(e))
        print("Last message forwarded. Closing proxy.")


    def start_udp_communication(self):
        """
        starts udp transaction for exchanging questions/answers
        :return: none
        """
        opening_statement = "Ekki-ekki-ekki-ekki-PTANG.".encode('utf-8')
        packed_statement = struct.pack('!??HH64s', True, True, len(opening_statement), 0, opening_statement)
        self.send_udp_message_to_host(packed_statement)
        print("sent: {}".format(opening_statement))

        # listen and response
        EOM = False
        while not EOM:
            print('listening..')
            if EOM:
                break
            try:
                msg_received, addr = self.server_udp_socket.recvfrom(70)
                unpacked_msg = struct.unpack('!??HH64s', msg_received)
                print("\nReceived:")
                self.pretty_print_packed_msg(msg_received)
                EOM = unpacked_msg[0]
                ACK = unpacked_msg[1]
                content_length = unpacked_msg[2]
                remaining_content = unpacked_msg[3]

                # print("need to handle multipart messags: {}".format(remaining_content > 0))
                # print("need to handle remaining content: {}".format(not self.multipart_message_handling_over))
                question = str(unpacked_msg[4].decode('utf-8'))

                if remaining_content > 0:
                    print("remaining content was larger than 0. So we have to handle multipart messages")
                    self.multipart_message_handling_over = False

                if not self.multipart_message_handling_over:
                    print("multipart handling is not over")
                    complete_question = self.handle_multipart_message(question, content_length, remaining_content)
                    print("complete question: {}".format(complete_question))

                    if complete_question:
                        self.answer_to_question(complete_question, EOM)
                elif self.multipart_message_buffer == "":
                    self.answer_to_question(question, EOM)

            except KeyboardInterrupt as KI:
                print(msg_received)
                if (input('Q?') == 'y'):
                    sys.exit(1)

            except Exception as e:
                print("ex. "+str(e))

    def answer_to_question(self, question, EOM):

        answer_to_question = answer(question)
        # tell the user what's happening
        print("----------------------------------------")
        print("Question received: {}".format(question))
        print("Answer: {}".format(answer_to_question))

        if len(answer_to_question) > 64:
            print("handle sending of a multipart message")
            first_part_of_the_answer = answer_to_question[:64].encode('utf-8')
            second_part_of_the_answer = answer_to_question[64:].encode('utf-8')

            print(first_part_of_the_answer)
            print(second_part_of_the_answer)

            first_answer_packed = struct.pack('!??HH64s', EOM, True, len(first_part_of_the_answer), len(second_part_of_the_answer), first_part_of_the_answer)
            second_answer_packed = struct.pack('!??HH64s', EOM, True, len(second_part_of_the_answer), 0, second_part_of_the_answer)
            self.send_udp_message_to_host(first_answer_packed)
            print("Sent: ")
            self.pretty_print_packed_msg(first_answer_packed)
            self.send_udp_message_to_host(second_answer_packed)
            print("Sent: ")
            self.pretty_print_packed_msg(second_answer_packed)

        else:

            byte_answer = answer_to_question.encode('utf-8')
            packed_answer = struct.pack('!??HH64s', EOM, True, len(byte_answer), 0, byte_answer)
            print("Sent:")
            self.pretty_print_packed_msg(packed_answer)

            self.send_udp_message_to_host(packed_answer)

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
                    print("Bind {} to port {}:{}".format(self.server_udp_socket, gethostname(), port_to_try))
                    self.server_udp_socket.bind(('', port_to_try))
                    self.server_udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                    self.local_udp_port = port_to_try
                    if port_to_try in self.locally_reserved_ports:
                        port_to_try += 1
                    print('udp server binded')

                elif type == 'tcpserver':
                    print("Bind {} to port {}:{}".format(self.server_tcp_socket, gethostname(), port_to_try))
                    self.server_tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                    self.server_tcp_socket.bind(('', port_to_try))
                    if port_to_try in self.locally_reserved_ports:
                        port_to_try += 1
                    self.host_tcp_port = port_to_try
                    print('tcp server binded')

                elif type == 'tcpclient':
                    self.tcp_connection_socket.connect((self.host_ip, self.host_tcp_port))
                    print("Bind {} to port {}:{}".format(self.tcp_connection_socket, self.host_ip, self.host_tcp_port))
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

        features = features.replace('None', '').strip(" ")
        print("features: '{}'".format(features))
        message = 'HELO {} {}'.format(self.local_udp_port, features)
        if message.endswith(' '):
            message.rstrip(' ')
        message += "\r\n"
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
        self.host_address = self.host_ip, self.host_udp_port
        # close connection
        self.tcp_connection_socket.close()

    def send_tcp_message(self, message):
        if type(message) != bytes:
            message = message.encode('utf-8')
        try:
            self.tcp_connection_socket.send(message)
            print(message)
            print("send_tcp_messag: {}.".format(self.tcp_connection_socket.getsockname()))
        except IOError as e:
            if e.errno == errno.EPIPE:
                self.tcp_connection_socket.connect((self.host_ip, self.host_tcp_port))
        print('message sent')

    def send_udp_message_to_host(self, message):
        """
        :param message: message to sent
        :param sock: UDP socket to use
        """
        self.server_udp_socket.sendto(message, (self.host_ip, self.host_udp_port))

        self.pretty_print_packed_msg(message)
        print("Sent to {} from {}".format(self.host_address, self.server_udp_socket.getsockname()))

    def add_multipart(self):
        if input('Add multipart feature? [y/n]: ') == 'y':
            self.features.set_multipart_status(True)


    def handle_multipart_message(self, message, content_length, remaining_content):
        print("\nhandling multipart message:")
        self.multipart_message_buffer = self.multipart_message_buffer + message
        print("\t\tbuffer: {}.".format(self.multipart_message_buffer))
        print("\t\tbuffer length: {}.".format(len(self.multipart_message_buffer)))
        self.multipart_message_handling_over = False

        # print("message: {}.".format(message))
        # print("content length: {}".format(content_length))
        # print("remaining content: {}".format(remaining_content))
        # print("length of buffer: {}".format(len(self.multipart_message_buffer)))

        if remaining_content == 0:
            complete_multipart_message = self.multipart_message_buffer
            self.multipart_message_buffer = ""
            self.multipart_message_handling_over = True
            print("multipart message compeleted: {}".format(complete_multipart_message))
            return complete_multipart_message

    def handle_remaining_multipart_content(self, msg):
        print("\nHandling remaining content")
        print("Buffer: {}".format(self.question_buffer))
        print("Partial question: {}".format(msg))
        question_to_return = self.question_buffer[0] + msg
        self.question_buffer[0] = None
        print("remaining content parsed together: {}".format(question_to_return))
        print("question buffer after handling remaining content\n{}.".format(self.question_buffer))
        return question_to_return

    def data_remaining(self, data_remaining):
        if data_remaining > 0:
            return True
        else:
            return False

    def pretty_print_packed_msg(self,msg):
        unpacked = struct.unpack('!??HH64s', msg)
        print("\nMessage unpacked:")
        print("\t\tEOM:\t\t\t{}".format(unpacked[0]))
        print("\t\tACK:\t\t\t{}".format(unpacked[1]))
        print("\t\tContent length:\t\t{}".format(unpacked[2]))
        print("\t\tRemaining content:\t{}".format(unpacked[3]))
        print("\t\tContent:\t\t{}\n".format(unpacked[4].decode('utf-8').strip("\x00")))