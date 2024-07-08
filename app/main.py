# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    
    server_socket = socket.create_server(("0.0.0.0", 4221), reuse_port=True)
    connection, _ = server_socket.accept() # wait for client

    with connection:
        print("Connection accepted, connection:", connection)
        connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        
        data = connection.recv(1024)
        print('Received', repr(data))

        connection.close()


if __name__ == "__main__":
    main()
