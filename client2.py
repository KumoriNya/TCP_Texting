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
        global full_connection
        to_send_header  = "thread"
        to_send_body    = user_name
        to_send_message = to_send_header + " " + to_send_body
        self.output_socket.sendall(to_send_message.encode())
        # wait for response from server for connection with speaker
        while online and not full_connection:
            continue
        while online and full_connection:
            to_send_message = input("> ")
            self.output_socket.sendall(to_send_message.encode())
            if to_send_message == "logout":
                sleep(3)
                break

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
        print("Login request sent") #TODO: debug use
        global online
        global quit
        global full_connection

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
                print("[recv] Account is being blocked due to multiple authentication failure. Please try again later.")
                quit = True
                break
            elif received_header == "concurrent_existance":
                print("[recv] Concurrent logging issue. Connection stopped.")
                quit = True
                break
            else:
                print("[recv] Message "+ received_message +" makes no sense")
            if not online:
                to_send_message = to_send_header + " " + to_send_body
                self.input_socket.sendall(to_send_message.encode())
        
        if online:
            print("Start listen only")
            self.input_socket.sendall("listen".encode())
            print("Listen status sent")
        while online:
            data = self.input_socket.recv(1024)
            received_message = data.decode()
            received_header, received_body = packet_decode(received_message)
            print(f"Received header: >>{received_header}<<, body: >>{received_body}<<.")
            if received_header == "speaker_connected":
                print("[recv] You are fully connected to the server.What do you wish to do next?\nYou can use thw following commands:\nmessage <user> <message>\nbroadcast <message>\nwhoelse\nwhoelsesince <time> where <time> is in seconds to the past from now\nblock <user>\nunblock <user>\nlogout\n")
                full_connection = True
            if received_header == "user_offlined":
                print("[recv] You have successfully logout. Quiting.")
                quit = True
                online = False
                sleep(3)
                break
            elif received_header == "current_online_users":
                print("[recv] Current online users are:\n"+received_body+">> ")
            elif received_header == "unknown_message":
                print(">> ")
            elif received_header == "delivered":
                print("[recv] Message successfully delivered.\n>> ")
            elif received_header == "receive" or received_header == "system_broadcast":
                print("[recv] " + received_body + "\n>> ")
        print("About to close listener socket")
        self.input_socket.sendall("logout".encode())
        self.input_socket.close()
        print("Listener socket closed")
            

    def close(self):
        self.input_socket.close()

server_host = "127.0.0.1"
server_port = int(sys.argv[1])
server_address = (server_host, server_port)

from_server = InputThread(server_address)
global user_name
global online
global quit     # for shutting down application when failure at login state
global full_connection
online  = False
quit    = False
full_connection = False
print(f"online status = {online}") #TODO: debug

if not online:
    from_server.start()

while not online and not quit:
    continue

print(f"quit = {quit}")
if not quit:
    to_server = OutputThread(server_address)
    print("Threads for receiving and sending are set. Start to wait for possible p2p connections.")
    to_server.start()
    while online:
        print(f"online = {online}")
        print(f"quit = {quit}")
        sleep(3)
        continue
    print("Offline, quitting")

while to_server.is_alive():
    to_server.close()
    sleep(3)
print("attempted to close to_server, offline")
if not to_server.is_alive():
    print(f"to_server>>{to_server}<< closed")
while from_server.is_alive():
    from_server.close()
if not from_server.is_alive():
    print(f"from_server>>{from_server}<< closed")
print("Disconnected now, application quiting.")
print("about to exit")
exit()
print("exited")