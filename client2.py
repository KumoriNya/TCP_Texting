"""
    Python 3
    Usage: python3 client2.py <server_port>
    
    Author: Claude Sun
"""

# TODO: logout - disconnect both threads.

from socket import *
from threading import Thread
import sys
from utility import *
from time import sleep

if len(sys.argv) != 2:
    print("\n===== Error usage, python3 client.py SERVER_PORT ======\n");
    exit(0);

class OutputThread(Thread):
    def __init__(self, target_address):
        Thread.__init__(self)
        self.target_address = target_address
        self.output_socket = socket(AF_INET, SOCK_STREAM)
        self.output_socket.connect(target_address)

    def run(self):
        global user_name
        global online
        to_send_header  = "thread"
        to_send_body    = user_name
        to_send_message = to_send_header + " " + to_send_body
        self.output_socket.sendall(to_send_message.encode())
        while online:
            to_send_message = input(">> ")
            self.output_socket.sendall(to_send_message.encode())
            if to_send_message == "logout":
                self.output_socket.close()
                online = False


    def close(self):
        self.output_socket.close()

class InputThread(Thread):
    def __init__(self, target_address):
        Thread.__init__(self)
        self.target_address = target_address
        self.input_socket = socket(AF_INET, SOCK_STREAM)
        self.input_socket.connect(target_address)

    def run(self):
        self.input_socket.sendall("login".encode())
        print("Login request sent")
        global online
        while not online:
            to_send_header = ""
            to_send_body = ""
            # receive response from the server
            data = self.input_socket.recv(1024)
            received_message = data.decode()
            received_header, received_body = packet_decode(received_message)
            print(f"Received header: >>{received_header}<<, body: >>{received_body}<<.")
            # parse the message received from server and take corresponding actions
            if received_header == "":
                print("[recv] Message from server is empty!")
            elif received_header == "blocked":
                print("[recv] You are currently being blocked. Force Quit.")
                self.input_socket.close()
            elif received_header == "user_credentials_request":
                print("[recv] You need to provide username and password to login")
                username = input("[send] Username: ")
                global user_name
                user_name = username
                to_send_header = "username"
                to_send_body = username
            elif received_header == "password":
                password = input("[send] Password: ")
                to_send_header = "password"
                to_send_body = password
            elif received_header == "authentication_success":
                print("[recv] Authentication Passed. Online Now")
                online = True
                break
            elif received_header == "authentication_failed":
                print("[recv] Authentication failed due to wrong password, please try again.")
                password = input("[send] Password: ")
                to_send_header = "password"
                to_send_body = password
            elif received_header == "authentication_protection":
                print("[recv] Multiple authentication error. Account is being blocked.")
                self.input_socket.close()
            elif received_header == "concurrent_existance":
                print("[recv] Concurrent logging issue. Connection stopped.")
                self.input_socket.close()
            else:
                print("[recv] Message "+ received_message +" makes no sense")
            if not online:
                to_send_message = to_send_header + " " + to_send_body
                self.input_socket.sendall(to_send_message.encode())
        print("Start listen only")
        self.input_socket.sendall("listen".encode())
        print("Listen status sent")
        while online:
            data = self.input_socket.recv(1024)
            received_message = data.decode()
            received_header, received_body = packet_decode(received_message)
            print(f"Received header: >>{received_header}<<, body: >>{received_body}<<.")
            if received_header == "user_offlined":
                print("[recv] You have successfully logout. Quiting.")
                break
            elif received_header == "current_online_users":
                print("[recv] Current online users are:\n"+received_body+">> ")
            elif received_header == "unknown_message":
                print(">> ")
            elif received_header == "delivered":
                print("[recv] Message successfully delivered.\n>> ")
            elif received_header == "receive" or received_header == "system_broadcast":
                print("[recv] " + received_body + "\n>> ")
        self.input_socket.close()

            

    def close(self):
        self.input_socket.close()

server_host = "127.0.0.1"
server_port = int(sys.argv[1])
server_address = (server_host, server_port)

from_server = InputThread(server_address)
global user_name
global online
online = False
print(f"online status = {online}")
if not online:
    from_server.start()
while not online:
    continue
to_server = OutputThread(server_address)
print("Threads for receiving and sending are set. Start to wait for possible p2p connections.")
to_server.start()
while online:
    # print(f"online status: {online}")
    sleep(1)
    continue
print("Offline now, application quiting.")
to_server.close()
from_server.close()
exit(1)