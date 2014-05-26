import socket
import sqlite3
import string
import connection_settings

class Kazbot(object):
   
    def __init__(self):
        self.Host = connection_settings.HOST
        self.Port = connection_settings.PORT
        self.Chan = connection_settings.CHAN 
        self.Nick = connection_settings.NICK
        self.debug = True
        self.IRC = socket.socket()

        self.connect()
        self.login()
        self.join_channel()
        self.main_loop()
        
    # IRC Protocol Functions

    def connect(self):
        self.IRC.connect((self.Host, self.Port))
        if self.debug: print("Connected to: " + str(self.IRC.getpeername()))

    def send_data(self, data):
        self.IRC.send("%s\r\n" % data)
        if self.debug: print("I> " + data)

    def login(self):
        self.send_data("Nick %s" % self.Nick)
        self.send_data("User %s 0 * :%s" % (self.Nick, self.Nick))

    def join_channel(self):
        self.send_data("Join %s" % self.Chan)

    def msg_chan(self, msg):
        self.send_data("PRIVMSG %s :%s" % (self.Chan, msg))

    def msg_user(self, user, msg):
        self.send_data("PRIVMSG %s :%s" % (user, msg))

    def pingpong(self, buff):
        buff = buff.split()
        if len(buff) > 1: self.send_data('PONG ' + buff[1])


    # User Command Functions

    def register_user(self, msg):
        name = (msg[0],)
        database = sqlite3.connect('factoids.db')
        c = database.cursor()

        c.execute("select * from registered_users where name=?", name)
        matches = c.fetchall()

        if matches:
            self.msg_chan("%s is already registered." % msg[0])
        elif msg[2] != '3':
            self.msg_chan("User must be registered with NickServ to register with kazbot.")
        else:
            c.execute("insert into registered_users values(?)", name)
            database.commit()
            self.msg_chan("%s succesfuly registered." % msg[0])

        database.close()

    def parse_buff(self, buff):
        buff = buff.split()
        name = buff[0][1:buff[0].find('!')]
        buff[3] = buff[3].lstrip(':')
        msg = buff[3:]
        return name, msg
            
    def process_command(self, buff):
        name, msg = self.parse_buff(buff)
        if self.debug: print "Name: %s \nMessage: %s" % (name, msg)

        if name == "NickServ" and msg[1] == "ACC": self.register_user(msg) # Step 2 of registering user.

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "register": # Step 1 of registering user.
            self.msg_user("NickServ", "ACC %s" % name)

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "help":
            self.msg_chan("Commands: register, say <message>, sort <data>")

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "say" and len(msg) > 2:
            self.msg_chan(string.join(msg[2:]))

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "sort" and len(msg) > 2:
            self.msg_chan(string.join(sorted(msg[2:])))

    def main_loop(self):
        while True:
            buff = self.IRC.recv(4096)
            if buff and self.debug: print "I< " + buff
            if buff.find('PING') != -1: self.pingpong(buff)
            elif buff.find('PRIVMSG') != -1 or buff.find('NOTICE') != -1: self.process_command(buff)
            

if __name__ == "__main__":
    kazbot = Kazbot()
