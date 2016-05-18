import socket
import sys
import time

messages = [ 'This is the message. ',
			 'It will be sent ',
			 'in parts.',
			 ]

# get ip e port
HOST = socket.gethostname()
PORT = 12345

server_address = (HOST, PORT)

# Create a TCP/IP socket
socks = [ socket.socket(socket.AF_INET, socket.SOCK_STREAM),
		  socket.socket(socket.AF_INET, socket.SOCK_STREAM),
		  ]

# Connect the socket to the port where the server is listening
print '\n\n'
print >>sys.stderr, 'connecting to %s port %s' % server_address
print '\n'
for s in socks:
	s.connect(server_address)
	print 'connected socket %s to server' %s
print '\n'

for message in messages:

	# Send messages on both sockets
	for s in socks:
		print >>sys.stderr, '%s: sending "%s"' % (s.getsockname(), message)
		print '\n'
		s.send(message)

	# Read responses on both sockets
	for s in socks:
		data = s.recv(1024)
		print >>sys.stderr, '%s: received "%s"' % (s.getsockname(), data)
		print '\n'

		if not data:
		    print >>sys.stderr, 'closing socket', s.getsockname()
		    s.close()
print '\n\n'
