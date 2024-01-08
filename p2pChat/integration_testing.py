import unittest
from unittest.mock import patch, MagicMock
from peer_main import peerMain
from peer_server import PeerServer
from socket import socket, AF_INET, SOCK_DGRAM

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_input = patch('builtins.input').start()

        self.peer_main = peerMain()

        self.mock_socket = MagicMock(spec=socket)
        self.mock_socket.getsockname.return_value = ('', 0)

        self.mock_socket_udp = MagicMock(spec=socket, family=AF_INET, type=SOCK_DGRAM)
        self.mock_socket_udp.getsockname.return_value = ('', 0)

        self.patcher_socket = patch('socket.socket', side_effect=[self.mock_socket, self.mock_socket_udp])
        self.patcher_socket.start()

    def tearDown(self):
        self.mock_input.stop()
        self.patcher_socket.stop()

    def test_create_account_and_join_room(self):
        # Set up the expected user inputs during the test
        self.mock_input.side_effect = ['test_user', '1234', 'testing_room', 'exit']

        username = "test_user"
        password = "1234"
        room_name = "testing_room"

        self.peer_main.create_new_account(username, password)
        sock = socket()
        sock.bind(('', 0))
        peerServerPort = sock.getsockname()[1]
        
        sockUDP = socket(AF_INET, SOCK_DGRAM) 
        sockUDP.bind(('', 0))
        peerServerUDPPort = sockUDP.getsockname()[1]
        self.peer_main.login(username, password, peerServerPort, peerServerUDPPort)
        self.peer_main.create_new_room(room_name, password, username)


    def test_join_create_leave(self):
        # Set up the expected user inputs during the test
        self.mock_input.side_effect = ['test_user', '1234', 'testing_room', 'exit']
        #mockdata
        username = "test_user"
        password = "1234"
        room_name = "testing_room"
        leave_result=1
        self.peer_main.create_new_account(username, password)
        # Create a new chat room and then attempt to join it from another client
        self.mock_input.side_effect = [2, room_name, password]  
        self.peer_main.chatroom_menu()
        create_result = self.peer_main.create_new_room(room_name, password, username)

        # Join the created chat room
        self.mock_input.side_effect = [3, room_name, 'y', password]  # Choosing the "Search/Join Chat room" option and then joining a room
        self.peer_main.chatroom_menu()
        join_result = self.peer_main.join_room_chat(room_name, password, username)

        # Leave the chat room
        self.mock_input.side_effect = [3, room_name, leave_result]  
        self.peer_main.chatroom_menu()
        leave_result = self.peer_main.leave_room(room_name, username)    

    def test_create_login_deleteaccount(self):
        username = "test_user"
        password = "1234"
        delete_result=1
        self.peer_main.create_new_account(username, password)
        # Set up the expected user inputs during the test
        self.mock_input.side_effect = [username, password, username, password, 1]
        self.peer_main.select_menu(self, Choice = 5, Title = "Chose to delete account ")
        delete_result = self.peer_main.delete_account(username)
        self.assertEqual(delete_result, 1)

if __name__ == '__main__':
    unittest.main()
