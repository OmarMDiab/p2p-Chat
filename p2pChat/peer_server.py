'''
    ##  Implementation of peer
    ##  Each peer has a client and a server side that runs on different threads
    ##  150114822 - Eren Ulaş
'''

from socket import *
import threading
import time
import select
import logging
import globals
import pickle
from colorama import init, Fore, Back, Style
import random
import re

init(autoreset=True)

# Server side of peer
class PeerServer(threading.Thread):
    # Peer server initialization
    def __init__(self, username, peerServerPort, peerServerPortUDP):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        # udp socket for peer server
        self.udpServerSocket = socket(AF_INET, SOCK_DGRAM)
        # port number of the peer server for tcp
        self.peerServerPort = peerServerPort
        # port number of the peer server for udp
        self.peerServerPortUDP = peerServerPortUDP
        # if 1, then user is already chatting with someone
        # if 0, then user is not chatting with anyone
        self.isChatRequested = 0
        # keeps the socket for the peer that is connected to this peer
        self.connectedPeerSocket = None
        # keeps the ip of the peer that is connected to this peer's server
        self.connectedPeerIP = None
        # keeps the port number of the peer that is connected to this peer's server
        self.connectedPeerPort = None
        # online status of the peer
        self.isOnline = True
        # keeps the username of the peer that this peer is chatting with
        self.chattingClientName = None

    # main method of the peer server thread
    def run(self):

        print("Peer server started...")    

        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        hostname=gethostname()
        try:
            self.peerServerHostname=gethostbyname(hostname)
        except gaierror:
            import netifaces as ni
            self.peerServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

        # ip address of this peer
        #self.peerServerHostname = 'localhost'
        # socket initializations for the server of the peer
        self.tcpServerSocket.bind((self.peerServerHostname, self.peerServerPort))
        self.tcpServerSocket.listen(4)
        
        self.udpServerSocket.bind((self.peerServerHostname, self.peerServerPortUDP))
        # inputs sockets that should be listened
        inputs = [self.tcpServerSocket, self.udpServerSocket]
        # server listens as long as there is a socket to listen in the inputs list and the user is online
        while inputs and self.isOnline:
            # monitors for the incoming connections
            try:
                readable, writable, exceptional = select.select(inputs, [], [])
                # If a server waits to be connected enters here
                for s in readable:
                    # if the socket that is receiving the connection is 
                    # the tcp socket of the peer's server, enters here
                    if s is self.tcpServerSocket:
                        # accepts the connection, and adds its connection socket to the inputs list
                        # so that we can monitor that socket as well
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        inputs.append(connected)
                        # if the user is not chatting, then the ip and the socket of
                        # this peer is assigned to server variables
                        if self.isChatRequested != 1:     
                            print(self.username + " is connected from " + str(addr))
                            self.connectedPeerSocket = connected
                            self.connectedPeerIP = addr[0]
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
                    elif s is self.udpServerSocket:
                        request = pickle.loads(self.udpServerSocket.recvfrom(1024)[0])
                        # if the user is not in the room
                        if(globals.joined_room_name != request["room_name"]):
                            continue 
                        if(globals.room_users.count(request["user"])==0):
                            globals.room_users.append(request["user"])
                        
                        print(request["message"])
                    else:
                        # message is received from connected peer
                        messageReceived = s.recv(1024).decode()
                        # logs the received message
                        logging.info("Received from " + str(self.connectedPeerIP) + " -> " + str(messageReceived))
                        # if message is a request message it means that this is the receiver side peer server
                        # so evaluate the chat request
                        if len(messageReceived) > 11 and messageReceived[:12] == "CHAT-REQUEST":
                            # text for proper input choices is printed however OK or REJECT is taken as input in main process of the peer
                            # if the socket that we received the data belongs to the peer that we are chatting with,
                            # enters here
                            if s is self.connectedPeerSocket:
                                # parses the message
                                messageReceived = messageReceived.split()
                                # gets the port of the peer that sends the chat request message
                                self.connectedPeerPort = int(messageReceived[1])
                                # gets the username of the peer sends the chat request message
                                self.chattingClientName = messageReceived[2]
                                # prints prompt for the incoming chat request
                                print("Incoming chat request from " + self.chattingClientName + " >> ")
                                print("Press Enter to continue")
                                globals.ignore_input.set()
                                
                                # makes isChatRequested = 1 which means that peer is chatting with someone
                                self.isChatRequested = 1
                            # if the socket that we received the data does not belong to the peer that we are chatting with
                            # and if the user is already chatting with someone else(isChatRequested = 1), then enters here
                            elif s is not self.connectedPeerSocket and self.isChatRequested == 1:
                                # sends a busy message to the peer that sends a chat request when this peer is 
                                # already chatting with someone else
                                message = "BUSY"
                                s.send(message.encode())
                                # remove the peer from the inputs list so that it will not monitor this socket
                                inputs.remove(s)
                        # if an OK message is received then ischatrequested is made 1 and then next messages will be shown to the peer of this server
                        elif messageReceived == "OK":
                            self.isChatRequested = 1
                        # if an REJECT message is received then ischatrequested is made 0 so that it can receive any other chat requests
                        elif messageReceived == "REJECT":
                            globals.ignore_input.clear()
                            self.isChatRequested = -1
                            inputs.remove(s)
                        # if a message is received, and if this is not a quit message 'quit' and 
                        # if it is not an empty message, show this message to the user
                        elif messageReceived[:4] != "quit" and len(messageReceived)!= 0:
