# Uncomment this to pass the first stage
import socket
import os
from argparse import ArgumentParser
import gzip

FILE_DIR = None

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

def select_valid_encoding(encodings):
    for encoding in encodings:
        if encoding.strip() == 'gzip':
            return encoding.strip()

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

    encoding = headers.get('Accept-Encoding')
    if encoding:
        encoding = select_valid_encoding(encoding.split(","))
    print("encoding:", encoding)

    body = request_data[header_end + 4:]

    print("body:", body)

    return method, path, headers, body, encoding

def generate_response(status = 200, headers = None, body = None):
    if headers is None:
        headers = {}

    if body is None:
        body = b""
    elif headers.get('Content-Encoding') != 'gzip':
        body = body.encode()

    headers_string = "\r\n".join([f"{key}: {value}" for key, value in headers.items()])

    status_ = "200 OK"

    if status == 404:
        status_ = "404 Not Found"
    elif status == 500:
        status_ = "500 Internal Server Error"
    elif status == 201:
        status_ = "201 Created"

    return f"HTTP/1.1 {status_}\r\n{headers_string}\r\n\r\n".encode('utf-8') + body

def process_connection(connection):
    request_data = fetch_request(connection)

    method, path, headers, body, encoding = parse_request(request_data)

    if not method or not path:
        return

    if method == 'GET' and path == '/':
        connection.sendall(generate_response(200))
    elif method == 'GET' and path.startswith('/echo/'):
        response_body = path[6:]
        response_header = {
            'Content-Type': 'text/plain'
        }

        print('decoded response', response_body)
        if encoding == 'gzip':
            response_header['Content-Encoding'] = 'gzip'
            response_body = gzip.compress(response_body.encode('utf-8'))
            
        print('encoded response', response_body)
        response_header['Content-Length'] = len(response_body)

        connection.sendall(generate_response(200, response_header, response_body))
    elif method == 'GET' and path.startswith('/files/'):
        response_body = path[7:]
        file_path = os.path.join(FILE_DIR, response_body)
        
        if os.path.isfile(file_path):
            file = open(file_path, 'r')
            file_content = file.read()
            response_header = {
                'Content-Type': 'application/octet-stream'
            }

            if encoding == 'gzip':
                response_header['Content-Encoding'] = 'gzip'
                file_content = gzip.compress(file_content.encode('utf-8'))

            response_header['Content-Length'] = len(file_content)
            connection.sendall(generate_response(200, response_header, file_content))
        else:
            connection.sendall(generate_response(404))
    elif method == 'POST' and path.startswith('/files/'):
        response_body = path[7:]
        file_path = os.path.join(FILE_DIR, response_body)
        
        file = open(file_path, 'w')
        file.write(body.decode('utf-8'))
        file.close()
        connection.sendall(generate_response(201))
    elif method == 'GET' and path == '/user-agent':
        response_body = headers.get('User-Agent')
        response_header = {
            'Content-Type': 'text/plain'
        }

        if encoding == 'gzip':
            response_header['Content-Encoding'] = 'gzip'
            response_body = gzip.compress(response_body.encode('utf-8'))

        response_header['Content-Length'] = len(response_body)
        connection.sendall(generate_response(200, response_header, response_body))
    else:
        connection.sendall(generate_response(404))

    connection.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    parser = ArgumentParser()
    parser.add_argument("-d", "--directory", dest="directory",
                        help="File Directory", metavar="DIRECTORY")
    args = parser.parse_args()

    if args.directory:
        print(f"File Directory: {args.directory}")
        globals()["FILE_DIR"] = args.directory


    # Uncomment this to pass the first stage
    
    server_socket = socket.create_server(("0.0.0.0", 4221), reuse_port=True)

    while True:
        connection, _ = server_socket.accept() # wait for client
        process_connection(connection)

if __name__ == "__main__":
    main()
