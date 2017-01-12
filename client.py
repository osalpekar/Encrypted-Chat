import sys
import select, socket
from utils import *


def client():
    
    args = sys.argv
    if(len(args) != 4) :
        print 'Usage : python chat_client.py user_name hostname port'
        sys.exit()

    name = str(args[1])
    host = str(args[2])
    port = int(args[3])
    rec = False
    
    msf = ''

    num_messages = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     
    # connect to remote host
    try:
        s.connect((host, port))
    except:
        print CLIENT_CANNOT_CONNECT.format(host, port)
        sys.exit()

    print 'Connected to remote host. You can start sending messages'
    sys.stdout.write(CLIENT_MESSAGE_PREFIX)
    sys.stdout.flush()
    s.send(pad(name))
     
    while(True):
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:			
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(MESSAGE_LENGTH)
                #data = data.rstrip()
                
                #BUFFERING
                if not data:
                    print '\nDisconnected from chat server'
                    sys.exit()
                else:
                    if len(msf) != 0:
                        p1 = len(msf)
                        if (p1 + len(data)) != MESSAGE_LENGTH:
                            msf += data
                            continue
                        else:
                            data = msf + data
                            data = data.rstrip()
                            msf = ''
                    else:
                        if len(data) != MESSAGE_LENGTH:
                            msf = data
                            continue
                        else:
                            data = data.rstrip()
                            msf = ''
                    
                    #print the data 
                    sys.stdout.write(CLIENT_WIPE_ME + '\r' +  data)
                    sys.stdout.write('\n[Me] ')
                    sys.stdout.flush()
                
            else:
                #waiting for user to type in message
                sys.stdout.write(CLIENT_MESSAGE_PREFIX)
                sys.stdout.flush()
                msg = sys.stdin.readline()
                msg = pad(msg)
                s.sendall(msg)

#padding messages to be 200 bytes long
def pad(message):
    num_spaces = MESSAGE_LENGTH - len(message)
    while (num_spaces > 0):
        message += ' '
        num_spaces -= 1
    return message

if __name__ == "__main__":
    sys.exit(client())

