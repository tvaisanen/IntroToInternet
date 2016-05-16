from socket import socket, AF_INET, SOCK_DGRAM

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', 12345))
while True:
	data = sock.recvfrom(70)
	print('data: {}.\n'.format(data))