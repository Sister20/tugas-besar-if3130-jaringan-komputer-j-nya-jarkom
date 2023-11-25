from lib.connection import Connection
from lib.tcp_manager import TCPManager
from lib.arg import ServerArg

import logging

if __name__ == "__main__":
    logging.basicConfig(format="[i] [Server] %(message)s", level=logging.INFO)
    args = ServerArg()

    connection = Connection("127.0.0.1", args.port_server)

    tcp_manager = TCPManager(connection=connection)

    tcp_manager.always_listen()
    
    connection.close()