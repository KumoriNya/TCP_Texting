
def find_user(user_name):
    with open('credentials.txt', 'r') as file:
        word = ''
        letter = file.read(1)
        print(word+'\n')
        found = False
        while not found:
            while (letter != '' and letter != ' ' and letter != '\n'):
                word += letter
                letter = file.read(1)
                print(word+'\n')
            if word == user_name:
                found = True
            letter = file.read(1)
            word = ''
        print("File End")
        file.read(1)
        file.read(1)
    return found

def authenticate(user_name, password):
    if (find_user(user_name)):
        match = False
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
