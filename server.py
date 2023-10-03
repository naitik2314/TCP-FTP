import socket
import os
import hashlib
import time

# Read configuration parameters from a configuration file
def read_config():
    config = {} #We initalized it as a Dictionary
    with open("server_config.txt", "r") as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config

# Function to send the file list to the client
def send_file_list(conn, shared_dir):
    file_list = os.listdir(shared_dir)
    response = f"<REP LIST {len(file_list)}>\n"
    for idx, file_name in enumerate(file_list, start=1):
        file_path = os.path.join(shared_dir, file_name)
        file_size = os.path.getsize(file_path)
        md5_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
        response += f"<{idx} {file_name} {file_size} {md5_hash}>\n"
    response += "<REP LIST END>\n"
    conn.send(response.encode())

# Function to send a portion of a file to the client
def send_file_chunk(conn, file_path, start_byte, end_byte):
    with open(file_path, "rb") as file:
        file.seek(start_byte)
        data = file.read(end_byte - start_byte)
        conn.send(data)

# Function to handle client requests
def handle_client(conn, addr, shared_dir):
    print(f"Accepted connection from {addr[0]}:{addr[1]}")
    conn.settimeout(120)  # Timeout if idle for 2 minutes
    try:
        while True:
            command = conn.recv(1024).decode().strip()
            if not command:
                break
            if command == "<REQ LIST>":
                send_file_list(conn, shared_dir)
            elif command.startswith("<GET "):
                _, file_name, start_byte, end_byte = command.split()
                start_byte = int(start_byte)
                end_byte = int(end_byte)
                file_path = os.path.join(shared_dir, file_name)
                send_file_chunk(conn, file_path, start_byte, end_byte)
            elif command == "<CLOSE>":
                break
    except socket.timeout:
        print(f"Connection from {addr[0]}:{addr[1]} timed out.")
    finally:
        print(f"Closed connection from {addr[0]}:{addr[1]}")
        conn.close()

# Main function to start the server
def main():
    config = read_config()
    host = config["server_ip"]
    port = int(config["server_port"])
    shared_dir = config["shared_directory"]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Listen for incoming connections

    print(f"Server listening on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        handle_client(conn, addr, shared_dir)

if __name__ == "__main__":
    main()

