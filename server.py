'''
    Python 3
    Usage: python3 server.py <server_port> <block_duration> <timeout>(in sec)

    Author: Claude Sun
'''


from socket import *
from threading import Thread
import sys
import time
from datetime import datetime
from utility import *
from data import data



if not (len(sys.argv) == 4):
    print("Usage: python3 server.py <server_port> <block_duration> <timeout>(in sec)\nPlease provide correct arguments")
    sys.exit()

# when server starts, intake server port number, block duration, timeout.
server_host     = "127.0.0.1"
server_port     = int(sys.argv[1])
server_address  = (server_host, server_port)
block_duration  = int(sys.argv[2])
idle_timeout    = int(sys.argv[3])

# open a socket at the port number
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
        self.speaker = client_socket
        self.listener = client_socket
        self.client_alive = False
        
        print("===== New connection created for: ", client_address)
        self.client_alive = True
        
    def run(self):
        username = ""
        wrong_password_count = 0
        
        to_client_header = ""
        to_client_body = ""
        to_client_message = to_client_header + to_client_body
        while self.client_alive:
            # use recv() to receive message from the client
            rcv_packet = self.speaker.recv(1024)

            decoded = rcv_packet.decode()
            packet  = packet_decode(decoded)

            header  = packet[0]
            body    = packet[1]
            print("======\nThread:", self)
            print("Received header: "+header+", body: "+body)
            print("From:", client_address)
            print("======")

            if header == "thread":
                username = body
                user_position_index = find_online_user_data_position(username)
                data['online_users'][user_position_index]['speak'] = client_socket
                print(f"====Connection with online user: {username} is fully established====")
                print(data['online_users'][user_position_index])
                self.listener = data['online_users'][user_position_index]['listen']
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            # if header == "":
            #     print("New Disconnection")
            #     self.client_alive = False
            #     print("===== the user disconnected - ", client_address)
            #     break

            
            # handle message from the client
            status_check = online_check(username)
            if not status_check:
                if header == "login":
                    print("[recv] New login request")
                    to_client_header = 'user_credentials_request'
                    # self.process_login()
                elif header == "username":
                    username = body
                    print("[recv] User trying to log in: " + username)
                    # handles concurrency if user already online when attempted to login
                    if username in data['online_users']:
                        to_client_header = "concurrent_existance"
                        break
                    else:
                        to_client_header = "password"
                elif header == "password":
                    print("Authenticating user: "+username)
                    password = body
                    authentication_result = authentication_check(username, password, wrong_password_count)
                    if authentication_result:
                        print("[send] Authentication Passed, User Logged In.")
                        to_client_header = "authentication_success"
                        to_all_header   = "system_broadcast"
                        to_all_body     = f"user: {username} is online"
                        to_all_message = to_all_header + " " + to_all_body
                        for user in data['online_users']:
                            user['listen'].send(to_all_message.encode())
                        data['online_users'].append(
                            {
                                'user_name' : username,
                                'listen'    : client_socket
                            }
                        )
                        data['online_history_rec'].append(
                            {
                                'user_name': username,
                                'last_active': datetime.now()
                            }
                        )
                    elif not authentication_result:
                        print("[send] Authentication Failed, Try Again.")
                        to_client_header = "authentication_failed"
                        if (wrong_password_count < 2):
                            wrong_password_count += 1
                        else:
                            print("[send] Multiple authentication error. Blocking account.")
                            to_client_header = "authentication_protection"
                            break
                    else:
                        print("[send] Concurrent logging issue. Stop connection.")
                        to_client_header = 'concurrent_existance'
                else:
                    print("[recv] " + decoded)
                    print("[send] Cannot understand this message")
                    to_client_header = 'unknown_message'
            else:
                # Concurrent issue
                if header == "password":
                    print("[send] Concurrent logging issue. Stop connection.")
                    to_client_header = 'concurrent_existance'
                    break
                elif header == "listen":
                    print(f"[recv] Listener socket for user {username} is {self.listener}")
                print("Serving online user: "+username)
                if header == "logout":
                    print("[recv] The user wish to logout. Processing disconnection.")
                    self.client_alive = False
                    # avoid concurrent editing issue
                    user_position_index = find_online_user_data_position(username)
                    del data['online_users'][user_position_index]
                    print("===== the user disconnected - ", client_address)
                    to_client_header = "user_offlined"
                    to_all_header   = "system_broadcast"
                    to_all_body     = f"user: {username} is offline"
                    to_all_message = to_all_header + " " + to_all_body
                    for user in data['online_users']:
                        user['listen'].send(to_all_message.encode())
                    self.speaker.close()
                    self.client_active = False
                    break
                # TODO: instructions before authentication state are ready.
                # message user message
                elif header == "message":
                    target, delivery = packet_decode(body)
                    if online_check(target):
                        f   = username
                        t   = target
                        info    = delivery
                        target_position = find_online_user_data_position(t)
                        target_socket = data['online_users'][target_position]['listen']
                        to_other_message = "receive "+f+": "+info
                        target_socket.send(to_other_message.encode())
                        print(f"[send] Message: {info}\n\tfrom: {f} to {t} is delivered.")
                    else:
                        data['offline_message_storage'].append(
                            {
                                'from'  : username,
                                'to'    : target,
                                'info'  : delivery
                            }
                        )
                        print(f"[send] Message: {delivery}\n\tfrom: {username} to {target} is stored.")
                    to_client_header = "delivered"
                elif header == "broadcast":
                    pass
                elif header == "whoelse":
                    to_client_header = "current_online_users"
                    whoelse = " "
                    # TODO: block
                    for user in data['online_users']:
                        if user['user_name'] != username:
                            whoelse = whoelse + user['user_name'] + '\n'
                    to_client_body += whoelse
                elif header == "whoelsesince":
                    pass
                elif "block" in header:
                    pass
            if self.client_alive:
                to_client_message = to_client_header + to_client_body
                self.listener.send(to_client_message.encode())
                print(f"[send] {to_client_message} to {self.listener}")
                to_client_header = ""
                to_client_body = ""
        if self.client_alive:
            to_client_message = to_client_header + to_client_body
            self.listener.send(to_client_message.encode())
            self.listener.close()

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

# while listening, if receive any info, open a thread and try to connect.
# after 3-way handshake, ASK for username
while True:
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    client_thread = ClientThread(client_address, client_socket)
    client_thread.start()
