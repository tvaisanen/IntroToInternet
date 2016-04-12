from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM


class Session:

    def __init__(self, udp_listener_port, target_host):
        init_msg = bytes('HELO {}\r\n'.format(udp_listener_port).encode('utf-8'))

        # create TCP socket for sending the information
        tcp_sock = socket(AF_INET, SOCK_STREAM)

        # Here should be a loop which scans ports if current port is busy
        try:
            print("connecting to {}:{}".format(target_host, 10000))
            tcp_sock.connect((target_host, 10000))
        except OSError as e:
            print(str(e))
        tcp_sock.send(init_msg)
        recv = tcp_sock.recv(1024)
        host_port = recv.decode('utf-8').split(' ')[1].split('\r')[0]
        print('Received msg: {}.'.format(recv))
        print('Host listens on port: {}.'.format(host_port))


        # close connection
        tcp_sock.close()
        print('Clients UDP port: {} has been delivered.\nClosing TCP-socket..'.format(udp_listener_port))



if __name__ == '__main__':
    host = 'ii.virtues.fi'
    host2 = 'st-cn0002.oulu.fi'
    host3 = 'st-cn0003.oulu.fi'
    udp_port = 10010
    session = Session(udp_port, host)