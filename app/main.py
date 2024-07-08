# Uncomment this to pass the first stage
import socket

def fetch_request(connection):
    buffer_length = 1024
    data = bytes()
    header_end = b'\r\n\r\n'

    while True:
        chunk = connection.recv(buffer_length)
        if not chunk:
            break
        data += chunk
        if header_end in chunk:
            break

    return data

def parse_request(request_data):
    header_end = request_data.find(b'\r\n\r\n')

    if header_end == -1:
        return None

    header_data = request_data[:header_end]

    lines = header_data.splitlines()

    method, path, _ = lines[0].decode('utf-8').split(' ')

    print("method and path:", method, path)

    headers = lines[1:]

    headers = dict(line.decode('utf-8').split(': ') for line in headers)

    print("headers:", headers) 

    body = request_data[header_end + 4:]

    print("body:", body)

    return method, path, headers, body

def generate_response(status = 200, headers = None, body = None):
    if headers is None:
        headers = {}

    if body is None:
        body = ""

    headers_string = "\r\n".join([f"{key}: {value}" for key, value in headers.items()])

    status_ = "200 OK"

    if status == 404:
        status_ = "404 Not Found"
    elif status == 500:
        status_ = "500 Internal Server Error"

    return f"HTTP/1.1 {status_}\r\n{headers_string}\r\n\r\n{body}".encode('utf-8')

def process_connection(connection):
    request_data = fetch_request(connection)

    method, path, headers, _ = parse_request(request_data)

    if not method or not path:
        return

    if method == 'GET' and path == '/':
        connection.sendall(generate_response(200))
    elif method == 'GET' and path.startswith('/echo/'):
        response_body = path[6:]
        response_header = {
            'Content-Type': 'text/plain',
            'Content-Length': len(response_body)
        }
        connection.sendall(generate_response(200, response_header, response_body))
    elif method == 'GET' and path == '/user-agent':
        response_body = headers.get('User-Agent')
        response_header = {
            'Content-Type': 'text/plain',
            'Content-Length': len(response_body)
        }
        connection.sendall(generate_response(200, response_header, response_body))
    else:
        connection.sendall(generate_response(404))

    connection.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    
    server_socket = socket.create_server(("0.0.0.0", 4221), reuse_port=True)
    connection, _ = server_socket.accept() # wait for client

    process_connection(connection)

if __name__ == "__main__":
    main()
