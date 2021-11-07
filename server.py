'''
Usage: python3 server.py <server_port> <block_duration> <timeout>(in sec)
'''

from socket import *
from threading import Thread
import sys
import time
import datetime



if not (len(sys.argv) == 4):
    print("Usage: python3 server.py <server_port> <block_duration> <timeout>(in sec)\nPlease provide correct arguments")
    sys.exit()

# when server starts, intake server port number, block duration, timeout.
server_host     = "127.0.0.1"
server_port     = int(sys.argv[1])
server_address  = (server_host, server_port)
block_duration  = int(sys.argv[2])
idle_timeout    = int(sys.argv[3])

# try to open a socket at the port number
# TODO: open socket
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, client_address, client_socket):
        Thread.__init__(self)
        self.client_address = client_address
        self.client_socket = client_socket
        self.client_alive = False
        
        print("===== New connection created for: ", client_address)
        self.client_alive = True
        
    def run(self):
        message = ''
        
        while self.client_alive:
            # use recv() to receive message from the client
            data = self.client_socket.recv(1024)
            message = data.decode()
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.client_alive = False
                print("===== the user disconnected - ", client_address)
                break
            
            # handle message from the client
            if message == 'login':
                print("[recv] New login request")
                self.process_login()
            elif message == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.client_socket.send(message.encode())
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.client_socket.send(message.encode())
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.client_socket.send(message.encode())
    """
    def process_login(self):
        message = 'user credentials request'
        print('[send] ' + message);
        self.client_socket.send(message.encode())

    # check if username in "credentials.txt",
    # TODO: 
    # if not: register()
    #   else: tryLogin()
    #   TODO: tryLogin should handle authentication protection(block(<user>) after 3 wrong password)
    # if login success: start timeout
    # else: logout(<user>), close connection, close thread.


print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

# while listening, if receive any info, open a thread and try to connect.
# after 3-way handshake, ASK for username
while True:
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    client_thread = ClientThread(client_address, client_socket)
    client_thread.start()
