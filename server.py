import socket
import threading
import datetime
# helllo



# ---------- SERVER SETUP ----------
HOST = '127.0.0.1'   # Localhost (use LAN IP to chat across devices)
PORT = 55555         # Any free port

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []     # List to store connected clients
nicknames = []   # List to store nicknames of connected users

def save_chat_log(message):
    """Save messages with timestamps to chat_log.txt"""
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("chat_log.txt", "a", encoding = "utf-8") as f:
        f.write(f"[{time}] : {message}\n")


# ---------- BROADCAST FUNCTION ----------
def broadcast(message, sender=None):
     # Save every broadcasted message
    try:
        save_chat_log(message.decode('utf-8'))
    except:
        pass  # in case message is not text (rare)
    # Send message to all clients, remove any that are disconnected
    disconnected_clients = []
    for client in clients:
        try:
            client.send(message)
        except:
            disconnected_clients.append(client)

    # Remove any disconnected clients safely (after the loop)
    for client in disconnected_clients:
        remove_client(client, broadcast_left=False)



# ---------- HANDLE INDIVIDUAL CLIENT ----------
def handle_client(client):
    """Receive messages from a client and broadcast to others."""
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            # Log message
            with open("chat_log.txt", "a") as log:
                log.write(message.decode('utf-8') + '\n')
            broadcast(message)
        except:
            remove_client(client)
            break


# ---------- REMOVE CLIENT ----------
def remove_client(client, broadcast_left=True):
    if client in clients:
        index = clients.index(client)
        nickname = nicknames[index]
        clients.remove(client)
        nicknames.remove(nickname)
        client.close()
        leave_msg = f"{nickname} left the chat."
        print(leave_msg)
        save_chat_log(leave_msg)

        if broadcast_left:
            broadcast(f"{leave_msg}".encode('utf-8'))
        


# ---------- ACCEPT NEW CONNECTIONS ----------
def receive_connections():
    """Main loop to accept and start threads for each client."""
    print("Server is running and listening...")
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Ask for nickname
        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode('utf-8'))
        client.send("Connected to the server!".encode('utf-8'))

        # Start a new thread for this client
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


# ---------- START SERVER ----------
if __name__ == "__main__":
    receive_connections()
