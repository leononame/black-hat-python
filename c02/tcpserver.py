import socket
import threading
import signal
import sys

bind_ip = "0.0.0.0"
bind_port = 9999
# Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# reuse address
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((bind_ip, bind_port))
server.listen(5)

print "[*] Listening on " + bind_ip + ":" + str(bind_port)


# Handle client request
def handle_client(client_socket):
    # Get client data
    req = client_socket.recv(1024)

    print "[*] Received: " + req

    client_socket.send("it works")
    client_socket.close()


while True:
    try:
        client, addr = server.accept()

        print "[*] Accepted connection from: %s:%d" % (addr[0], addr[1])

        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

    except KeyboardInterrupt:
        client.close()
        break

print "[*] Closing server..."
server.close()
