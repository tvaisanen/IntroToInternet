import socket

udp_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sender.sendto('Hello'.encode('utf-8'), (socket.gethostname(), 10010))
print('Hello sended to {}.'.format(socket.gethostname()))