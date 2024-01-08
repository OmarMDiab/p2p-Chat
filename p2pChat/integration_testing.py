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

    def test_create_login_deleteaccount(self):
        username = "test_user"
        password = "1234"
        delete_result=1
        self.peer_main.create_new_account(username, password)
        # Set up the expected user inputs during the test
        self.mock_input.side_effect = [username, password, username, password, 1]
        delete_result = self.peer_main.delete_account(username)
        self.assertEqual(delete_result, 1)

if __name__ == '__main__':
    unittest.main()