# >>>>>>>>>>>>>>>> fixing alignemnt
                            messageReceived=self.one_to_one_Fomrating(messageReceived)
                            print('\n\033[1A' + '\033[K', end="")
                            print(self.get_user_color(self.chattingClientName) + self.chattingClientName + ": " + Fore.RESET + messageReceived)
                            print ("you:", end=" ")
                        # if the message received is a quit message 'quit',
                        # makes ischatrequested 1 to receive new incoming request messages
                        # removes the socket of the connected peer from the inputs list
                        elif messageReceived[:4] == "quit":
                            self.isChatRequested = 0
                            globals.ignore_input.clear()
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            # connected peer ended the chat
                            if len(messageReceived) == 4:
                                print('\n\033[1A' + '\033[K', end="")
                                print("User you're chatting with ended the chat")
                                print("Press enter to quit the chat: ")
                        # if the message is an empty one, then it means that the
                        # connected user suddenly ended the chat(an error occurred)
                        elif len(messageReceived) == 0:
                            self.isChatRequested = 0
                            globals.ignore_input.clear()
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            print('\n\033[1A' + '\033[K', end="")
                            print("User you're chatting with suddenly ended the chat")
                            print("Press enter to quit the chat: ")
            # handles the exceptions, and logs them
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))
                
    def get_user_color(self, username):
        # Define a list of colors from Colorama
        colors = [
            Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN
        ]

        # Use the hash of the username to choose a color
        random.seed(hash(username))
        color = random.choice(colors)
        return color  
        
    def one_to_one_Fomrating(self, raw_message):
        formatted_message = raw_message

        # **bold**
        formatted_message = re.sub(r'\*\*(.*?)\*\*', lambda match: f'\033[1m{match.group(1)}\033[0m', formatted_message)

        # __italic__
        formatted_message = re.sub(r'__(.*?)__', lambda match: f'\033[3m{match.group(1)}\033[0m', formatted_message)

        # [hyperlink](url)
        formatted_message = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\033]8;;\2\033\\ \1 \033]8;;\033\\', formatted_message)
        
        return formatted_message  

