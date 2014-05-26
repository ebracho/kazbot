import socket
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

    def pingpong(self, buff):
        buff = buff.split()
        if len(buff) > 1: self.send_data('PONG ' + buff[1])
        

    def main_loop(self):
        while True:
            buff = self.IRC.recv(4096)
            if buff and self.debug: print buff
            if buff.find('PING') != -1: self.pingpong(buff)

if __name__ == "__main__":
    kazbot = Kazbot()
