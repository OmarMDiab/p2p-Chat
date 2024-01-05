# P2P Chatting Application

## Description
The P2P Chatting Application is a sophisticated, Python-based messaging system designed for decentralized, peer-to-peer communication. It employs a unique architecture combining a centralized registry server with decentralized peer servers. The registry plays a key role in authenticating users and maintaining a list of active users, facilitating peer discovery. Each user operates a peer server, enabling direct and encrypted message exchanges with others, ensuring privacy and security. This blend of centralized and decentralized components provides a robust, scalable platform for real-time messaging, exemplifying advanced concepts in network programming and application design.

## Installation
**1. Clone the Repository**
```bash
git clone https://github.com/OmarMDiab/p2p-Chat.git
cd p2pChat
```

**2. Install Dependencies**:
- Ensure you have Python installed on your system. The application is tested on Python 3.8.
- Install `MongoDB Compass` and ensure it is running as the application uses it for data storage.
- Install required Python packages:
  ```
  pip install pymongo colorama inquirer
  ```

**3. Configure the Application**:
- Set up and configure MongoDB if not already done. Ensure the database connection details in `db.py` are correctly set.
- Review `config.py` to adjust any application settings, like port numbers.

## Usage Instructions

To effectively use the P2P Chatting Application, follow these steps:

**1. Starting the Registry Server**:
```
python registry.py
```
This initiates the central server responsible for user management and peer discovery.

**2. Running the Client Application**:
```
python peer_main.py
```
Launches the user interface for the chat application.

**3. Navigating the Application**:
- Use commands like `register`, `login`, `chat`, and `logout` for various operations.
- The application provides prompts and instructions for each command.

**4. Development and Testing**:
- For developers, `run_peers.py` can be used to simulate 4 simultaneous peers for testing.

## How It Works
- **Registry Server**: The core of the system, handling user authentication and maintaining a list of online peers. It acts as a central index for peer discovery, allowing users to find and connect with each other.
- **Peer Server**: Each user runs a peer server instance on their machine. This server listens for incoming connections and handles direct message exchanges with other peers. It ensures decentralized, real-time communication.
- **Database (MongoDB)**: Used for securely storing user credentials and managing account information. It supports the authentication process and maintains data integrity.
- **Client Application**: The interface through which users interact with the system. It connects to the registry to fetch the list of active peers and handles user inputs for messaging and other chat functionalities.
![Architecture Diagram](https://github.com/OmarMDiab/p2p-Chat/blob/main/Architecture.png?raw=true)


## Features
- **User Registration and Authentication**: Secure process for creating new user accounts and logging in. The registry server validates credentials, ensuring secure access.
- **Real-Time Peer-to-Peer Messaging**: Users can directly communicate with others in real-time, establishing private chat connections.
- **One-to-One Chat Functionality**: Engage in private conversations.
- **Optimized TCP/UDP Usage**: Efficient, reliable communication.
- **Performance Testing**: Validated scalability and responsiveness.
- **Enhanced User Interface**: Improved navigation and visual presentation.
- **Dynamic Peer List Retrieval**: The application provides an updated list of online peers, allowing users to choose whom they want to chat with.
- **Encrypted Communication**: Messages are encrypted to ensure privacy and security in conversations.
- **Multi-Threaded Server**: Each peer server uses multi-threading to handle multiple incoming connections efficiently.
- **Command-Line Interface**: Offers a user-friendly command-line interface for easy navigation and operation of the chat functions.


## File Descriptions

Each file in the P2P Chatting Application serves a distinct purpose:

- `db.py`: Manages database operations for user account management and authentication, interfacing with MongoDB.

- `registry.py`: The central server script, responsible for handling user registrations, logins, and maintaining the list of active peers.

- `peer_server.py`: Runs the server side of a peer, handling incoming peer connections and messages, using multi-threading for efficient communication.

- `peer_main.py`: The client-side script, providing the user interface for chat functionalities, including commands for registration, login, and messaging.

- `config.py`: Contains configuration settings for the application, such as maximum user limits, to ensure scalability and performance optimization.

- `run_peers.py`: A utility script used in development to simulate multiple peer instances, aiding in comprehensive testing of the application's functionalities.

- `globals.py`: Manages global variables that needs to be accessible within multiple files.

- `performance_testing`: A script for performance testing, it simulates `X` number of running threads and creates new accounts for them then join a room named `performance_testing` then it prints the average time taken for this `X` value.



## Authors
- [Mohamed Abdelmaksoud](https://github.com/helmy162)
- [Nada Wagdy](https://github.com/nadaWagdy)
- [Nour Ayman](https://github.com/NourAbouElMakarem)
- [Omar Diab](https://github.com/OmarMDiab)
