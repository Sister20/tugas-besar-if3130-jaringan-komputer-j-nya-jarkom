from lib.tcp import TCPClient, TCPServer
from lib.connection import Connection

def main():
    connection = Connection("127.0.0.1", 8080)
    tcp_client = TCPClient(connection, "127.0.0.1", 8080)
    tcp_client.connect()
    connection.close()




if __name__ == '__main__':
    main()