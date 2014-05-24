import socket
from connection_settings import HOST, PORT, CHAN, nickname, username, realname, pwd, debug

IRC = socket.socket()

def connect():
    IRC.connect((HOST, PORT))
    if debug == True:
        print ("Connected to: " + str(IRC.getpeername()))

def send_data(msg):
    IRC.send("%s\r\n" % msg)
    if debug == True:
        print("I> " + msg)

def login():
    if pwd != None: send_data("Pass %s" % pwd)
    send_data("Nick %s" % nickname)
    send_data("User %s 0 * :%s" % (username, realname))

def join_channel():
    send_data("Join %s" % CHAN)

def main():
    connect()
    login()
    join_channel()


if __name__ == "__main__":
    main()
