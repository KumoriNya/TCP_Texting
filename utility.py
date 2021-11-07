
def find_user(user_name):
    with open('credentials.txt', 'r') as file:
        word = ''
        letter = file.read(1)
        found = False
        while not found:
            while (letter != '' and letter != ' '):
                word += letter
                letter = file.read(1)
                print(word+'\n')
            if letter == '':
                break
            if word == user_name:
                found = True
            while (letter != '\n'):
                letter = file.read(1)
            letter = file.read(1)
            word = ''
        print("File End")
    return found

def authenticate(user_name, password):
    match = False
    if (find_user(user_name)):
        with open('credentials.txt', 'r') as file:
            word = ''
            letter = file.read(1)
            found = False
            while not found:
                # find a user name
                while (letter != '' and letter != ' '):
                    word += letter
                    letter = file.read(1)
                if word == user_name:
                    found = True
                    break
                # user name found does not match, iterate until pass this line
                word = ''
                while (letter != '\n'):
                    letter = file.read(1)
            word = ''
            letter = file.read(1)
            while (letter != '\n'):
                word += letter
                letter = file.read(1)
            if word == password:
                match = True
    return match
