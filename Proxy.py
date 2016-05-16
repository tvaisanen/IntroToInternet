
class Proxy:

    def __init__(self):
        # start tcp server
        self.start_proxy_server()
        # init connection client-proxy-host
        pass

    def start_proxy_server(self):
        """
        start tcp server needed in proxy mode
        implement message forwarding here?
        supports only one client at a time at this point
        TODO: forward HELO with
        :return:
        """
        # enable reuse address/port
        self.tcp_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        print('Starting proxy service on {}:{}'.format(self.localhost, self.tcp_server_port))
        self.tcp_server_socket.listen(1)
        print('Waiting connection to be forwarded')
        while True:
            print(self.tcp_server_socket.type)
            self.tcp_client_socket, self.client_address = self.tcp_server_socket.accept()
            msg = self.tcp_client_socket.recv(1024).decode('utf-8')
            if msg:
                print('Received message: {} from {}'.format(msg, self.client_address))
                self.client_init_msg = msg
                if self.client_init_msg.startswith('HELO'):
                    print('loppu')
                    break
            self.tcp_client_socket.close()