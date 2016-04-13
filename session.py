from questions import answer, questions
from socket import socket, gethostname
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM
import argparse



class Session:

    def __init__(self, udp_listener_port, target_host):

        # initialize udp listener
        self.udp_listener_port = udp_listener_port
        self.udp_listener_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_listener_sock.bind(("", udp_listener_port))
        print('listening on {}:{}'.format(
            gethostname(), self.udp_listener_port))

        self.target_host = target_host
        self.init_msg = bytes(
            'HELO {}\r\n'.format(self.udp_listener_port).encode('utf-8'))

        # create TCP socket for sending the information
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)

        """ TODO: loop ports until available is found 10000-10100(?) """
        try:
            print("connecting to {}:{}".format(target_host, 10000))
            self.tcp_sock.connect((target_host, 10000))
        except Exception as e:
            print(str(e))
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

    def start_udp_messaging(self):
        # init socket for sending udp packets
        self.udp_sender_sock = socket(AF_INET, SOCK_DGRAM)
        smalltalk = "Hello".encode('utf-8')

        # send "hello" message to the server
        self.udp_sender_sock.sendto(
            smalltalk, (self.target_host, self.target_port))
        print('sent: "Hello\\r\\n".encode(\'utf-8\')')

        # listen to the response
        print(self.udp_listener_sock.recvfrom(128))


""" TODO: handle errors if there's no arguments given """


def handle_arguments():
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
