#!/usr/bin/python
import socket

host = "www.google.com"
port = 80
# Create client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Send data, suppose this worked
client.sendto("GET / HTTP/1.1\nHost: google.com\n\n", (host, port))

data, addr = client.recvfrom(4096)
print data
print addr
