import argparse
import socket


class ClientArg:
    port_client: int
    port_server: int
    host_server: str
    file_path: str  

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description="Client for handling file transfer connection from server"
        )

        parser.add_argument(
            "client_port",
            metavar="[client port]",
            type=int,
            help="Client port to start the service"
        )

        parser.add_argument(
            "broadcast_port",
            metavar="[broadcast port]",
            type=int,
            help="broadcast port for server address"
        )

        parser.add_argument(
            "file_path",  
            metavar="[path folder output]",
            type=str,
            help="location of output path"
        )

        parser.add_argument(
            "host",
            metavar="[broadcast host]",
            type=str,
            help="broadcast host for server address"
        )

        args = parser.parse_args()

        self.port_client = getattr(args, "client_port")
        self.port_server = getattr(args, "broadcast_port")
        self.file_path = getattr(args, "file_path")
        self.host_server = getattr(args, "host")

class ServerArg:
    port_server: int
    file_path: str

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description="Server for sending file transfer to client"
        )

        parser.add_argument(
            "server_port",
            metavar="[server port]",
            type=int,
            help="Server port to start the service"
        )

        parser.add_argument(
            "file_path",
            metavar="[file input path]",
            type=str,
            help="location of file input path"
        )

        args = parser.parse_args()

        self.port_server = getattr(args, "server_port")
        self.file_path = getattr(args, "file_path")

    