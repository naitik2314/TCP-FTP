import socket #To send the message accross internet
import hashlib #To Check MD5

#Function to connect to the server
def connect_to_server(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    return client_socket

#Functio to send a command to the server
def send_command(client_socket, command):
    client_socket.send(command_encode())

#Function to receive data from the server
def receive_data(client_socket):
    data = b""
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        data += chunk
    return data.decode()

#Function to verify MD5 checksum of the downloaded file
def verify_md5(file_path, received_md5):
    md5_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
    return md5_hash == received_md5

#Main Function
def main():
    server_ip = "127.0.0.1" 
    server_port = 12345

    try:
        client_socket = connect_to_server(server_ip, server_port)
        while True:
            print("Available Commands:")
            print("1. LIST - list files")
            print("2. GET <file_name> - Download file")
            print("3. CLOSE - Close connection")

            user_input = input("Enter command: ").strip()
            send_command(client_socket=client_socket, user_input=user_input)

            if user_input == "CLOSE":
                break
            elif user_input == "LIST":
                data = receive_data(client_socket)
                print(data)
            elif user_input.startswith("GET "):
                _, file_name, start_byte, end_byte = user_input.split()
                start_byte = int(start_byte)
                end_byte = int(end_byte)
                file_data = receive_data(client_socket)
                
                if file_data.startswith("<REP GET BEGIN>"):
                    file_data = file_data[len("<REP GET BEGIN>\n"):]
                    
                    if end_byte == -1:
                        file_path = f"downloaded_{file_name}"
                    else:
                        file_path = f"downloaded_{file_name}_{start_byte}_{end_byte}"
                    
                    with open(file_path, "wb") as file:
                        file.write(file_data.encode())
                    
                    received_md5 = receive_data(client_socket)
                    
                    if verify_md5(file_path, received_md5):
                        print(f"File {file_name} downloaded successfully.")
                    else:
                        print(f"File {file_name} download failed (checksum mismatch).")
                else:
                    print(file_data)
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
