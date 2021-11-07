# CNA
you should submit a small report,
report.pdf (no more than 3 pages) describing 
> the program design, 
> data structure design, 
> the application layer message format, 
> a brief description of how your system works.

Language: Python, Version: 3.7
Features: 
    provided by the server:
        user authentication (and registeration) [
        # automatically used
        $ login <user name\n>
            if <user name> in <credential.txt>: continue
            else: $ register <user name\n>
            <password\n>
            if <password> match <credential.txt>: login
            else: error message, password protection count +1
                if count > 2:   $ block_auth <user name>
                                $ logout
        $ logout
        ], 
        authentication protection (wrong password force quit and concurrent account usage protection), 
        auto logout for idle user, 
        presence broadcasts (behaviourly, notification for users), 
        show list of online users [$ Whoelse
            for <all online users>:
                <temp list>.remove(<sender>)
                if <user> not block <sender>: add to <return list>
        ], 
        show online history of all users [$ whoelsesince <time> sec
            for <all users>:
                <temp list>.remove(<sender>)
                if <user> active since <now-time>
                if <user> not block <sender>: add to <return list>
        ], 
        message broadcast [$ broadcast <message>
            for <all users>
                if <user> not block <sender>: send to user
                else: feedback to <sender>, message dumped.
        ], 
        blacklist [
        $ block <user>
            if <user> is <sender>, or, <user> invalid: error message.
            else: add <user> to <sender.blacklist>
        $ unblock <user>
            if <user> is not in <sender.blacklist>: error message
            else: remove <user> from <sender.blacklist>
        ].
    used between users:
        message: 
            general message delivery [$ message <user> <message>
                if <user> block <sender>: feedback to <sender>, message dumped
                elif <user> invalid: feedback(error message) to <sender>, message dumped
            ],
            message forwarding between users (assuming both ends are online), 
            offline messasge, 
        
