import socket
import threading
import datetime
import sys

# ---------- CLIENT SETUP ----------
HOST = '127.0.0.1'   # Same as server IP
PORT = 55555         # Same port as server

nickname = input("Enter your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

stop_thread = False


# ---------- LOG MESSAGE TO FILE ----------
def log_message(message):
    """Append chat messages to a personal log file with timestamp."""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(f"chat_log_{nickname}.txt", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")


# ---------- RECEIVE MESSAGES ----------
def receive():
    global stop_thread
    while True:
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                # Ignore messages you sent yourself
                if not message.startswith(f"{nickname}:"):
                    print(message)
                    log_message(message)
        except:
            print("You have been disconnected from the server.")
            client.close()
            break



# ---------- SEND MESSAGES ----------
def write():
    while True:
        try:
            message = input("")
            if message.lower() == "exit":
                client.send(f"{nickname} left the chat.".encode('utf-8'))
                client.close()
                print("You have left the chat.")
                break
            client.send(f"{nickname}: {message}".encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            try:
                client.send(f"{nickname} left the chat.".encode('utf-8'))
                client.close()
            except:
                pass #avoid errors if connection is already closed
                print("\nYou have left the chat.")
                break



# ---------- START THREADS ----------
if __name__ == "__main__":
    try:
        receive_thread = threading.Thread(target=receive, daemon=True)
        write_thread = threading.Thread(target=write, daemon=True)

        receive_thread.start()
        write_thread.start()

        # Wait for write thread to finish (user exit)
        write_thread.join()

    except KeyboardInterrupt:
        try:
            client.close()
        except:
            pass
        print("\nClient closed by user (Ctrl + C).")
