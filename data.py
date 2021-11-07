from datetime import datetime, timezone

class User():

    def __inti__(self, user_name):
        self.user_name = user_name

        print(f"TEST, a user object for user with name: " + user_name + " is created. Registering.")

    def try_register(self, password):
        self.password = password
        with open('credentials.txt', 'a') as file:
            file.write(self.user_name + " " + self.password + "\n")

    def try_login(self, password):
        pass



data = {
    'users'         : [

    ],
    'channels'      : [

    ],
    'dms'           : [

    ],
    'msg_positions' : [

    ],
    'dreams_stats'  :{
        'channels_exist': [{
            'num_channels_exist': 0,
            'time_stamp': datetime.now().replace(tzinfo=timezone.utc).timestamp()}],
        'dms_exist': [{
            'num_dms_exist': 0,
            'time_stamp': datetime.now().replace(tzinfo=timezone.utc).timestamp()}],
        'messages_exist': [{
            'num_messages_exist': 0,
            'time_stamp': datetime.now().replace(tzinfo=timezone.utc).timestamp()}],
        'utilization_rate':  0,
    },
}
