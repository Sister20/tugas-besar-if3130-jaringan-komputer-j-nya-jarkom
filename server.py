from lib.connection import Connection
from lib.tcp_manager import TCPManager
from lib.arg import ServerArg

import logging
import sys
import socket
import traceback

def main():
    logging.basicConfig(format="[i] [Server] %(message)s", level=logging.INFO)
    args = ServerArg()

    connection = Connection("", args.port_server)

    tcp_manager = TCPManager(args=args, connection=connection)

    try:
        tcp_manager.listen_for_connection()

        tcp_manager.print_all_connections()

        result = input("Use parallel transfer? [y/n] ")

        if result == "y":
            tcp_manager.parallel_handle()
        else:
            tcp_manager.sequential_handle()        
        
    except KeyboardInterrupt as e:
        logging.info("Received KeyboardInterrupt. Closing connection.")
    except Exception as e:
        logging.info("Exception occured, closing connection.")
        logging.info(traceback.format_exc())
        print(e)
        
if __name__ == "__main__":
    main()
