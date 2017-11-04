#!/usr/bin/python

import sys
import socket
import getopt
import threading
import subprocess

# Globals
listen = False
cmd = False
upld = False
upld_dest = ""
target = ""
exe = ""
port = 0


# Print cli usage
def print_usage():
    print "netcat improved (ncm)\n"
    print "Usage: netcat.py -t target -p port"
    print "-l --listen                  - listen on [host]:[port] for incoming connections"
    print "-e --execute=file            - execute the given file upon receiving a connection"
    print "-c --command                 - initialize a command shell"
    print "-u --upload=destination      - upon receiving connection upload a file and write to [destination]"
    print
    print


def client_send():
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        c.connect((target, port))

        while True:
            buff = raw_input("")
            while len(buff) <= 0:
                buff = raw_input("")
            c.send(buff)

            recv_len = 1
            resp = ""

            while recv_len:
                data = c.recv(4096)
                recv_len = len(data)
                resp += data
                if recv_len == 0:
                    print "Connection closed by server..."
                    sys.exit(0)
                if recv_len < 4096:
                    break

            print resp,
    except KeyboardInterrupt:
        c.close()
        print "[*] Exit..."
    except SystemExit:
        sys.exit(0)
    except:
        c.close()
        print "[*] Exception: ", sys.exc_info()[0]
        sys.exit(1)


def main():
    global listen, port, exe, cmd, upld_dest, target
    if not len(sys.argv[1:]):
        print_usage()
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "le:cu:t:p:h",
                                  ["listen", "execute", "command", "upload", "target", "port", "help"])
    except getopt.GetoptError as err:
        print str(err)
        print_usage()
        sys.exit(1)

    for o,a in opts:
        if o in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            exe = a
        elif o in ("-c", "--command"):
            cmd = True
        elif o in ("-u", "--upload"):
            upld_dest = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            print "Unknown option " + o
            sys.exit(1)

    # Connect
    if not listen and len(target) and port > 0:
        # Send data
        client_send()
    # Listen
    elif listen:
        #server_run()
        sys.exit(0)


main()
