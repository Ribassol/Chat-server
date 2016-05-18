# serve para importar a classe socket e todos os seus atributos (* = all)
import socket
import select
import sys
import Queue

# criar um objecto da classe socket para o servidor
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# get ip e port
HOST = socket.gethostname()
PORT = 12345

# o servidor adapta o ip e port
server.bind((HOST, PORT)) 

# o servidor fica a escuta de clientes com uma capacidade maxima de 5 ligacoes
print 'Server listening...'
server.listen(5)

# definicao das listas de sockets para o select()
emissor = [ server ]
receptor = []

# o buffer de menssagens passadas pelas sockets emissoras
message_queue = {}


while emissor:
	# Wait for at least one of the sockets to be ready for processing
	print >>sys.stderr, '\nwaiting for the next event'
	readable, writable, exceptional = select.select(emissor, receptor, emissor)

	# Handle inputs
	for s in readable:
		if s is server:
		    # A "readable" server socket is ready to accept a connection
		    connection, client_address = s.accept()
		    print >>sys.stderr, 'new connection from', client_address
		    connection.setblocking(0)
		    emissor.append(connection)

		    # Give the connection a queue for data we want to send
		    message_queue[connection] = Queue.Queue()
		
		else:
			data = s.recv(1024)
			if data:
				# A readable client socket has data
				print >>sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
				message_queue[s].put(data)
				# Add output channel for response
				if s not in receptor:
				    receptor.append(s)
		
			else:
				# Interpret empty result as closed connection
				print >>sys.stderr, 'closing', client_address, 'after reading no data'
				# Stop listening for input on the connection
				if s in receptor:
				    receptor.remove(s)
				emissor.remove(s)
				s.close()
				print 'closed a client'

				# Remove message queue
				del message_queue[s]


	# Handle outputs
	for s in writable:
		try:
		    next_msg = message_queue[s].get_nowait()
		except Queue.Empty:
		    # No messages waiting so stop checking for writability.
		    print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
		    receptor.remove(s)
		else:
		    print >>sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername())
		    s.send(next_msg)
		    

	# Handle "exceptional conditions"
	for s in exceptional:
		print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
		# Stop listening for input on the connection
		emissor.remove(s)
		if s in receptor:
			receptor.remove(s)
		s.close()
		print 'closed a client'

		# Remove message queue
		del message_queue[s]

