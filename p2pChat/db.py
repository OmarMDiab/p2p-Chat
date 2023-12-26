from pymongo import MongoClient

class DB:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat']

    def is_account_exist(self, username):
        return self.db.accounts.count_documents({'username': username}) > 0

    def register(self, username, password):
        account = {
            "username": username,
            "ChatRooms":[],
            "password": password
        }
        self.db.accounts.insert_one(account)

    def get_password(self, username):
        user_data = self.db.accounts.find_one({"username": username})
        return user_data["password"] if user_data else None

    def is_account_online(self, username):
        return self.db.online_peers.count_documents({"username": username}) > 0

    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        self.db.online_peers.insert_one(online_peer)

    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    def get_peer_ip_port(self, username):
        online_peer = self.db.online_peers.find_one({"username": username})
        if online_peer and "ip" in online_peer and "port" in online_peer:
            return online_peer["ip"], online_peer["port"]
        else:
            print(f"Error: Required fields not found for {username}")
            return None
    
    def get_online_usernames(self):
        online_peers = self.db.online_peers.find()
        usernames = []

        for online_peer in online_peers:
            if "username" in online_peer:
                usernames.append(online_peer["username"])
            else:
                print(f"Error: Username not found for online peer {online_peer}")

        return usernames

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> chatting rooms: -
    
    def Register_room(self, room_name, password,Admin):
        Chat_room = {
            "room_name": room_name,
            "Admin":Admin,
            "users": [Admin],         # Initialize an list for users with admin as first user
            "password": password     
        }
        self.db.accounts.update_one(
                {"username": Admin},
                {"$push": {"ChatRooms": room_name}}
        )
        self.db.Chatrooms.insert_one(Chat_room)

    def does_room_exist(self, room_name):
        return self.db.Chatrooms.count_documents({'room_name': room_name}) > 0
    
    def get_chat_rooms(self):
        chatrooms = self.db.Chatrooms.find()
        room_names = []

        for Chat_room in chatrooms:
            if "room_name" in Chat_room:
                room_names.append(Chat_room["room_name"])
            else:
                print(f"Error: Username not found for online peer {Chat_room}")

        return room_names
    
    def get_room_details(self, room_name):
        room = self.db.Chatrooms.find_one({"room_name": room_name})
        if room and "users" in room and "Admin" in room:
            return room["Admin"], room["users"] 
        else:
            print(f"Error: Required fields not found for {room_name}")
            return None
        
    
    def Join_room(self,room_name ,username):
        
       # Update the users list in the chat room to add the new username
            self.db.Chatrooms.update_one(
                {"room_name": room_name},
                {"$push": {"users": username}}
            )
            self.db.accounts.update_one(
                {"username": username},
                {"$push": {"ChatRooms": room_name}}
            )

    def get_room_pass(self, room_name):
        room_data = self.db.Chatrooms.find_one({"room_name": room_name})
        return room_data["password"] if room_data else None
    
    def is_user_in_chat_room(self, username, room_name):
        return self.db.Chatrooms.count_documents({'room_name': room_name, 'users': username}) > 0


        
    