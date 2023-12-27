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
from colorama import init, Fore, Back, Style


init(autoreset=True)

# Server side of peer
class PeerServer(threading.Thread):


    # Peer server initialization
    def __init__(self, username, peerServerPort):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        # port number of the peer server
        self.peerServerPort = peerServerPort
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

        self.isChatRoom = 0
    

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
        # inputs sockets that should be listened
        inputs = [self.tcpServerSocket]
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
                        if self.isChatRequested == 0:     
                            print(self.username + " is connected from " + str(addr))
                            self.connectedPeerSocket = connected
                            self.connectedPeerIP = addr[0]
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
                    else:
                        # message is received from connected peer
                        message_received = s.recv(1024).decode()
                        # logs the received message
                        logging.info("Received from " + str(self.connectedPeerIP) + " -> " + str(message_received))
                        # if message is a request message it means that this is the receiver side peer server
                        # so evaluate the chat request
                        if self.isChatRoom == 1:
                            group_message = f"{self.username}: {message_received[12:]}"
                            print("hereeeeeeeeeeeeeeeeeeeeee")
                            print(Fore.RED + messageReceived)
            # handles the exceptions, and logs them
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))
        

class PeerClient(threading.Thread):
    def __init__(self, ip_to_connect, port_to_connect, username, peer_server, response_received):
        threading.Thread.__init__(self)
        self.ipToConnect = ip_to_connect
        self.username = username
        self.portToConnect = port_to_connect
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.peerServer = peer_server
        self.responseReceived = response_received
        self.isEndingChat = False

    def run(self):
        print("Peer client started...")
        self.tcpClientSocket.connect((self.ipToConnect, self.portToConnect))

        if self.peerServer.isChatRequested == 0 and self.responseReceived is None:
            self.initiate_chatroom()

    def initiate_chatroom(self):
        self.peerServer.isChatRequested = 1
        self.peerServer.isChatRoom = 1
        self.peerServer.chattingClientName = self.username
        self.run_chatroom()

    def run_chatroom(self):
        print(f"Welcome to Chat Room with {self.peerServer.chattingClientName}")
        print("Type your messages or type 'exit' to leave the chat room.")

        while self.peerServer.isChatRequested == 1:
            message = input("Your message: ")
            if message.lower() == 'exit':
                print("Leaving the chat room.")
                self.peerServer.isChatRequested = 0
                self.isEndingChat = True
                break

            if message.startswith("GROUP-CHAT: "):
                self.send_group_chat_message(message)
            else:
                self.send_private_message(message)

    def send_group_chat_message(self, message):
        group_message = f"GROUP-CHAT: {message[12:]}"
        self.tcpClientSocket.send(group_message.encode())

    def send_private_message(self, message):
        private_message = f"{self.peerServer.chattingClientName}: {message}"
        self.tcpClientSocket.send(private_message.encode())

    def broadcast_group_chat_message(self, message, sender_socket):
        for s in inputs:
            if s != self.tcpServerSocket and s != sender_socket:
                try:
                    s.send(message.encode())
                except:
                    s.close()
                    inputs.remove(s)