import paramiko
from datetime import datetime
import json
import os
from dotenv import load_dotenv

def main():
    # Informações de conexão SSH
    hostname = ''
    username = ''
    password = ''
    port = 384

    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=port, username=username, password=password)
    _stdin, _stdout, _stderr = client.exec_command("df")
    print(_stdout.read().decode())
    client.close()

if __name__ == "__main__":
    main()