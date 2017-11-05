#!/usr/bin/python
import socket

host = "127.0.0.1"
port = 9999
# Create client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect
client.connect((host, port))
# Send data
client.send("GET / HTTP/1.1\nHost: localhost\n\n")
response = client.recv(4096)
print response
