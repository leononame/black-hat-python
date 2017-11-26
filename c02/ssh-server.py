#!/usr/bin/python3

import socket
import paramiko
import threading
import sys

# Load key
# Very good programming
host_key = paramiko.RSAKey(filename='../keys/ssh_host_rsa_key')

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'root') and (password == 'toor'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print('[+] Listening for connection... ')
    client, addr = sock.accept()

except Exception as e:
    print('[-] Listen failed: ' + str(e))
    sys.exit(1)

print('[+] Incoming connection!')

try:
    ssh_session = paramiko.Transport(client)
    ssh_session.add_server_key(host_key)
    server = Server()
    try:
        ssh_session.start_server(server=server)
    except paramiko.SSHException as x:
        print('[-] SSH negotiation failed')
        sys.exit(1)

    chan = ssh_session.accept(20)
    print('[+] Authenticated!')
    print(chan.recv(1024))
    chan.send('Welcome, root!')
    
    while True:
        try:
            command = input('=== Enter command; ').strip('\n')
            if command != 'exit':
                chan.send(command)
                sys.stdout.buffer.write(chan.recv(1024))
            else:
                chan.send('exit')
                print('[+] Exiting...')
                ssh_session.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            ssh_session.close()
            raise Exception('exit')

except Exception as e:
    print('[-] Caught exception: ' + str(e))
    try:
        ssh_session.close()
    except:
        pass
    sys.exit(1)

