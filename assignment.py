import socket
import argparse

BUFF = 1024


def init_connection(udp_port):

    # initialize connection
    host_for_init = 'ii.virtues.fi'
    host_for_init2 = 'st-cn0002.oulu.fi'
    host_for_init3 = 'st-cn0003.oulu.fi'
    port_for_init = 10000
    address_for_init = (host_for_init, port_for_init)

    # send port number for UDP-transfers
    init_msg = bytes('HELO {}\r\n'.format(udp_port).encode('utf-8'))

    # create TCP socket for sending the information
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("connecting to {}:{}".format(host_for_init, port_for_init))
        tcp_sock.connect(address_for_init)
    except OSError as e:
        print(str(e))

    tcp_sock.send(init_msg)

    # receive confirmation
    recv = tcp_sock.recv(BUFF)
    print(recv)

    # close connection
    tcp_sock.close()
    print('Connection established.. \nClosing TCP-socket \nUDP listens...')


def proxymode():
    pass


def clientmode(host, udp_port):
    host_port = 12345
    udp_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_listener.bind((socket.gethostname(), udp_port))
    init_connection(udp_port)
    udp_sender.sendto('Hello\r\n'.encode('utf-8'), (host, host_port))
    print('Sended: "Hello" to {}:{}'.format(host, host_port))
    while True:
        data, addr = udp_listener.recvfrom(BUFF)
        print(data)

if __name__ == '__main__':
    host = 'ii.virtues.fi'
    host2 = 'st-cn0002.oulu.fi'
    host3 = 'st-cn0003.oulu.fi'
    udp_port = 10010
    clientmode(host, udp_port)
