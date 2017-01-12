#Encrypted Chat Application

A real-time chat application with end-to-end RSA Encryption. It has features that such as group chat, message buffering, and error correction, to make for a simple, secure, and reliable chatting application from your terminal.

##Running

Open a terminal window to start the chat server:

```
python server.py <host IP> <port number>
```

Any person that wants to participate in the chatshould open a separate terminal window and run the following:

```
python client.py <your name> <server IP> <port number>
```

The IP address and port number at each client must be the same as the ones on which the chat server is running for the connection to be successfully made.

##Use

To create a new chatroom:

```
/create <chatroom name>
```

To join an existing chatroom:

```
/join <chatroom name>
```

To see a list of existing chatrooms:

```
/list
```

##Built With

* Socket API
* NumPy
