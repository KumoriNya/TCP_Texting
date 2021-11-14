from data import data
from datetime import date, datetime, timezone

def find_user(user_name):
    positionCounter = 0
    with open('credentials.txt', 'r') as file:
        word = ''
        letter = file.read(1)
        positionCounter += 1
        found = False
        while not found:
            # '' case for empty file, ' ' case for end of one user name
            while (letter != '' and letter != ' '):
                word += letter
                letter = file.read(1)
                positionCounter += 1
            # print(word)
            if word == user_name:
                found = True
                # print("Found")
                break
            # iterating until the next user name in credentials file
            # print("Not match, iterating through password")
            while (letter != '\n' and letter != ''):
                letter = file.read(1)
                positionCounter += 1
            # either a password is finished or end of file -> one line read
            letter = file.read(1)
            positionCounter += 1
            word = ''
            # No empty line in the initial file, but once writing new data into it there will
            if letter == '':
                positionCounter = -1
                # print("File End, NOT Found")
                break
        
    return positionCounter

def authenticate(user_name, password):
    # return 0 if no match
    match = 0
    targetPasswordPosition = find_user(user_name)
    # return 2 if already online
    if online_check(user_name):
        return 2
    # return True if not online AND password match username
    if (targetPasswordPosition != -1):
        # print("User " + user_name + " exists, start finding")
        with open('credentials.txt', 'r') as file:
            word = ''
            letter = file.read(targetPasswordPosition)
            letter = file.read(1)
            while (letter != '\n' and letter != ''):
                word += letter
                letter = file.read(1)
            if word == password:
                match = True
    return match

def block_user(user_name, duration):
    data['blocked_user_rec'].append(
        {
            'user_name'     : user_name,
            'block_until'   : datetime.now() + duration
        }
    )

def block_check(user_name, now):
    result = False
    blocked_user_index = 0
    for user in data['blocked_user_rec']:
        if user_name == user['user_name']:
            if now - user['block_until'] < 0:
                result = True
            else:
                blocked_user_index += 1
    if result:
        data['blocked_user_rec'].remove(blocked_user_index)
    return result

def register(user_name, password):
    if (find_user(user_name) == -1):
        with open('credentials.txt', 'a+') as file:
            file.write('\n'+user_name+' '+password)
        return True
    return False


def packet_decode(message):
    splitted = message.split()
    header  = ""
    body    = ""
    if len(splitted) > 0:
        header = splitted[0]
        body = message[len(header) + 1:]
    # else:
        # print("Length = "+str(len(splitted)))
        # print("Packet info = "+message)
        # print(f"Splitted = {splitted}")
        # header = splitted[0]
    return (header, body)

# def packet_decode(packet):
#     message = packet.decode()
#     splitted = message.split()
#     header  = ""
#     body    = ""
#     if len(splitted) > 2:
#         header = splitted[0]+' '+splitted[1]
#         body = message[len(header) + 1:]
#     elif len(splitted) > 1:
#         header = splitted[0]
#         body = message[len(header) + 1:]
#     else:
#         # print("Length = "+str(len(splitted)))
#         # print("Packet info = "+message)
#         # print(f"Splitted = {splitted}")
#         header = splitted[0]
#     return (header, body)

def authentication_check(username, password, count):
    authentication_result = False
    if (find_user(username) == -1):
        register(username, password)
        authentication_result = True
    else:
        authentication_result = authenticate(username, password)
    return authentication_result

def online_check(username):
    for user in data['online_users']:
        if user['user_name'] == username:
            return True
    return False

def find_online_user_data_position(username):
    index = 0
    for user in data['online_users']:
        if user['user_name'] == username:
            break
        else:
            index += 1
    if index == len(data['online_users']):
        index -= 1
    return index

def handle_client_instruction(user_input):
    decoded = packet_decode(user_input)
    header = decoded[0]
    if "private" not in header:
        pass
    body = decoded[1]

def client_to_server_message(user_input):
    message = user_input
    splitted = message.split()
    header  = ""
    body    = ""
    while len(splitted) < 1:
        message = input("Please enter a valid input\n>>")
        splitted = message.split()
    header  = splitted[0]
    body    = message[len(header) + 1:]
    return (header, body)

def distinguish(username, socket):
    result = "no_user_yet"
    if len(data['online_users']) > 0:
        index = find_online_user_data_position(username)
        # print(data['online_users'])
        print(f"index = {index}")
        if socket == data['online_users'][index]['speak']:
            result = "speak"
        elif socket == data['online_users'][index]['listen']:
            result = "listen"
        else:
            result = "problem"
    return result