from peer_server import *
import hashlib
import getpass
import ast
# main process of the peer
class peerMain:
    # peer initializations
    def __init__(self):
        # ip address of the registry
        self.registryName = gethostname()
        # port number of the registry
        self.registryPort = 15600
        # tcp socket connection to registry
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.registryName,self.registryPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = 15500
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None
        
        choice = "0"
        log_flag=False  # Am i logged in?
        i_flag=True     # input flag
        

        # log file initialization
        logging.basicConfig(filename="peer.log", level=logging.INFO)
        # as long as the user is not logged out, asks to select an option in the menu
        print("Welcome to Chating_club_19 ^^ ")
        
        
        while choice != "q":

            if not log_flag:
# >>>>>>>>>>>>>>>>>>>Create Account               
                while choice!= "n" and choice!="y": 
                    print("Have an Account?")
                    choice=input("[y] or [n]\n")
                    if choice!="y" and choice!="n":
                        print("invalid input!\n")

                if choice == "n":
                    print(">>Signup")
                    username = input("username: ")
                    password = getpass.getpass("Password: ")
                    password = hashlib.sha256(password.encode()).hexdigest()
                    self.createAccount(username, password)
                    i_flag=False
                    choice="y"

# >>>>>>>>>>>>>>>>>>>>>>>> login
                elif choice == "y" and not self.isOnline:
                    if i_flag:
                        print(">>login")
                        username = input("username: ")
                        # Get password input without echoing to the terminal
                        password = getpass.getpass("Password: ")
                        # Hash the password using SHA-256
                        password = hashlib.sha256(password.encode()).hexdigest()
                    print("trying Logging you in .....")

                    # Get New Port: -
                    sock = socket()
                    sock.bind(('', 0))
                    peerServerPort = sock.getsockname()[1]

                    status = self.login(username, password, peerServerPort)
                    # is user logs in successfully, peer variables are set
                    if status == 1:
                        self.isOnline = True
                        self.loginCredentials = (username, password)
                        self.peerServerPort = peerServerPort
                        
                        # creates the server thread for this peer, and runs it
                        self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort)
                        self.peerServer.start()
                        # hello message is sent to registry
                        self.sendHelloMessage()
                        print(f"Soket = {self.peerServer.tcpServerSocket}\n")
                        self.store_soket(username,self.peerServer.tcpServerSocket)
                        print( Fore.GREEN + f"Hello {username} ^^")
                        log_flag=True  # to know if he logged_in
                        i_flag=True    # Reset Flag

            else:
                choice=input("\nMain Menu: -\n1) Profile\n2) Show Online users\n3) search a user\n4) Chatrooms\n5) Logout\n                    press <q> to exit\n")
                # if choice is 3 and user is logged in, then user is logged out
                # and peer variables are set, and server and client sockets are closed


                if choice=="1":
                    searchStatus = self.searchUser(username)
                    split_values = searchStatus.split(":")
                    ip = split_values[0]
                    usr_port = split_values[1]
                    print(Fore.BLUE +  f"Username: {username}\nip: {ip}\nPort: {usr_port}")



                if choice=="2":
                    online_users=self.get_online_users()
                    print("\nOnline User: -")
                    for user in online_users:
                        if user != username:
                            print(Fore.BLUE + f">> {user}")
                

# >>>>>>>>>>>>>>>>>>>>>>> search a user
                if choice == "3" and self.isOnline:
                    search_user = input("Username to be searched: ")
                    searchStatus = self.searchUser(search_user)
                    # if user is found its ip address is shown to user
                    if searchStatus is not None and searchStatus != 0:
                        print("IP address of " + search_user + " is " + searchStatus)
                        print("\nDo you want to start chat with him?")
                        choice=input("press [y]:Yes or [n]:Not now\n")
                        if choice=="y":
                            choice = "4"
                            i_flag= False



