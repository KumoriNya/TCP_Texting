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
            # print statement to the server for distinguishing which user/socket
            # this thread is serving
            print("======\nThread:", self)
            print("Received header: "+header+", body: "+body)
            source = distinguish(username, self.speaker)
            if source != "no_user_yet":
                print("From:", source)
            else:
                print("From:", self.speaker)
            print("======")

            # header == "thread": only case
            #   >> user authentication passed, building connection with the speaker
            if header == "thread":
                username = body
                user_position_index = find_online_user_data_position(username)
                data['online_users'][user_position_index]['speak'] = client_socket
                # print(f"====Connection with online user: {username} is fully established====")
                # print(data['online_users'][user_position_index])
                self.listener = data['online_users'][user_position_index]['listen']
            # header == "username": only case
            #   >> user starting first phase of authentication
            elif header == "username":
                username = body


            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            # if header == "":
            #     print("New Disconnection")
            #     self.client_alive = False
            #     print("===== the user disconnected - ", client_address)
            #     break
            
            status_check = online_check(username)
            # print(f"Check for online status: {username}, {status_check}")
            # handle message from the client
            if not status_check:
                if header == "login":
                    print("[recv] New login request")
                    to_client_header = 'user_credentials_request'
                    # self.process_login()
                elif header == "username":
                    print("[recv] User trying to log in: " + username)
                    # handles concurrency if user already online when attempted to login
                    if username in data['online_users']:
                        to_client_header = "concurrent_existance"
                        self.client_alive = False
                    else:
                        user_blocked = block_check(username, datetime.now())
                        if user_blocked:
                            to_client_header == "authentication_protection"
                            # TODO: optional: add information about block_until to user
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
                                'listen'    : client_socket,
                                'speak'     : ""
                            }
                        )
                        data['online_history_rec'].append(
                            {
                                'user_name': username,
                                'last_active': datetime.now()
                            }
                        )
                        # logout solution 1: once authentication done, break
                        # hence shut down t1
                    elif not authentication_result:
                        print("[send] Authentication Failed, Try Again.")
                        to_client_header = "authentication_failed"
                        if (wrong_password_count < 2):
                            wrong_password_count += 1
                        else:
                            print("[send] Multiple authentication error. Blocking account.")
                            to_client_header = "authentication_protection"
                            block_user(username, block_duration)
                            self.client_alive = False
                    else:
                        print("[send] Concurrent logging issue. Stop connection.")
                        to_client_header = 'concurrent_existance'
                else:
                    print("[recv] " + decoded)
                    print("[send] Cannot understand this message")
                    to_client_header = 'unknown_message'
            else:
                # Concurrent issue
                if header == "password" or header == "username":
                    print("[send] Concurrent logging issue. Stop connection.")
                    to_client_header = 'concurrent_existance'
                    self.client_alive = False
                elif header == "listen":
                    print(f"[recv] Listener socket for user {username} is {self.listener}")
                print("Serving online user: "+username)
                if header == "logout":
                    print("[recv] The user wish to logout. Processing disconnection.")
                    # avoid concurrent editing issue
                    print("===== the user disconnected - ", self.client_address)
                    self.client_alive = False
                    if source == "speak":
                        to_client_header = "user_offlined"
                        to_all_header   = "system_broadcast"
                        to_all_body     = f"user: {username} is offline"
                        to_all_message = to_all_header + " " + to_all_body
                        for user in data['online_users']:
                            if user['user_name'] != username:
                                user['listen'].send(to_all_message.encode())
                        self.speaker.close()
                        print(f"[server] Disconnected with the speaker socket of {username} proceeded. Break loop, sending information to listener to disconnect with the listener")
                    else:
                        del data['online_users'][find_online_user_data_position(username)]
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
                elif header == "thread":
                    to_client_header = "speaker_connected"
            # when client is active, send message to listener
            print(f"before the loop is finished, alive = {self.client_alive}")
            # in loop, if alive, deliver message
            send_condition = True
            if self.speaker == self.listener:
                send_condition = self.client_alive
            if send_condition:
                to_client_message = to_client_header + to_client_body
                self.listener.send(to_client_message.encode())
                print(f"[send] {to_client_message} to {distinguish(username, self.listener)}")
                to_client_header = ""
                to_client_body = ""
        ''' 
            the loop is quit under 2 circumstances:
                1. user authentication success, user name and listener stored, 
                   thus quiting authentication thread.
                2. user logout
            either case, the thread needs to close its connections with 
            the two sockets from user (speaker and listener)
                case 1: the user would have stayed alive
                case 2: the user should be killed after logout procedure is done
                => different message send to the client to indicate disconnection
        '''
            
        
        
        # client is no longer active when loop is broken
        # send the final message for successful disconnection
        # for log out or block to listener
        self.listener.close()
        print("Thread should be closing")

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

# while listening, if receive any info, open a thread and try to connect.
# after 3-way handshake, ASK for username
alive_threads = []
while True:
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    client_thread = ClientThread(client_address, client_socket)
    client_thread.start()
    alive_threads.append(client_thread)
    i = 0
    for thread in alive_threads:
        if thread.is_alive():
            i += 1
    print(f"Number of alive threads = {i}")
