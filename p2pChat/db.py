from pymongo import MongoClient

class DB:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat']

    def is_account_exist(self, username):
        return self.db.accounts.count_documents({'username': username}) > 0
    
# >>> Register user
    def register(self, username, password):
        account = {
            "username": username,
            "ChatRooms":[],
            "password": password
        }
        self.db.accounts.insert_one(account)

# >>> Delete user 
    def Delete_user(self, username):
        # Check if the user exists
        user = self.db.accounts.find_one({"username": username})
        
        # Remove the user from all ChatRooms
        chatrooms_list = user.get("ChatRooms", [])
        if chatrooms_list:
            for Chatroom in chatrooms_list:
                self.remove_user_from_room(Chatroom,username)

        # Delete the user from the accounts collection
        self.db.accounts.delete_one({"username": username})

        print(f"User '{username}' has been successfully deleted.")
        return 1


    def get_password(self, username):
        user_data = self.db.accounts.find_one({"username": username})
        return user_data["password"] if user_data else None

    def is_account_online(self, username):
        return self.db.online_peers.count_documents({"username": username}) > 0

    def user_login(self, username, ip, portTCP, portUDP):
        online_peer = {
            "username": username,
            "ip": ip,
            "portTCP": portTCP,
            "portUDP": portUDP
        }
        self.db.online_peers.insert_one(online_peer)

    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    def get_peer_ip_port(self, username):
        online_peer = self.db.online_peers.find_one({"username": username})
        if online_peer and "ip" in online_peer and "portTCP" in online_peer and "portUDP" in online_peer:
            return online_peer["ip"], online_peer["portTCP"], online_peer["portUDP"]
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

    def Delete_room(self, room_name, Admin="leaved"):

        # >>  Check if the Admin exists and has the authority to delete the room
        admin_check = self.db.Chatrooms.find_one({"Admin": Admin, "room_name": room_name})

        if Admin=="leaved":  # Empty Chatroom
            self.db.Chatrooms.delete_one({"room_name": room_name}) 

        elif admin_check:
            # Remove the room from the admin's ChatRooms list
            self.db.accounts.update_one(
                {"username": Admin},
                {"$pull": {"ChatRooms": room_name}}
            )

            # Delete the room from the Chatrooms collection
            self.db.Chatrooms.delete_one({"room_name": room_name})
            
            # Remove all references to the room in other users' ChatRooms lists
            self.db.accounts.update_many(
                {"ChatRooms": room_name},
                {"$pull": {"ChatRooms": room_name}}
            )

            print(f"Room '{room_name}' has been successfully deleted.")
            return 1
        else:
            print(f"user '{Admin}' does not have the authority to delete room '{room_name}'")
            return 0


    def does_room_exist(self, room_name):
        return self.db.Chatrooms.count_documents({'room_name': room_name}) > 0
    
    def get_chat_rooms(self, username=None):
        if username:
            # Return specific user's room names
            user_account = self.db.accounts.find_one({"username": username})
            if user_account:
                chat_rooms = user_account.get("ChatRooms", [])
                if not chat_rooms:
                    return None
                else:
                    return chat_rooms
            else:
                return None
        else:
            # Return all room names
            chatrooms = self.db.Chatrooms.find()
            room_names = [chat_room["room_name"] for chat_room in chatrooms]
            return room_names

    
    def get_room_details(self, room_name):
        room = self.db.Chatrooms.find_one({"room_name": room_name})
        if room and "users" in room and "Admin" in room:
            return room["Admin"], room["users"] 
        else:
            print(f"Error: Required fields not found for {room_name}")
            return None
    
    def get_room_members(self, room_name):
        room = self.db.Chatrooms.find_one({"room_name": room_name})
        if room and "users" in room and "Admin" in room:
            online_users_in_room = list(self.db.online_peers.find({"username": {"$in": room["users"]}}))
            return {"admin":room["Admin"],"users": online_users_in_room}
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
    
    def remove_user_from_room(self, room_name, user_to_remove):
        newAdminFlag=0
        chat_room = self.db.Chatrooms.find_one({"room_name": room_name})
        chat_room["users"].remove(user_to_remove)
        # Update the user's account to remove the room from ChatRooms
        self.db.accounts.update_one(
            {"username": user_to_remove},
            {"$pull": {"ChatRooms": room_name}}
        )

        if user_to_remove == chat_room["Admin"]:
            # Get the first user in the room to be promoted as the new admin
            if len(chat_room["users"]) > 0:
                new_admin = chat_room["users"][0]  
                # Promote the first user to be the new admin
                self.db.Chatrooms.update_one(
                    {"room_name": room_name},
                    {"$set": {"Admin": new_admin}}
                )
                newAdminFlag=1
            else: 
                self.Delete_room(room_name) # the room is empty!
                return "room-deleted"    

        

        # Update the database with the modified chat room
        self.db.Chatrooms.update_one(
            {"room_name": room_name},
            {"$set": {"users": chat_room["users"]}}
        )

        if newAdminFlag:
            return "new-admin"
        else:
            return "user-leaved"





        
    