# >>>>>>>>>>>>>>>>>>>>>>>> Start a chat
                if choice == "wla_7aga" and self.isOnline:
                    if i_flag:
                        username = input("Enter the username of user to start chat: ")
                        searchStatus = self.searchUser(username)
                    i_flag=True
                    # if searched user is found, then its ip address and port number is retrieved
                    # and a client thread is created
                    # main process waits for the client thread to finish its chat
                    if searchStatus is not None and searchStatus != 0:
                        # Check if the variable is a list
                        if not isinstance(searchStatus, list):
                            searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]) , self.loginCredentials[0], self.peerServer, None)
                        self.peerClient.start()
                        self.peerClient.join()

                if choice =="4" and self.isOnline:
                    while choice !="b":
                        choice=input("\nChat rooms menu: -\n1) My Rooms\n2) Create Room\n3) Show Chat rooms\n4) Search or Join Chat room\n                        press <b> to go back to main menu\n")
                        

                        if choice =="1":
                            while choice!="b":
                                Joined_rooms = self.get_Chatrooms(username)
                                if Joined_rooms is not None:
                                    print("Joined Chat Rooms: -")
                                    for chatroom in Joined_rooms:
                                        print(Fore.BLUE + f">> {chatroom}")
                                    choice = input("\n1) Leave a room\n2) Enter Room\n                        press <b> to go back to chat room menu\n")
                                    if choice == "1":
                                        r_name=input("Enter Room Name: ")
                                        self.LeaveRoom(r_name,username)
                                        print("Making Another Check....")
                                    elif choice =="2":
                                        self.run_chatroom(room_name, username, self.peerServer)  # Start chat room functionality
                                        ss=self.get_sokets()
                                        print(f"sokets: -\n{ss}")
                                else:
                                    print(Fore.RED + "You are not in any room :(")
                                    choice = "b"
                                

                        elif choice=="2":
                            print(">> Create Room: -")
                            room_name = input("Room Name: ")
                            password = input("Password: ")
                            self.CreateRoom(room_name, password, username)

                        elif choice == "3":
                            Chatrooms=self.get_Chatrooms(" ")
                            print("Chat Rooms: -")
                            for chatroom in Chatrooms:
                                print(Fore.BLUE + f">> {chatroom}")

                        elif choice =="4":
                            print("Search ChatRoom: -")
                            room_name = input("Enter the room_name: ")
                            Admin,users = self.Search_room(room_name)
                            if Admin is not None:
                                print(Fore.YELLOW + f"Admin: {Admin}")
                                print(Fore.BLUE + f"Users: {users}")
                                print("Do you want to Join the Chatroom?")
                                choice=input("[y]:yes / [n]:no\n")
                                room_status = 3
                                if choice =="y":
                                    while room_status==3:
                                        room_pass = input("Enter room Password: ")
                                        room_status = self.join_chat(room_name,room_pass,username)
                                        #sokets=self.get_sokets()
                                        #print(f"sokets = {sokets}")
                        choice="reset"
                                        

                
                if choice == "5" and self.isOnline:
                    self.logout(1)
                    self.isOnline = False
                    self.loginCredentials = (None, None)
                    self.peerServer.isOnline = False
                    self.peerServer.tcpServerSocket.close()
                    if self.peerClient is not None:
                        self.peerClient.tcpClientSocket.close()
                    print("Logged out successfully\n")
                    choice="q"
                    log_flag=False
                    del self  # To reserve memory
                    new_obj=peerMain()  # to initialize a new peer after he Logs out!
                    


                # if this is the receiver side then it will get the prompt to accept an incoming request during the main loop
                # that's why response is evaluated in main process not the server thread even though the prompt is printed by server
                # if the response is ok then a client is created for this peer with the OK message and that's why it will directly
                # sent an OK message to the requesting side peer server and waits for the user input
                # main process waits for the client thread to finish its chat
                elif choice == "OK" and self.isOnline:
                    okMessage = "OK " + self.loginCredentials[0]
                    logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                    self.peerServer.connectedPeerSocket.send(okMessage.encode())
                    self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort , self.loginCredentials[0], self.peerServer, "OK")
                    self.peerClient.start()
                    self.peerClient.join()

                # if user rejects the chat request then reject message is sent to the requester side
                elif choice == "REJECT" and self.isOnline:
                    self.peerServer.connectedPeerSocket.send("REJECT".encode())
                    self.peerServer.isChatRequested = 0
                    logging.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")

                # if choice is cancel timer for hello message is cancelled
                elif choice == "CANCEL":
                    self.timer.cancel()
                    break

        # if main process is not ended with cancel selection
        # socket of the client is closed
        if choice != "CANCEL":
            self.tcpClientSocket.close()


    # room creation function
    def CreateRoom(self, room_name, password,Admin):
        message = "CREATE " + room_name + " " + password + " " + Admin
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print(f"Chat room '{room_name}' created by {Admin}.")
        elif response == "join-exist":
            print("Room name exists!")

    def store_soket(self,username,soket):
        message = "STORE " + username + " " + str(soket)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
    
    def get_sokets(self):
        message = "GETSOKETS "
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        # Use ast.literal_eval to safely evaluate the string as a dictionary
        try:
            sockets_dict = ast.literal_eval(response)
            return sockets_dict
        except (SyntaxError, ValueError) as e:
            logging.error("Error parsing response: " + str(e))
            return None

    def Search_room(self, room_name):
        message = "ROOM " + room_name
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "search-success":
            print(room_name + " is found successfully...\n")
            return response[1],response[2:]   # 1: Admin , 2: Users list
        elif response[0] == "search-Room-not-found":
            print(room_name + " is not found")
            return None
        
    # Join room function
    def join_chat(self, room_name,room_pass,username):
        message = "JoinRoom " + room_name + " " + room_pass + " " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print(f"Joined {room_name} successfully...")
            return 1
        elif response =="Already-in":
            print("You already in the chat room!")
            return 2
        elif response == "Wrong-pass":
            print(f"{response} Try again\n")
            return 3
        
    def LeaveRoom(self,room_name,username):
        message = "Leave "+ room_name +" "+ username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        print(response)


    def get_online_users(self):
        message = "GET_USERS "
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        return response
    
    def get_Chatrooms(self,username):
        message = "GET_ROOMS " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response != "no-rooms":
            response=response.split()
            logging.info("Received from " + self.registryName + " -> " + " ".join(response))
            return response
        else:
            logging.info("Received from " + self.registryName + " -> " + response)
            return None
            
    
    
    # account creation function
    def createAccount(self, username, password):
        # join message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response is exist then informs the user for account existence
        message = "JOIN " + username + " " + password
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print("Account created...")
        elif response == "join-exist":
            print("choose another username or login...")

    # login function
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
            print("Logged in successfully...")
            return 1
        elif response == "login-account-not-exist":
            print("Account does not exist...")
            return 0
        elif response == "login-online":
            print("Account is already online...")
            return 2
        elif response == "login-wrong-password":
            print("Wrong password...")
            return 3
    
    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        

    # function for searching an online user
    def searchUser(self, username):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "SEARCH " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "search-success":
            print(username + " is found successfully...")
            return response[1]
        elif response[0] == "search-user-not-online":
            print(username + " is not online...")
            return 0
        elif response[0] == "search-user-not-found":
            print(username + " is not found")
            return None
    
    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of registry
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        logging.info("Send to " + self.registryName + ":" + str(self.registryUDPPort) + " -> " + message)
        self.udpClientSocket.sendto(message.encode(), (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage) # status control
        self.timer.start()

# peer is started
main = peerMain()