import logging
import threading
import time
import random
import string
from peer_main import peerMain
import os
from socket import *

os.environ['PYTHONIOENCODING'] = 'utf-8'

total_time_to_join = 0
total_time_to_enter = 0

def random_username(length=8):
    """ Generate a random username """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class TestThread(threading.Thread):
    def __init__(self, user_id):
        self.user_id = user_id
        threading.Thread.__init__(self)
        new_logger = self.setup_logger()
        self.peer = peerMain()
        self.logger = new_logger

    def setup_logger(self):
        """Set up a logger for each thread."""
        logger = logging.getLogger(f"user_{self.user_id}")
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f"logs/user_{self.user_id}_output.txt")
        logger.addHandler(file_handler)
        return logger

    def run(self):
        global total_time_to_join  # Declare as global
        global total_time_to_enter # Declare as global
        username = random_username()
        password = "testpassword"  # Using a fixed password for simplicity

        # Create a new user and login
        self.peer.create_new_account(username, password)
        # Get New Port
        sock = socket()
        sock.bind(('', 0))
        peerServerPort = sock.getsockname()[1]
        
        sockUDP = socket(AF_INET, SOCK_DGRAM)
        sockUDP.bind(('', 0))
        peerServerUDPPort = sockUDP.getsockname()[1]
        
        self.peer.login(username, password, peerServerPort, peerServerUDPPort)
        
        # Use logger to log messages
        self.logger.info(f"My name is {username}")
        
        # Go to chat room management and join a room
        start_time = time.time()
        self.peer.join_room_chat("performance_testing", "123", username)
        end_time = time.time()
        self.logger.info(f"Time to join room: {end_time - start_time} seconds")
        total_time_to_join += end_time - start_time
        start_time = time.time()
        self.peer.enter_chat_room("performance_testing", username)
        end_time = time.time()
        self.logger.info(f"Time to enter room: {end_time - start_time} seconds")
        total_time_to_enter += end_time - start_time
        
def main():
    num_threads = 1000
    
    # Create and start threads
    threads = [TestThread(user_id=i) for i in range(num_threads)]
    for thread in threads:
        thread.start()
        time.sleep(.2)

    time.sleep(2)  # Wait for all threads to join the room

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
        
    print("Average time to join room:", total_time_to_join / num_threads)
    print("Average time to enter room:", total_time_to_enter / num_threads)
        

if __name__ == "__main__":
    main()
