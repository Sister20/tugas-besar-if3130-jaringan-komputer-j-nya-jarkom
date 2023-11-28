# client.py
from lib.connection import Connection
from lib.handler import FileReceiver
from lib.arg import ClientArg
from lib.constants import TIMEOUT
from socket import timeout as socket_timeout

import logging
import sys
import socket

def main():
    logging.basicConfig(format="[i] [Client] %(message)s", level=logging.INFO)

    args = ClientArg()

    file_path = args.file_path  

    connection = Connection("", args.port_client)

    tcp = FileReceiver(connection, args.host_server, args.port_server, file_path)
    tcp.connect()

    while not tcp.closed:
        try:
            message = connection.receive()
            tcp.handle_message(message)
        except socket_timeout:
            continue


    connection.close()

if __name__ == "__main__":
    main()
