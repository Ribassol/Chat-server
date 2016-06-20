# chat_server.py
 
import sys, socket, select

HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9009
CLIENT_LIST = []
client_count=0

# Client class to store the users' important infos
class Client:
	def __init__(self,username,socket_tag,address):
		self.username=username
		self.socket_tag=socket_tag
		self.address=address

# Method to add new users to the client list
def newClient(conn,address):
	global client_count
	client_count += 1
	newCL = Client('User_'+str(client_count),conn,address)
	CLIENT_LIST.append(newCL)
	return newCL

def chat_server():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((HOST, PORT))
	server_socket.listen(10)

	# add server socket object to the list of readable connections
	SOCKET_LIST.append(server_socket)
	print "Chat server started on port " + str(PORT)

	while 1:
		# get the list sockets which are ready to be read through select
		# 4th arg, time_out  = 0 : poll and never block
		ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
	  
		for sock in ready_to_read:
			# a new connection request recieved
			if sock == server_socket:
				sockfd, addr = server_socket.accept()
				SOCKET_LIST.append(sockfd)
				newCL=newClient(sockfd,addr)
				print "%s connected" % newCL.username               
				broadcast(server_socket, sockfd, "%s entered our chatting room\n" % newCL.username)
			 
			# a message from a client, not a new connection
			else:
				# process data recieved from client, 
				try:
					# receiving data from the socket.
					data = sock.recv(RECV_BUFFER)
					if data:
						# there is something in the socket
						for clt in CLIENT_LIST:
							if clt.socket_tag == sock:
								username=clt.username
						broadcast(server_socket, sock, "\r" + '[' + username + '] ' + data)
						
					else:
						# remove the socket that's broken    
						if sock in SOCKET_LIST:
						    SOCKET_LIST.remove(sock)
						
						# also remove the respective client
						for clt in CLIENT_LIST:
							if clt.socket_tag == sock:
								username=clt.username
								CLIENT_LIST.remove(clt)
						print "%s disconnected" % username
						
						# at this stage, no data means probably the connection has been broken
						broadcast(server_socket, sock, "%s is offline\n" % username) 

				# exception 
				except:
					for clt in CLIENT_LIST:
						if clt.socket_tag == sock:
							username=clt.username
					print "%s disconnected" % username
					broadcast(server_socket, sock, "%s is offline\n" % username)
					continue

	server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":

    sys.exit(chat_server())


         
