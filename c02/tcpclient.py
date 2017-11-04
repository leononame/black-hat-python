import socket

host = "www.google.com"
port = 80
# Create client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect
client.connect((host, port))
# Send data
client.send("GET / HTTP/1.1\nHost: google.com\n\n")
response = client.recv(4096)
print response
