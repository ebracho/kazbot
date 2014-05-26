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
        name = msg[0]
        database = sqlite3.connect('factoids.db')
        c = database.cursor()

        if self.is_registered(name):
            self.msg_chan("You've already registered %s!" % msg[0])
        elif msg[2] != '3':
            self.msg_chan("You must be registered with NickServ to register with kazbot %s!" % name)
        else:
            c.execute("insert into registered_users values(?)", (name,))
            database.commit()
            self.msg_chan("%s succesfuly registered!" % msg[0])

        database.close()

    def add_factoid(self, name, msg):
        key = msg[0]
        data = string.join(msg[1:])

        if not self.is_registered(name):
            self.msg_chan("You havn't registered yet %s! Type: kazbot register" % name)
            return
        elif len(key) > 30: 
            self.msg_chan("Error: key must be less than 30 chars")
            return
        elif len(data) > 300: 
            self.msg_chan("Error: data must be less than 300 chars")
            return

        database = sqlite3.connect('factoids.db')
        c = database.cursor()

        c.execute("select key from factoids where name=?", (name,))
        key_list = c.fetchall()

        c.execute("select * from factoids where name=? and key=?", (name, key))
        match = c.fetchall()

        if len(key_list) >= 100:
            self.msg_chan("Error: %s has reached their factoid limit of 100 factoids. Damn." % name)
        else:
            if match:
                c.execute("delete from factoids where name=? and key=?", (name, key))
                database.commit()
            factoid = (name, key, data)
            c.execute("insert into factoids values (?,?,?)", factoid)
            database.commit()
            self.msg_chan("Factoid succesfully entered")

        database.close()

    def get_factoid(self, name, key):
        database = sqlite3.connect('factoids.db')
        c = database.cursor()

        c.execute("select * from factoids where name=?", (name,))
        factoid_list = c.fetchall()
        
        c.execute("select factoid from factoids where name=? and key=?", (name, key))
        factoid = c.fetchall()

        if not self.is_registered(name): 
            self.msg_chan("You need to register and add your own factoids %s! Try: kazbot help" % name)

        elif not factoid_list: 
            self.msg_chan("You don't have any factoids yet, %s. Try: kazbot add-factoid <key> <factoid>" % name)

        elif not factoid:
            self.msg_chan("You havn't created a factoid with that key %s." % name)
        
        else: self.msg_chan(factoid[0][0])

        database.close()
        

    def is_registered(self, name):
        database = sqlite3.connect('factoids.db')
        c = database.cursor()
        c.execute("select * from registered_users where name=?", (name,))
        matches = c.fetchall()
        if matches: return True
        else: return False

    def parse_buff(self, buff):
        buff = buff.split()
        name = buff[0][1:buff[0].find('!')]
        buff[3] = buff[3].lstrip(':')
        msg = buff[3:]
        return name, msg
            
    def process_command(self, buff):
        name, msg = self.parse_buff(buff)
        if self.debug: print "Name: %s \nMessage: %s" % (name, msg)

        if len(msg) == 1 and msg[0][0] == '~': # get-factoid command
            self.get_factoid(name, msg[0][1:])

        if len(msg) < 2: return # Functions below here require 2 arguments

        if name == "NickServ" and msg[1] == "ACC": self.register_user(msg) # Step 2 of registering user.

        elif len(msg) > 1 and msg[0].find("kazbot") != -1 and msg[1].lower() == "register": # Step 1 of registering user.
            self.msg_user("NickServ", "ACC %s" % name)

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "add-factoid": # "add-factoid" command
            self.add_factoid(name, msg[2:])

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "help": # "help" command
            self.msg_chan("Commands: register, add-factoid <key> <factoid>, ~<factoid-key>, say <message>, sort <data>") 

        if len(msg) < 3: return # Functions below here require 3 arguments

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "say" and len(msg) > 2: # "say" command
            self.msg_chan(string.join(msg[2:]))

        elif msg[0].find("kazbot") != -1 and msg[1].lower() == "sort" and len(msg) > 2: # "sort" command
            self.msg_chan(string.join(sorted(msg[2:])))

    def main_loop(self):
        while True:
            buff = self.IRC.recv(4096)
            if buff and self.debug: print "I< " + buff
            if buff.find('PING') != -1: self.pingpong(buff)
            elif buff.find('PRIVMSG') != -1 or buff.find('NOTICE') != -1: self.process_command(buff)
            

if __name__ == "__main__":
    kazbot = Kazbot()
