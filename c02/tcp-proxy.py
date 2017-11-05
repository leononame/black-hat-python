#!/usr/bin/python3
import sys
import socket
import threading
import textwrap


# Hexdump of a string
def hexdump(src):
    length = 16
    res = []
    for i in range(0, len(src), length):
        s = src[i:i+length]
        # get hex vals
        vals = ['{:02x}'.format(x) for x in s]
        # convert into hexstring
        hexstring = ' '.join(vals)
        text = ''.join(chr(x) if 0x20 <= x < 0x7F else '.' for x in s)
        res.append('0x{:04x} {:48} {}'.format(i, hexstring, text))
    print('\n'.join(res))


# Receive data from a socket
def receive(sock):
    buff = b""
    sock.settimeout(2)

    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            buff += data
    # Ignore timeout exception
    except:
        pass

    return buff


# Can be used to modify rhost requests
def request_handler(buff):
    return buff


# can be used to modify lhost responses
def response_handler(buff):
    return buff


# If a client connects to the proxy server,
# the request is forwarded through this function in a new thread
def run_proxy_connection(client, rhost, rport, recfirst):
    # remote server
    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote.connect((rhost, rport))
    except:
        remote.close()
        print("[!!] Error connecting to remote host {}:{}".format(rhost, rport))
        return 1

    # If data is first received
    if recfirst:
        rbuff = receive(remote)
        print('[<==] Received {} bytes from remote'.format(len(rbuff)))
        hexdump(rbuff)
        # Modify data
        rbuff = response_handler(rbuff)
        if len(rbuff):
            print("[<==] Forwarding data to localhost")
            client.send(rbuff)

    # Proxy loop
    # Read from local, send to remote
    # Read from remote, send to local
    while True:
        lbuff = receive(client)
        if len(lbuff):
            print("[==>] Received {} bytes from localhost".format(len(lbuff)))
            hexdump(lbuff)
            lbuff = request_handler(lbuff)
            print("[==>] Forwarding data to remote")
            remote.send(lbuff)

        rbuff = receive(remote)
        if len(rbuff):
            print('[<==] Received {} bytes from remote'.format(len(rbuff)))
            hexdump(rbuff)
            rbuff = response_handler(rbuff)
            print("[<==] Forwarding data to localhost")
            client.send(rbuff)
        # Close sockets on exit
        if not len(rbuff) and not len(lbuff):
            remote.close()
            client.close()
            print("[*] No more data. Closing connections.")
            break
    return 0


# Server function
# Opens a TCP socket and accepts input in infinite loop
def run_server(lhost, lport, rhost, rport, recfirst):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set socket opts to reuse address
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Listen
    try:
        s.bind((lhost, lport))
        s.listen(5)
    except:
        print("[!] Error listening on {}:{}".format(lhost, lport))
        print("[!] Expcetion: " + sys.exc_info()[0])
        sys.exit(1)

    print("[*] Listening on {}:{}".format(lhost, lport))
    # start server loop
    while True:
        try:
            c, addr = s.accept()

            print("[==>] Incoming connection from {}:{}".format(*addr))
            # new thread to run run_proxy_connection()
            t = threading.Thread(target=run_proxy_connection,
                                 args=(c, rhost, rport, recfirst))
            # set as deamon thread and run
            t.setDaemon(True)
            t.start()

        except (KeyboardInterrupt, EOFError):
            s.close()
            print("\n[*] Exit signal received. Shutting down...")
            break

    return 0


# Initial starting point
# Reads config from cli and starts server
def main():
    # Check cli args
    if len(sys.argv[1:]) not in (4, 5):
        print("Usage: tcp-proxy.py lhost lport rhost rport [rec first]")
        print("Parameters:")

        prefix = "    Receive First:  "
        wrapper = textwrap.TextWrapper(initial_indent=prefix, width=80, subsequent_indent=' ' * len(prefix))
        message = "A value of 1 indicates that the proxy will first receive data from the remote host"
        print(wrapper.fill(message))
        sys.exit(1)

    # Parse cli args
    lhost = sys.argv[1]
    lport = int(sys.argv[2])
    rhost = sys.argv[3]
    rport = int(sys.argv[4])
    recfirst = False
    if len(sys.argv[1:]) == 5 and sys.argv[5] == "1":
        recfirst = True
        print("[*] Starting proxy in receive first mode...")
    else:
        print("[*] Starting proxy in standard mode...")

    # Run server
    run_server(lhost, lport, rhost, rport, recfirst)

    return 0


# Run main
if __name__ == "__main__":
    main()
