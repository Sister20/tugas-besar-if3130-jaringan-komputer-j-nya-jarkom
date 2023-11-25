from lib.connection import Connection
from lib.tcp import TCPClient
from lib.arg import ClientArg
from lib.constants import TIMEOUT
from socket import timeout as socket_timeout

import logging

if __name__ == "__main__":
    logging.basicConfig(format="[i] [Client] %(message)s", level=logging.INFO)
    
    args = ClientArg()

    connection = Connection("127.0.0.1", args.port_client)
    
    tcp = TCPClient(connection, args.host_server, args.port_server)
    tcp.connect()

    while True:
        try:
            message = connection.receive()
            tcp.handle_message(message)
        except socket_timeout:
            pass

    connection.close()