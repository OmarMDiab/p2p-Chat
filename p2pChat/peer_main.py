from peer_server import *
import hashlib
import getpass
import ast
import pickle
import globals
import logging
from socket import gaierror, timeout
# main process of the peer
class peerMain:
    # peer initializations
    def __init__(self):
        try:
            # ip address of the registry
            self.registryName = gethostname()
            # port number of the registry
            self.registryPort = 15600
            # tcp socket connection to registry
            self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
            self.tcpClientSocket.connect((self.registryName, self.registryPort))
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
        except (gaierror, timeout) as e:
            logging.error(f"Network error during initialization: {e}")
            exit("Failed to initialize network settings.")

        choice = "0"
        log_flag = False  # Am i logged in?
        i_flag = True     # input flag
        
        # log file initialization
        logging.basicConfig(filename="peer.log", level=logging.INFO)
        # as long as the user is not logged out, asks to select an option in the menu
        print("Welcome to Chating_club_19 ^^ ")
        
        while choice != "q":
            try:
                if not log_flag:
                    while choice != "n" and choice != "y": 
                        print("Have an Account?")
                        choice = input("[y] or [n]\n")
                        if choice != "y" and choice != "n":
                            print("invalid input!\n")

                    if choice == "n":
                        print(">>Signup")
                        username = input("username: ")
                        password = getpass.getpass("Password: ")
                        password = hashlib.sha256(password.encode()).hexdigest()
                        self.create_new_account(username, password)
                        i_flag = False
                        choice = "y"
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
                        
                        sockUDP = socket(AF_INET, SOCK_DGRAM) 
                        sockUDP.bind(('', 0))
                        peerServerUDPPort = sockUDP.getsockname()[1]
                        
                        status = self.login(username, password, peerServerPort, peerServerUDPPort)
                        # is user logs in successfully, peer variables are set
                        if status == 1:
                            self.isOnline = True
                            self.loginCredentials = (username, password)
                            self.peerServerPort = peerServerPort
                            self.peerServerUDPPort = peerServerUDPPort
                            
                            # creates the server thread for this peer, and runs it
                            self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort, self.peerServerUDPPort)
                            self.peerServer.start()
                            
                            # hello message is sent to registry
                            self.sendHelloMessage()
                            print(f"Soket = {self.peerServer.tcpServerSocket}\n")
                            self.store_soket(username,self.peerServer.tcpServerSocket)
                            print(Fore.GREEN + f"Hello {username} ^^")
                            log_flag = True  # to know if he logged_in
                            i_flag = True    # Reset Flag
            

                else:
                    try:
                        choice = input("\nMain Menu: -\n1) Profile\n2) Show Online users\n3) search a user\n4) Chatrooms\n5) Logout\n                    press <q> to exit\n")

                        # Profile viewing
                        if choice == "1":
                            try:
                                searchStatus = self.search_for_user(username)
                                if searchStatus:
                                    split_values = searchStatus.split(":")
                                    ip = split_values[0]
                                    user_tcp_port = split_values[1]
                                    user_udp_port = split_values[2]
                                    print(Fore.BLUE +  f"Username: {username}\nip: {ip}\nTCP Port: {user_tcp_port}\nUDP Port: {user_udp_port}")
                                else:
                                    print("Failed to retrieve profile information.")
                            except Exception as e:
                                logging.error(f"Error retrieving profile: {e}")
                                print("Error occurred while fetching profile information.")

                        # Show online users
                        elif choice == "2":
                            try:
                                online_users = self.get_online_users()
                                print("\nOnline Users: -")
                                for user in online_users:
                                    if user != username:
                                        print(Fore.BLUE + f">> {user}")
                            except Exception as e:
                                logging.error(f"Error fetching online users: {e}")
                                print("Error occurred while fetching online users.")

                        # Search a user
                        elif choice == "3" and self.isOnline:
                            try:
                                search_user = input("Username to be searched: ")
                                searchStatus = self.search_for_user(search_user)
                                if searchStatus is not None and searchStatus != 0:
                                    print("IP address of " + search_user + " is " + searchStatus)
                                    print("\nDo you want to start chat with them?")
                                    choice = input("press [y]:Yes or [n]:Not now\n")
                                    if choice == "y":
                                        choice = "4"
                                        i_flag = False
                                else:
                                    print("User not found or error occurred.")
                            except Exception as e:
                                logging.error(f"Error searching user: {e}")
                                print("Error occurred while searching for user.")

                        # Start a chat
                        elif choice == "wla_7aga" and self.isOnline:
                            try:
                                if i_flag:
                                    username = input("Enter the username of user to start chat: ")
                                    searchStatus = self.search_for_user(username)
                                i_flag = True
                                if searchStatus is not None and searchStatus != 0:
                                    if not isinstance(searchStatus, list):
                                        searchStatus = searchStatus.split(":")
                                    self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]), self.loginCredentials[0], self.peerServer, None)
                                    self.peerClient.start()
                                    self.peerClient.join()
                                else:
                                    print("User not found or error occurred.")
                            except Exception as e:
                                logging.error(f"Error starting chat: {e}")
                                print("Error occurred while starting chat.")

                        # Chatroom management
                        elif choice == "4" and self.isOnline:
                            while choice != "b":
                                try:
                                    choice = input("\nChat rooms menu: -\n1) My Rooms\n2) Create Room\n3) Show Chat rooms\n4) Search or Join Chat room\n                        press <b> to go back to main menu\n")
                                    
                                    # My Rooms
                                    if choice == "1":
                                        while choice != "b":
                                            Joined_rooms = self.get_all_rooms(username)
                                            if Joined_rooms is not None:
                                                print("Joined Chat Rooms: -")
                                                for chatroom in Joined_rooms:
                                                    print(Fore.BLUE + f">> {chatroom}")
                                                choice = input("\n1) Leave a room\n2) Enter Room\n                        press <b> to go back to chat room menu\n")
                                                if choice == "1":
                                                    r_name = input("Enter Room Name: ")
                                                    self.leave_room(r_name, username)
                                                    print("Making Another Check....")
                                                elif choice == "2":
                                                    room_name = input("Enter Room Name: ")
                                                    self.enter_chat_room(room_name, username)
                                            else:
                                                print(Fore.RED + "You are not in any room :(")
                                                choice = "b"
                                

                                    # Create Room
                                    elif choice == "2":
                                        try:
                                            print(">> Create Room: -")
                                            room_name = input("Room Name: ")
                                            password = input("Password: ")
                                            self.create_new_room(room_name, password, username)
                                        except Exception as e:
                                            logging.error(f"Error creating room: {e}")
                                            print("Error occurred while creating room.")

                                    # Show Chat rooms
                                    elif choice == "3":
                                        try:
                                            Chatrooms = self.get_all_rooms(" ")
                                            print("Chat Rooms: -")
                                            for chatroom in Chatrooms:
                                                print(Fore.BLUE + f">> {chatroom}")
                                        except Exception as e:
                                            logging.error(f"Error fetching chat rooms: {e}")
                                            print("Error occurred while fetching chat rooms.")

                                    # Search or Join Chat room
                                    elif choice == "4":
                                        try:
                                            print("Search ChatRoom: -")
                                            room_name = input("Enter the room_name: ")
                                            Admin, users = self.search_for_room(room_name)
                                            if Admin is not None:
                                                print(Fore.YELLOW + f"Admin: {Admin}")
                                                print(Fore.BLUE + f"Users: {users}")
                                                print("Do you want to Join the Chatroom?")
                                                choice = input("[y]:yes / [n]:no\n")
                                                room_status = 3
                                                if choice == "y":
                                                    while room_status == 3:
                                                        room_pass = input("Enter room Password: ")
                                                        room_status = self.join_room_chat(room_name, room_pass, username)
                                        except Exception as e:
                                            import traceback
                                            logging.error(f"Error in searching or joining chat room: {traceback.format_exc()}")
                                            print("Error occurred while handling chat rooms.")
                                        choice = "reset"
                                    
                                except Exception as e:
                                    logging.error(f"Error in chatroom management: {e}")
                                    print("Error occurred in chatroom management.")
                                    break
                        # Logout
                        elif choice == "5" and self.isOnline:
                            self.logout(1)
                            self.isOnline = False
                            self.loginCredentials = (None, None)
                            self.peerServer.isOnline = False
                            self.peerServer.tcpServerSocket.close()
                            if self.peerClient is not None:
                                self.peerClient.tcpClientSocket.close()
                            print("Logged out successfully\n")
                            choice = "q"
                            log_flag = False
                            del self  # To reserve memory
                            new_obj = peerMain()  # to initialize a new peer after logout!
                    except Exception as e:
                        logging.error(f"Error in main menu: {e}")
                        print("An unexpected error occurred in the main menu. Please try again.")
                        choice = "q"  # Exiting the loop in case of an unexpected error

            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                print("An unexpected error occurred. Please try again.")
                break
        # if main process is ended with quit selection
        if choice == "q":
            print("Exiting the application. Goodbye!")
            self.cleanup_resources()
            
            
        # if main process is not ended with cancel selection
        # socket of the client is closed
        if choice != "CANCEL":
            self.tcpClientSocket.close()
    
    def cleanup_resources(self):
        try:
            if self.isOnline:
                self.logout(1)
                self.peerServer.isOnline = False
                self.peerServer.tcpServerSocket.close()
                if self.peerClient is not None:
                    self.peerClient.tcpClientSocket.close()
            print("Resources cleaned up successfully.")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")       
            
    def enter_chat_room(self, room_name, username):
        try:
            # Sending request to join room
            message = "GET_ROOM " + room_name
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving response
            response = pickle.loads(self.tcpClientSocket.recv(1024))
            logging.info(f"Received from {self.registryName} -> {response}")

            # Handling response
            if response.get("result") == "success":
                print(f"You joined {room_name} room successfully...")
                globals.room_users = response.get("users", [])
                globals.joined_room_name = room_name
            else:
                print("Could not join the room!")
                return

            with socket(AF_INET, SOCK_DGRAM) as sender_socket:
                me = next((user for user in globals.room_users if user['username'] == username), None)
                
                if not me:
                    print("Error: User not found in room users.")
                    return

                self.send_message_to_room_users(sender_socket, f"{username} joined the room", me, room_name)
                
                # Chat loop
                while True:
                    message = input()
                    if message.lower() == "exit":
                        globals.room_users = []
                        globals.joined_room_name = ""
                        print("Exiting the room...")
                        break
                    else:
                        self.send_message_to_room_users(sender_socket, f"{username}: {message}", me, room_name)
        except Exception as e:
            logging.error(f"Error in enter_chat_room: {e}")
            print("An error occurred while entering the chat room.")
                
    def send_message_to_room_users(self, sender_socket, message, me, room_name):
        data = { 
            "message": message,
            "user": me,
            "room_name": room_name
        }

        for user in globals.room_users: 
            if user['username'] != me["username"]:
                try:
                    # Serialize the data using pickle
                    serialized_data = pickle.dumps(data)
                    sender_socket.sendto(serialized_data, (user['ip'], int(user['portUDP'])))
                except Exception as e:
                    print(f"Error sending message to {user['username']}: {e}")
                    continue

    # room creation function
    def create_new_room(self, room_name, password, Admin):
        try:
            # Constructing and sending the room creation message
            message = "CREATE " + room_name + " " + password + " " + Admin
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()
            logging.info(f"Received from {self.registryName} -> {response}")

            # Handling different responses
            if response == "join-success":
                print(f"Chat room '{room_name}' created by {Admin}.")
            elif response == "join-exist":
                print("Room name exists!")
            else:
                print("Unexpected response from the server.")
        except Exception as e:
            logging.error(f"Error in create_new_room: {e}")
            print("An error occurred while creating the chat room.")

    def search_for_room(self, room_name):
        try:
            # Constructing and sending the search room message
            message = "ROOM " + room_name
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode().split()
            logging.info(f"Received from {self.registryName} -> {' '.join(response)}")
            
            # Handling different responses
            if response[0] == "search-success":
                print(f"{room_name} is found successfully...\n")
                return response[1], response[2:]  # 1: Admin, 2: Users list
            elif response[0] == "search-Room-not-found":
                print(f"{room_name} is not found")
                return None
            else:
                print("Unexpected response from the server.")
                return None
        except Exception as e:
            logging.error(f"Error in search_for_room: {e}")
            print("An error occurred while searching for the room.")
            return None
        
    def join_room_chat(self, room_name, room_pass, username):
        try:
            # Constructing and sending the join room message
            message = f"JoinRoom {room_name} {room_pass} {username}"
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()
            logging.info(f"Received from {self.registryName} -> {response}")

            # Handling different responses
            if response == "join-success":
                print(f"Joined {room_name} successfully...")
                return 1
            elif response == "Already-in":
                print("You are already in the chat room!")
                return 2
            elif response == "Wrong-pass":
                print("Incorrect password. Try again.")
                return 3
            else:
                print("Unexpected response from the server.")
                return -1
        except Exception as e:
            logging.error(f"Error in join_room_chat: {e}")
            print("An error occurred while joining the chat room.")
            return -1

        
    def leave_room(self, room_name, username):
        try:
            # Constructing and sending the leave room message
            message = f"Leave {room_name} {username}"
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()
            logging.info(f"Received from {self.registryName} -> {response}")

            # Print the server response
            print(response)

        except Exception as e:
            logging.error(f"Error in leave_room: {e}")
            print("An error occurred while trying to leave the room.")

    def get_online_users(self):
        try:
            # Constructing and sending the get online users message
            message = "GET_USERS "
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode().split()
            logging.info(f"Received from {self.registryName} -> {' '.join(response)}")

            # Returning the response
            # The response format can be modified here if needed, based on how the server sends the online users list
            return response
        except Exception as e:
            logging.error(f"Error in get_online_users: {e}")
            print("An error occurred while fetching online users.")
            return []
    
    def get_all_rooms(self, username):
        try:
            # Constructing and sending the get all rooms message
            message = f"GET_ROOMS {username}"
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()

            # Checking and handling the response
            if response != "no-rooms":
                rooms = response.split()
                logging.info(f"Received from {self.registryName} -> {' '.join(rooms)}")
                return rooms
            else:
                logging.info(f"Received from {self.registryName} -> {response}")
                print(f"No rooms found for {username}.")
                return None
        except Exception as e:
            logging.error(f"Error in get_all_rooms: {e}")
            print("An error occurred while fetching the rooms.")
            return None

    # account creation function
    def create_new_account(self, username, password):
        try:
            # Constructing and sending the account creation message
            message = f"CREATE_NEW_ACCOUNT {username} {password}"
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()
            logging.info(f"Received from {self.registryName} -> {response}")

            # Handling different responses
            if response == "join-success":
                print("Account created successfully.")
            elif response == "join-exist":
                print("Username already exists, please choose another username or login.")
            else:
                print("Unexpected response from the server.")
        except Exception as e:
            logging.error(f"Error in create_new_account: {e}")
            print("An error occurred while creating a new account.")


    # login function
    def login(self, username, password, peerServerPort, peerServerUDPPort):
        try:
            # Constructing and sending the login message
            message = f"LOGIN {username} {password} {peerServerPort} {peerServerUDPPort}"
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()
            logging.info(f"Received from {self.registryName} -> {response}")

            # Handling different responses
            if response == "login-success":
                print("Logged in successfully.")
                return 1
            elif response == "login-account-not-exist":
                print("Account does not exist.")
                return 0
            elif response == "login-online":
                print("Account is already online.")
                return 2
            elif response == "login-wrong-password":
                print("Wrong password.")
                return 3
            else:
                print("Unexpected response from the server.")
                return -1
        except Exception as e:
            logging.error(f"Error in login: {e}")
            print("An error occurred while trying to log in.")
            return -1
   
    # logout function
    def logout(self, option):
        try:
            # a logout message is composed and sent to registry
            # timer is stopped
            if option == 1:
                message = "LOGOUT " + self.loginCredentials[0]
                self.timer.cancel()
            else:
                message = "LOGOUT"
            logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
            self.tcpClientSocket.send(message.encode())  
        except Exception as e:
            logging.error(f"Error in logout: {e}")
            print("An error occurred while trying to log out.")
            return -1

    # function for searching an online user
    def search_for_user(self, username):
        try:
            # Constructing and sending the search user message
            message = f"SEARCH {username}"
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode().split()
            logging.info(f"Received from {self.registryName} -> {' '.join(response)}")

            # Handling different responses
            if response[0] == "search-success":
                print(f"{username} is found successfully.")
                # Assuming the IP address of the user is the second element in the response
                return response[1]
            elif response[0] == "search-user-not-online":
                print(f"{username} is not online.")
                return 0
            elif response[0] == "search-user-not-found":
                print(f"{username} is not found.")
                return None
            else:
                print("Unexpected response from the server.")
                return None
        except Exception as e:
            logging.error(f"Error in search_for_user: {e}")
            print("An error occurred while searching for the user.")
            return None

        
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