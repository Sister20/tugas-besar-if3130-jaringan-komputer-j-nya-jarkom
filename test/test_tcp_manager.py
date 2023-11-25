from lib.connection import Connection
from lib.tcp_manager import TCPManager

def main():
    connection = Connection("127.0.0.1", 8080)
    tcp_manager = TCPManager(connection=connection)
    tcp_manager.always_listen()
    connection.close()


if __name__ == '__main__':
    main()