# Client side of peer
class PeerClient(threading.Thread):
    # variable initializations for the client side of the peer
    def __init__(self, ipToConnect, portToConnect, username, peerServer, responseReceived):
        threading.Thread.__init__(self)
        # keeps the ip address of the peer that this will connect
        self.ipToConnect = ipToConnect
        # keeps the username of the peer
        self.username = username
        # keeps the port number that this client should connect
        self.portToConnect = portToConnect
        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        # keeps the server of this client
        self.peerServer = peerServer
        # keeps the phrase that is used when creating the client
        # if the client is created with a phrase, it means this one received the request
        # this phrase should be none if this is the client of the requester peer
        self.responseReceived = responseReceived

        # keeps if this client is ending the chat or not
        self.isEndingChat = False
        


    # main method of the peer client thread
    def run(self):
        # connects to the server of other peer
        self.tcpClientSocket.connect((self.ipToConnect, self.portToConnect))
        # if the server of this peer is not connected by someone else and if this is the requester side peer client then enters here
        if self.peerServer.isChatRequested != 1 and self.responseReceived is None:
            # composes a request message and this is sent to server and then this waits a response message from the server this client connects
            requestMessage = "CHAT-REQUEST " + str(self.peerServer.peerServerPort)+ " " + self.username
            # logs the chat request sent to other peer
            logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + requestMessage)
            # sends the chat request
            self.tcpClientSocket.send(requestMessage.encode())
            # print("Request message " + requestMessage + " is sent...")
            print("Waiting for a response...")
            # received a response from the peer which the request message is sent to
            self.responseReceived = self.tcpClientSocket.recv(1024).decode()
            # logs the received message
            logging.info("Received from " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + self.responseReceived)
            # parses the response for the chat request
            self.responseReceived = self.responseReceived.split()
            # if response is ok then incoming messages will be evaluated as client messages and will be sent to the connected server
            if self.responseReceived[0] == "OK":
                print("You're chatting with " + self.responseReceived[1])
                # changes the status of this client's server to chatting
                self.peerServer.isChatRequested = 1
                # sets the server variable with the username of the peer that this one is chatting
                self.peerServer.chattingClientName = self.responseReceived[1]
                # as long as the server status is chatting, this client can send messages
                while self.peerServer.isChatRequested == 1:
                    # message input prompt
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> fixed alignment
                    print ("you:", end=" ")    
                    messageSent = input()
                    # sends the message to the connected peer, and logs it
                    self.tcpClientSocket.send(messageSent.encode())
                    logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                    # if the quit message is sent, then the server status is changed to not chatting
                    # and this is the side that is ending the chat
                    if messageSent == "quit":
                        self.peerServer.isChatRequested = 0
                        globals.ignore_input.clear()
                        self.isEndingChat = True
                        break
                # if peer is not chatting, checks if this is not the ending side
                if self.peerServer.isChatRequested != 1:
                    if not self.isEndingChat:
                        # tries to send a quit message to the connected peer
                        # logs the message and handles the exception
                        try:
                            self.tcpClientSocket.send("quit ending-side".encode())
                            logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> quit")
                        except BrokenPipeError as bpErr:
                            logging.error("BrokenPipeError: {0}".format(bpErr))
                    # closes the socket
                    self.responseReceived = None
                    self.tcpClientSocket.close()
            # if the request is rejected, then changes the server status, sends a reject message to the connected peer's server
            # logs the message and then the socket is closed       
            elif self.responseReceived[0] == "REJECT":
                print("Chat request is rejected")
                globals.ignore_input.clear()
                self.peerServer.isChatRequested = -1
                print("client of requester is closing...")
                self.tcpClientSocket.send("REJECT".encode())
                logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> REJECT")
                self.tcpClientSocket.close()
            # if a busy response is received, closes the socket
            elif self.responseReceived[0] == "BUSY":
                print("Receiver peer is busy")
                self.tcpClientSocket.close()
        # if the client is created with OK message it means that this is the client of receiver side peer
        # so it sends an OK message to the requesting side peer server that it connects and then waits for the user inputs.
        elif self.responseReceived == "OK":
            # server status is changed
            self.peerServer.isChatRequested = 1
            # ok response is sent to the requester side
            okMessage = "OK"
            self.tcpClientSocket.send(okMessage.encode())
            logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + okMessage)
            print("You're chatting with " + self.peerServer.chattingClientName)
            # client can send messsages as long as the server status is chatting
            while self.peerServer.isChatRequested == 1:
                # input prompt for user to enter message
                print ("you:", end=" ")    
                messageSent = input()
                self.tcpClientSocket.send(messageSent.encode())
                logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                # if a quit message is sent, server status is changed
                if messageSent == "quit":
                    self.peerServer.isChatRequested = 0
                    globals.ignore_input.clear()
                    self.isEndingChat = True
                    break
            # if server is not chatting, and if this is not the ending side
            # sends a quitting message to the server of the other peer
            # then closes the socket
            if self.peerServer.isChatRequested != 1:
                if not self.isEndingChat:
                    self.tcpClientSocket.send("quit ending-side".encode())
                    logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> quit")
                self.responseReceived = None
                self.tcpClientSocket.close()

    