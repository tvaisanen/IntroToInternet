import socket

udp_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_listener.bind((socket.gethostname(), 20))
while True:
        data, addr = udp_listener.recvfrom(1024)
        print(data)