from peer_server import *
import hashlib
import getpass
import ast
import pickle
import globals
import logging
from socket import gaierror, timeout
import inquirer
import os
from tabulate import tabulate
import random
import re
import webbrowser

# main process of the peer
class peerMain:
    # peer initializations
    def __init__(self, message = 'Welcome to Club House CLI of Group 19 🥰'):
        self.setup_network()
        self.main_menu(0, message)
                    
    def setup_network(self):
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
            
            # log file initialization
            logging.basicConfig(filename="peer.log", level=logging.INFO)
        except (gaierror, timeout) as e:
            logging.error(f"Network error during initialization: {e}")
            exit("Failed to initialize network settings.")
    
    def styleAsError(self, error):
        return Fore.RED + Style.BRIGHT + error + Style.RESET_ALL
    def styleAsSuccess(self, success):
        return Fore.GREEN + Style.BRIGHT + success + Style.RESET_ALL
    def styleAsWarning(self, warning):
        return Fore.YELLOW + Style.BRIGHT + warning + Style.RESET_ALL
    def styleAsInfo(self, info):
        return Fore.BLUE + Style.BRIGHT + info + Style.RESET_ALL
    def styleAsQuestion(self, question):
        return Fore.CYAN + Style.BRIGHT + question + Style.RESET_ALL
    def styleAsInput(self, input):
        return Fore.MAGENTA + Style.BRIGHT + input + Style.RESET_ALL
    def getStyledInput(self, title=""):
        return input(Fore.MAGENTA + title)
    def styleAsReset(self, reset):
        return Style.RESET_ALL + reset
    
    
    def main_menu(self, intialChoice = 0, intitalTitle = "Welcome to Club House CLI of Group 19 🥰"):
        os.system('cls')
        print(intitalTitle + "\n")
        choice = intialChoice
        options = ["Signup", "Login", "Exit the application"]
        titleForOptions = ["Creating New Account", "Logging In", "Exiting the application"]

        if choice == 0: # Select an option
            questions = [inquirer.List('auth_choice',message="Please select an option",choices=options,carousel=True)]
            answers = inquirer.prompt(questions)
            choice = options.index(answers['auth_choice']) + 1
            return self.main_menu(choice, self.styleAsInfo(titleForOptions[choice-1])) # redirect to the required page
        
        elif choice == 1: # Signup
            print("Enter your username: ")
            username = self.getStyledInput()
            print(Fore.RESET + "Enter your password: ")
            password = getpass.getpass('')
            print("Confirm your password: ")
            confirm_password = getpass.getpass('')
            if(password != confirm_password):
                return self.main_menu(1, self.styleAsError("Passwords do not match. Please try again.")) # redirect to main menu
            password = hashlib.sha256(password.encode()).hexdigest()
            status = self.create_new_account(username, password)
            if status == 1:
                return self.main_menu(2, self.styleAsSuccess("Account created successfully, please login")) # redirect to login
            else: # username already exist, internal server error
                return self.main_menu(0, self.styleAsError(status + " Please try again")) # redirect to main menu
            
        elif choice == 2: # Login
            print("Enter your username: ")
            username = self.getStyledInput()
            print(Fore.RESET + "Enter your password: ")
            password = getpass.getpass()
            password = hashlib.sha256(password.encode()).hexdigest() # Hashing the password using SHA-256
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
                print(Fore.GREEN + Style.BRIGHT + "Logged In Successfully" + Style.RESET_ALL)
                self.isOnline = True
                self.loginCredentials = (username, password)
                self.peerServerPort = peerServerPort
                self.peerServerUDPPort = peerServerUDPPort
                
                # creates the server thread for this peer, and runs it
                self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort, self.peerServerUDPPort)
                self.peerServer.start()
                
                # hello message is sent to registry
                self.sendHelloMessage()
                self.store_soket(username,self.peerServer.tcpServerSocket)
                print()
                # Show next menu
                self.select_menu(0, self.styleAsInfo(f"Hello {username}"))
            else: # wrong password, or already online
                return self.main_menu(0, status + " Please try again") # redirect to main menu
            

        
            

    def select_menu(self, intialChoice = 0, intitalTitle = "Please select an option: "):
        os.system('cls')
        if(globals.ignore_input.is_set()):
            return self.one_to_one_chat_menu()
        print(intitalTitle + "\n")
        choice = intialChoice
        options = ["View Profile", "Show Online Users", "Chatrooms", "Logout",Fore.RED + "Delete Account", "Exit the application"]

        if choice == 0: # Select an option
            questions = [inquirer.List('main_choice',message="Please select an option",choices=options,carousel=True)]
            answers = inquirer.prompt(questions)
            choice = options.index(answers['main_choice']) + 1
            return self.select_menu(choice, self.styleAsInfo(answers['main_choice'])) # redirect to the required page
        

        elif choice == 1: # View Profile
            try:
                searchStatus = self.search_for_user(self.loginCredentials[0])
                if searchStatus:
                    split_values = searchStatus.split(":")
                    ip = split_values[0]
                    user_tcp_port = split_values[1]
                    user_udp_port = split_values[2]
                    table = [
                                ["Username", self.styleAsQuestion(self.loginCredentials[0])],
                                ["IP", self.styleAsQuestion(ip)],
                                ["TCP Port", self.styleAsQuestion(user_tcp_port)],
                                ["UDP Port", self.styleAsQuestion(user_udp_port)]  
                            ]
                    print(tabulate(table, tablefmt='fancy_grid'))
                    input("Press Enter to return to main menu")
                    return self.select_menu(0)
                else:
                    return self.select_menu(0, "Failed to retrieve profile information. Please try again.")
            except Exception as e:
                logging.error(f"Error retrieving profile: {e}")
                return self.select_menu(0, "Error occurred while fetching profile information. Please try again.")
            
        elif choice == 2: # Show Online Users
            try:
                online_users = self.get_online_users()
                # check if the user is online, and remove it from the list
                if self.loginCredentials[0] in online_users:
                    online_users.remove(self.loginCredentials[0])
                if online_users:
                    online_users.append("Go back to Main Menu")
                    questions = [inquirer.List('user',message="Please select a user",choices=online_users,carousel=True)]
                    answers = inquirer.prompt(questions)
                    selectedUser = answers['user']
                    if selectedUser == "Go back to Main Menu":
                        return self.select_menu(0)
                    searchStatus = self.search_for_user(selectedUser)
                    if searchStatus:
                        if not isinstance(searchStatus, list):
                            searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]), self.loginCredentials[0], self.peerServer, None)
                        self.peerClient.start()
                        self.peerClient.join()
                        title = f"{selectedUser} has rejected your request" if self.peerServer.isChatRequested == -1 else f"Chat with {selectedUser} has ended"
                        return self.select_menu(0, self.styleAsError(title))
                    else:
                        return self.select_menu(2, self.styleAsError("User not found or error occurred. Please try again."))
                else:
                    return self.select_menu(0, self.styleAsError("There are no Online Users"))
                
            except Exception as e:
                logging.error(f"Error fetching online users: {e}")
                return self.select_menu(0, "Error occurred while fetching online users. Please try again.")   
            
        elif choice == 3: # Chatroom management
            return self.chatroom_menu(0, self.styleAsInfo("Chatroom management"))
        
        elif choice == 4: # Logout
            self.logout(1)
            self.isOnline = False
            name = self.loginCredentials[0]
            self.loginCredentials = (None, None)
            self.peerServer.isOnline = False
            self.peerServer.tcpServerSocket.close()
            if self.peerClient is not None:
                self.peerClient.tcpClientSocket.close()
            
            return self.CreateNewPeer(self.styleAsSuccess(f"{name} Logged Out Successfully!"))
        
        elif choice == 5: # Delete Account
            if self.delete_account(self.loginCredentials[0]):
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                self.peerServer.isOnline = False
                self.peerServer.tcpServerSocket.close()
                if self.peerClient is not None:
                    self.peerClient.tcpClientSocket.close()
                
                return self.CreateNewPeer(self.styleAsSuccess("Your Account is Deleted Successfully!"))
            else:
                return self.select_menu(0, self.styleAsError("error in deleting your Account"))
            
        elif choice == 6: # Exit the application
            self.cleanup_resources()
            exit("Exiting the application. Goodbye!")

    
    def chatroom_menu(self, intialChoice = 0, intitalTitle = "Chatrooms Management"):
        os.system('cls')
        print(intitalTitle + "\n")
        choice = intialChoice

        options = ["My Rooms", "Create New Room", "Search/Join Chat room", "Go back to main menu"]

        if choice == 0: # Select an option
            questions = [inquirer.List('room_main_choice',message="Please select an option",choices=options,carousel=True)]
            answers = inquirer.prompt(questions)
            choice = options.index(answers['room_main_choice']) + 1
            return self.chatroom_menu(choice, self.styleAsInfo(answers['room_main_choice'])) # redirect to the required page
        
        elif choice == 1: # My Rooms
            try:
                Joined_rooms = self.get_all_rooms(self.loginCredentials[0])
                if Joined_rooms is not None:
                    options = Joined_rooms
                    options.append("Go back to chat room menu")
                    questions = [inquirer.List('room_choice',message="Select a room",choices=options,carousel=True)]
                    answers = inquirer.prompt(questions)
                    room_name = answers['room_choice']                    
                    
                    if room_name == "Go back to chat room menu":
                        return self.chatroom_menu(0)
                    else:
                        self.room_menu(room_name,0,"")    
                else:
                    self.chatroom_menu(0, self.styleAsError("You are not in any room"))
            except Exception as e:
                logging.error(f"Error in chatroom management: {e}")
                return self.chatroom_menu(0, self.styleAsError("Error occurred while fetching chat rooms. Please try again."))
            
        elif choice == 2: # Create Room
            try:
                print("Enter Room Name:")
                room_name = self.getStyledInput()
                print(Fore.RESET + "Enter a password for " + self.styleAsInput(room_name) + " room:")
                password = getpass.getpass("")
                username = self.loginCredentials[0]
                status = self.create_new_room(room_name, password, username)
                if status == 1:
                    return self.chatroom_menu(0, self.styleAsInput(room_name) + self.styleAsInfo(" room was created successfully"))
                else : 
                    return self.chatroom_menu(0, self.styleAsError(status + " Please try again"))
                
            except Exception as e:
                logging.error(f"Error creating room: {e}")
                return self.chatroom_menu(2, self.styleAsError("Error occurred while creating room. Please try again.")) 
            

        elif choice == 3: # Search or Join Chat room
            try:
                print("Enter the room name:")
                room_name = self.getStyledInput()  
                Admin, users = self.search_for_room(room_name)
                if Admin is not None:
                    print(Fore.LIGHTYELLOW_EX + f"Admin: {Admin}")
                    print(Fore.LIGHTBLUE_EX + f"Users: {users}" + Fore.RESET)
                    print()
                    questions = [
                        inquirer.Confirm("join_room", message="Do you want to Join the Chatroom?", default=True),
                    ]
                    answers = inquirer.prompt(questions)
                    
                    if answers["join_room"]:
                        print("Enter room Password: ")
                        room_pass = getpass.getpass("")
                        username = self.loginCredentials[0]
                        room_status = self.join_room_chat(room_name, room_pass, username)
                        if room_status == 1:
                            return self.chatroom_menu(0, self.styleAsSuccess("Joined " + room_name + " successfully"))
                        else:
                            return self.chatroom_menu(0, self.styleAsError(room_status + " Please try again"))
                    else:
                        return self.chatroom_menu(0)
                else:
                    return self.chatroom_menu(0, self.styleAsError("Room not found. Please try again."))
            except Exception as e:
                import traceback
                logging.error(f"Error in searching or joining chat room: {traceback.format_exc()}")
                print("Error occurred while handling chat rooms.")

        elif choice == 4: # Go back to main menu
            return self.select_menu(0, self.styleAsInfo(f"Hello {self.loginCredentials[0]}"))
        
    def room_menu(self, room_name, intialChoice = 0,intitalTitle=""):
        os.system('cls')
        intitalTitle = f"Room: {room_name}" if intitalTitle == "" else intitalTitle
        print(intitalTitle + "\n")
        choice = intialChoice

        options = [f"Enter {room_name}", f"Leave {room_name}", Fore.RED +f"Delete {room_name} (You must be the Admin)","Go back to Chatrooms Management"]

        if choice == 0: # Select an option
            questions = [inquirer.List('room_main_choice',message="Please select an option",choices=options,carousel=True)]
            answers = inquirer.prompt(questions)
            choice = options.index(answers['room_main_choice']) + 1
            return self.room_menu(room_name,choice, "") # redirect to the required page

        if choice == 1: # Enter Room
                self.enter_chat_room(room_name, self.loginCredentials[0])

            
        elif choice == 2: # Leave Room
            try:
                status = self.leave_room(room_name, self.loginCredentials[0])
                if status == 1:
                    return self.chatroom_menu(0, self.styleAsSuccess("You left " + room_name + " successfully"))
                elif status == 2:
                    return self.chatroom_menu(0, self.styleAsError(f"{room_name} is deleted because all users leaved"))
                if status == 3:
                    return self.chatroom_menu(0, self.styleAsSuccess(f"You Left {room_name} and it has a new Admin!"))
                else:
                    return self.chatroom_menu(0, self.styleAsError(status + " Please try again later"))
            except Exception as e:
                logging.error(f"Error in Leaving {room_name}: {e}")
                return self.chatroom_menu(0, self.styleAsError(f"Error occurred while fetching {room_name} :(. Please try again."))
        
        elif choice == 3: # Delete Room
            try:
                status=self.Delete_room(room_name,self.loginCredentials[0])
                if status == 1:
                    return self.chatroom_menu(0, self.styleAsSuccess("You Deleted " + room_name + " successfully"))
                else:
                    return self.chatroom_menu(0, self.styleAsError(status + " Please try again later"))
            except Exception as e:
                logging.error(f"Error in deleting {room_name}: {e}")
                return self.chatroom_menu(0, self.styleAsError(f"Error occurred while fetching {room_name} :(. Please try again later."))
            
        elif choice == 4: # Go back to Chatrooms Management
            return self.chatroom_menu(0, self.styleAsInfo("Chatroom management"))

    def one_to_one_chat_menu(self):
        print("Enter OK to accept or REJECT to reject:  ")
        questions = [
            inquirer.Confirm("join_chat", message=f"Do you want to accept the chatting request from {self.peerServer.chattingClientName}?", default=True),
        ]
        answers = inquirer.prompt(questions)
        choice = answers["join_chat"]
        try:
            if choice:
                print(self.styleAsError("Type 'quit' to exit the chat"))
                okMessage = "OK " + self.loginCredentials[0]
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                self.peerServer.connectedPeerSocket.send(okMessage.encode())
                self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort , self.loginCredentials[0], self.peerServer, "OK")
                self.peerClient.start()
                self.peerClient.join()
                return self.select_menu(0, self.styleAsInfo(f"Hello {self.loginCredentials[0]}"))

        # if user rejects the chat request then reject message is sent to the requester side
            else:
                self.peerServer.connectedPeerSocket.send("REJECT".encode())
                self.peerServer.isChatRequested = 0
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")
                return self.select_menu(0, self.styleAsInfo(f"Hello {self.loginCredentials[0]}"))
        except Exception as e:
            logging.error(f"Error in one_to_one_chat_menu: {e}")
            return self.select_menu(0, self.styleAsError("Error occurred while handling chat request. Please try again."))
      
    def cleanup_resources(self):
        try:
            if self.isOnline:
                self.logout(1)
                self.peerServer.isOnline = False
                self.peerServer.tcpServerSocket.close()
                self.peerServer.udpServerSocket.close()
                self.tcpClientSocket.close()
                self.udpClientSocket.close()
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
                print(self.styleAsInfo("You joined " + room_name + " room successfully.") + self.styleAsError(" Type 'exit' to leave the room."))
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

                self.send_message_to_room_users(sender_socket, self.get_user_color(username) + f"{username}" + Fore.RESET +" joined the room", me, room_name)
                
                # Chat loop
                while True:
                    message = input()
                    print('\033[1A' + '\033[K', end='')
                    print("you: " + message)
                    if message.lower() == "exit":
                        globals.room_users = []
                        globals.joined_room_name = ""
                        print("Exiting the room...")
                        break
                    else:
                        formatted_message = self.formatting_message(message)
                        self.send_message_to_room_users(
                            sender_socket, 
                            self.get_user_color(username) + f"{username}: " + Fore.RESET + f"{formatted_message}", 
                            me, 
                            room_name
                        )
                        
                return self.chatroom_menu(0)
        except Exception as e:
            logging.error(f"Error in enter_chat_room: {e}")
            print("An error occurred while entering the chat room.")

    def formatting_message(self, raw_message):
        formatted_message = raw_message

        # **bold**
        formatted_message = re.sub(r'\*\*(.*?)\*\*', lambda match: f'\033[1m{match.group(1)}\033[0m', formatted_message)

        # __italic__
        formatted_message = re.sub(r'__(.*?)__', lambda match: f'\033[3m{match.group(1)}\033[0m', formatted_message)

        # [hyperlink](url)
        formatted_message = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\033]8;;\2\033\\ \1 \033]8;;\033\\', formatted_message)
        
        return formatted_message

    def send_message_to_room_users(self, sender_socket, message, me, room_name):

        if '\033]8;;' in message:
            url = re.search(r'\033]8;;(.*?)\033\\', message).group(1)
            webbrowser.open(url)  # to open 
            #message = message + '( '+ url + ' )'

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

    def get_user_color(self, username):
        # Define a list of colors from Colorama
        colors = [
            Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN
        ]

        # Use the hash of the username to choose a color
        random.seed(hash(username))
        color = random.choice(colors)
        return color


