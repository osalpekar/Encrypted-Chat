import socket
import sys
import select
from utils import *

SOCKET_LIST = []
CHANNELS = []
CHANNEL_DICT = {} #Maps channel names to channel lists
SOCKET_NAMES = {} #Maps sockets to client names
BUFFER = {} #Maps clients to partial messages
HOST = '127.0.0.1'

def server():
	
    #parse the command line arguments
    args = sys.argv
    if (len(args) != 2):
        print 'Please enter only port number in your command line arguments'
        sys.exit()

    port = int(args[1])
    
    #create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, port))
    server_socket.listen(5)

    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
    found = False 

    #start listening for client connection requests
    while(True):

        # get the list sockets which are ready to be read through select
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[])

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                name = sockfd.recv(MESSAGE_LENGTH)
                name = name.rstrip()
                SOCKET_NAMES[sockfd] = name
                 
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    if sock in BUFFER:
                        #message = sock.recv(MESSAGE_LENGTH - len(BUFFER[sock]))
                        message = sock.recv(MESSAGE_LENGTH)# - len(BUFFER[sock]))
                    else:
                        message = sock.recv(MESSAGE_LENGTH)
                    if message:
                        # there is something in the socket
                        
                        #BUFFERING
                        if sock in BUFFER:
                            p1 = len(BUFFER[sock])
                            if (p1 + len(message)) < MESSAGE_LENGTH: #change to !=
                                BUFFER[sock] += message
                                continue
                            else:
                                message = BUFFER[sock] + message
                                message = message.rstrip()
                                #send
                                del BUFFER[sock]
                        else:
                            if len(message) < MESSAGE_LENGTH: #change to !=
                                BUFFER[sock] = message
                                continue
                            else:
                                message = message.rstrip()
                                #send'''
                    
                            #parsing the message for command messages
                            msg_list = message.split()
                            first_word = msg_list[0]
                            if '/' in first_word:

                                if first_word == '/join':
                                    #msg_list = message.split()

                                    #handle if /join entered without argument
                                    if len(msg_list) < 2:
                                        mg = pad(SERVER_JOIN_REQUIRES_ARGUMENT + '\n')
                                        sock.send(mg)
                                        continue
                                    channel_name = msg_list[1]

                                    #handle if user trying to join nonexistant channel
                                    if channel_name not in CHANNELS:
                                        temp_msg = pad(SERVER_NO_CHANNEL_EXISTS.format(channel_name) + '\n')
                                        sock.send(temp_msg)
                                        continue	

                                    #remove user from pervious channels they were in
                                    temp_name = SOCKET_NAMES[sock]
                                    for key, value in CHANNEL_DICT.iteritems():
                                        if sock in value:
                                            #message = temp_name + ' has left'
                                            message = pad(SERVER_CLIENT_LEFT_CHANNEL.format(temp_name))
                                            broadcast(server_socket, sock, value, message)
                                            value.remove(sock)

                                    #add user to new channel and broadcast that message
                                    CHANNEL_DICT[channel_name].append(sock)
                                    message = pad(SERVER_CLIENT_JOINED_CHANNEL.format(SOCKET_NAMES[sock]))
                                    broadcast(server_socket, sock, CHANNEL_DICT[channel_name], message)
                                    continue

                                elif first_word == '/create':
                                    #msg_list = message.split()
                                        
                                    #handle if /create entered without argument
                                    if len(msg_list) < 2:
                                        sock.send(pad(SERVER_CREATE_REQUIRES_ARGUMENT + '\n'))
                                        continue
                                    new_channel_name = msg_list[1]

                                    #handle is user is trying to create an existing channel
                                    if new_channel_name in CHANNELS:
                                        temp_msg = pad(SERVER_CHANNEL_EXISTS.format(new_channel_name) + '\n')
                                        sock.send(temp_msg)
                                        continue

                                    #remove user from old channels that they were in
                                    new_channel_list = []
                                    temp_name = SOCKET_NAMES[sock]
                                    for key, value in CHANNEL_DICT.iteritems():
                                        if sock in value:
                                            #message = temp_name + ' has left'
                                            message = pad(SERVER_CLIENT_LEFT_CHANNEL.format(temp_name))
                                            broadcast(server_socket, sock, value, message)
                                            value.remove(sock)

                                    #add user to new channel
                                    new_channel_list.append(sock)
                                    CHANNELS.append(new_channel_name)
                                    CHANNEL_DICT[new_channel_name] = new_channel_list
                                    continue

                                elif first_word == '/list':
                                    for item in CHANNELS:
                                        sock.send(pad(item + '\n'))
                                    continue
                                
                                #handle invalid control messages 
                                else:
                                    msg_list = message.split()
                                    new_message = pad(SERVER_INVALID_CONTROL_MESSAGE.format(msg_list[0]))
                                    sock.send(new_message)

                            else:
                                #if there is no / in the message, it is just a regular message.
                                temp_name = SOCKET_NAMES[sock]
                                for key, value in CHANNEL_DICT.iteritems():
                                    if sock in value:
                                        message = '[' + temp_name + '] ' + message
                                        message = pad(message)
                                        broadcast(server_socket, sock, value, message) 
                                        found = True
                                if not found:
                                    sock.send(pad(SERVER_CLIENT_NOT_IN_CHANNEL + '\n'))
                                    found = False
                                continue

                    else:
                        # remove the socket that's broken
                        temp_name = SOCKET_NAMES[sock]
                        for key, value in CHANNEL_DICT.iteritems():
                            if sock in value:
                                #message = temp_name + ' has left'
                                message = pad(SERVER_CLIENT_LEFT_CHANNEL.format(temp_name))
                                broadcast(server_socket, sock, value, message)
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                        del SOCKET_NAMES[sock]

                        # at this stage, no data means probably the connection has been broken

                # exception 
                except:
                    temp_name = SOCKET_NAMES[sock]
                    for key, value in CHANNEL_DICT.iteritems(): 
                        if sock in value:
                            message = pad(CLIENT_SERVER_DISCONNECTED.format(HOST, port))
                            broadcast(server_socket, sock, value, message)
                    if sock in SOCKET_LIST:
                        SOCKET_LIST.remove(sock)
                    del SOCKET_NAMES[sock]
    server_socket.close()
	
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, channel, message):
    message = pad(message)
    for socket in channel:
        # send the message only to peer
        if socket != server_socket and socket != sock:
            try:
                socket.sendall(message)
            except:
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
                if socket in channel:
                    channel.remove(socket)
                del SOCKET_NAMES[socket]

#pad messages to become 200 bytes long
def pad(message):
    num_spaces = MESSAGE_LENGTH - len(message)
    while (num_spaces > 0):
        message += ' '
        num_spaces -= 1
    return message

if __name__ == "__main__":
    sys.exit(server())
