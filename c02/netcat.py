#!/usr/bin/python

import sys
import socket
import getopt
import threading
import subprocess
import time

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
            # try catch server data first
            try:
                c.settimeout(0.5)
                recv_len = 1
                resp = ""
                while recv_len:
                    data = c.recv(4096)
                    recv_len = len(data)
                    resp += data
                    if recv_len < 4096:
                        break
                if len(resp):
                    print resp,
            # timeout
            except:
                print

            buff = sys.stdin.read()

            c.send(buff + "\n")
            print buff
            c.settimeout(2)
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
    # Catch ^c, etc.
    except (KeyboardInterrupt, EOFError):
        c.close()
        print "[*] Exit..."
        sys.exit(0)
    # Catch SystemExit to not show any error
    except SystemExit:
        c.close()
        sys.exit(0)
    except:
        c.close()
        print "[*] Unexpected error: ", sys.exc_info()[0]
        sys.exit(1)


def server_run():
    global target

    # If no target is specified, listen on all ifs
    if not len(target):
        target = "0.0.0.0"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse address
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((target, port))
    s.listen(5)
    while True:
        try:
            c, addr = s.accept()

            handler = threading.Thread(target=server_handle, args=(c,))
            # make handler a daemon to stop all threading
            handler.setDaemon(True)
            handler.start()

        # Catch ^c, etc.
        except (KeyboardInterrupt, EOFError):
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            print "[*] Exit..."
            exit(0)
        # Catch SystemExit to not show any error
        except SystemExit:
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            sys.exit(0)
        except:
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            print "[*] Unexpected error: ", sys.exc_info()[0]
            sys.exit(1)


# Run a command
def run_cmd(cmd):
    # trim
    cmd = cmd.rstrip()
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\n"

    return output


# Handle a client request
def server_handle(client):
    global upld, upld_dest, exe, cmd

    # If file upload
    if len(upld_dest):
        # file buffer
        fbuff = ""
        # read data into buffer
        while True:
            d = client.recv(1024)
            if not d:
                break
            else:
                fbuff += d
        # write file and send status
        try:
            fd = open(upld_dest, "wb")
            fd.write(fbuff)
            fd.close()
            # ack
            client.send("Success")
        except:
            client.send("Error")
    # command exec
    if len(exe):
        output = run_cmd(exe)
        client.send(output)

    # ssh
    if cmd:
        while True:
            # send "shell"
            client.send("root@localhost:/#")
            # read cmd
            cmd_buff = ""
            while "\n" not in cmd_buff:
                cmd_buff += client.recv(1024)
            # send response
            client.send(run_cmd(cmd_buff))

    client.close()


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
        server_run()


main()