# >> server/db Functions     
    
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
                return 1
            elif response == "join-exist":
                return "Room name exists, please choose another room name."
            else:
                return "Unexpected response from the server."
        except Exception as e:
            logging.error(f"Error in create_new_room: {e}")
            return "An error occurred while creating the chat room."
        
    def Delete_room(self,room_name, username):
        try:
            message="DELETE " + room_name +" "+ username
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()
            logging.info(f"Received from {self.registryName} -> {response}")

            # Handling different responses
            if response == "room-deleted":
                return 1
            elif response == "not-admin":
                return "You are not the Admin of the room"
            else:
                return "Unexpected response from the server."
        except Exception as e:
            logging.error(f"Error in Deleting-room: {e}")
            return "An error occurred while deleting the chat room."

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
                return response[1], response[2:]  # 1: Admin, 2: Users list
            elif response[0] == "search-Room-not-found":
                print(f"{room_name} is not found")
                return None,None
            else:
                print("Unexpected response from the server.")
                return None
        except Exception as e:
            logging.error(f"Error in search_for_room: {e}")
            print("An error occurred while searching for the room.")
            return None,None
        
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
                return 1
            elif response == "Already-in":
                return "You are already in the chat room!"
            elif response == "Wrong-pass":
                return "Incorrect password. Try again."
            else:
                return "Unexpected response from the server."
        except Exception as e:
            logging.error(f"Error in join_room_chat: {e}")
            return "An error occurred while joining the chat room."
       
    def leave_room(self, room_name, username):
        try:
            # Constructing and sending the leave room message
            message = f"Leave {room_name} {username}"
            logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
            self.tcpClientSocket.send(message.encode())

            # Receiving and decoding the response
            response = self.tcpClientSocket.recv(1024).decode()
            logging.info(f"Received from {self.registryName} -> {response}")
            if response=="user-leaved":
                return 1
            elif response=="room-deleted":
                return 2
            elif response=="new-admin":
                return 3

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
                return 1
            elif response == "join-exist":
                return "Username already exists, please choose another username or login."
            else:
                return "Unexpected response from the server."
        except Exception as e:
            logging.error(f"Error in create_new_account: {e}")
            return "An error occurred while creating a new account."

    def delete_account(self,username):
        message = "delAcc " + " " + username
        logging.info(f"Send to {self.registryName}:{self.registryPort} -> {message}")
        self.tcpClientSocket.send(message.encode())

        # Receiving and decoding the response
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info(f"Received from {self.registryName} -> {response}")
        if response == "User-Deleted":
            return 1
        else:
            return 0

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
                return 1
            elif response == "login-account-not-exist":
                return "Account does not exist."
            elif response == "login-online":
                return "Account is already online."
            elif response == "login-wrong-password":
                return "Wrong password."
            else:
                return "Unexpected response from the server."
        except Exception as e:
            logging.error(f"Error in login: {e}")
            return "An error occurred while trying to log in."
   
    # logout function
    def logout(self, option):
        try:
            # a logout message is composed and sent to registry
            # timer is stopped
            if option == 1:
                message = "LOGOUT " + self.loginCredentials[0]
                self.timer.cancel()
            else:
                message = "LOGOUT "
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
                return response[1]
            elif response[0] == "search-user-not-online":
                print(self.styleAsError(f"{username} is not online."))
                return 0
            elif response[0] == "search-user-not-found":
                print(self.styleAsError(f"{username} is not found."))
                return None
            else:
                print(self.styleAsError("Unexpected response from the server."))
                return None
        except Exception as e:
            logging.error(f"Error in search_for_user: {e}")
            print(self.styleAsError("An error occurred while searching for the user."))
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
    
    def CreateNewPeer(self, message):
        del self
        p = peerMain(message=message)
        return 1


# peer is started
main = peerMain()