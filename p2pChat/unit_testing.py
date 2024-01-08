import unittest
from unittest.mock import patch, MagicMock
from peer_main import peerMain
from peer_server import PeerServer
from socket import socket, AF_INET, SOCK_DGRAM

class TestPeerApp(unittest.TestCase):
    def setUp(self):
        # Mock the input function to simulate user input during tests
        self.mock_input = patch('builtins.input').start()

        self.peer_main = peerMain()

        # Mock socket creation to avoid port conflicts during tests
        self.mock_socket = MagicMock(spec=socket)
        self.mock_socket.getsockname.return_value = ('', 0)

        self.mock_socket_udp = MagicMock(spec=socket, family=AF_INET, type=SOCK_DGRAM)
        self.mock_socket_udp.getsockname.return_value = ('', 0)

        self.patcher_socket = patch('socket.socket', side_effect=[self.mock_socket, self.mock_socket_udp])
        self.patcher_socket.start()

    def tearDown(self):
        self.mock_input.stop()
        self.patcher_socket.stop()

    def test_create_new_account(self):
        username = "test_user"
        password = "1234"
        result = self.peer_main.create_new_account(username, password)
        self.assertEqual(result, 1)

    def test_create_new_room(self):
        room_name = "testing_room"
        password = "1234"
        username = "test_user"
        result = self.peer_main.create_new_room(room_name, password, username)
        self.assertEqual(result, 1)

    def test_enter_chat_room(self):
        # Set up the expected user inputs during the test
        self.mock_input.side_effect = ['testing_room', 'test_user', 'exit']

        room_name = "testing_room"
        username = "test_user"
        result = self.peer_main.enter_chat_room(room_name, username)
        self.assertIsNone(result)

    def test_formatting_message(self):
        test_message = "test_message"
        self.mock_input.return_value = test_message

        result = self.peer_main.formatting_message(test_message)
        self.assertEqual(result, test_message)


if __name__ == '__main__':
    unittest.main()
