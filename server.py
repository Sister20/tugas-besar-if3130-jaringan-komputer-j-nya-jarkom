from lib.connection import Connection
from lib.tcp_manager import TCPManager
from lib.arg import ServerArg

import logging
import sys
import socket

def main():
    logging.basicConfig(format="[i] [Server] %(message)s", level=logging.INFO)
    args = ServerArg()

    connection = Connection("127.0.0.1", args.port_server)

    tcp_manager = TCPManager(connection=connection)

    try:
        tcp_manager.always_listen()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt. Closing connection.")
    finally:
        try:
            logging.info("Socket status before closing: %s", connection.socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR))
        except OSError:
            logging.info("Socket is already closed.")
        connection.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
