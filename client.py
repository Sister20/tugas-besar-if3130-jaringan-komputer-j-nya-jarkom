from lib.connection import Connection
from lib.tcp import TCPClient
from lib.arg import ClientArg

import logging

if __name__ == "__main__":
    logging.basicConfig(format="[i] [Client] %(message)s", level=logging.INFO)
    
    args = ClientArg()

    connection = Connection("127.0.0.1", args.port_client)
    
    tcp = TCPClient(connection, args.host_server, args.port_server)
    tcp.connect()

    connection.close()