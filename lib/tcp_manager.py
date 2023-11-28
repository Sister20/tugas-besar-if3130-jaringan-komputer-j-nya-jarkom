import random
from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum, TIMEOUT
from .tcp_pending import TCPPending
from .handler import FileSender
from .arg import ServerArg
from socket import timeout as socket_timeout

from typing import List, Dict, Tuple

import logging
import time
import threading

class TCPManager:
    ip: str
    port: int
    tcp_connections: Dict[Tuple[str, int], FileSender]
    pending_connections: TCPPending = TCPPending()
    connection: Connection
    args: ServerArg

    def __init__(self, args: ServerArg, connection: Connection):
        self.tcp_connections = {}
        self.connection = connection
        self.connection.listen()
        self.args = args

    def listen_for_connection(self):
        logging.info("Begin listening for connections. Use Ctrl+C to stop new incoming connection")
        accept_new = True

        try:
            while accept_new or self.pending_connections.tcp_client.__len__() != 0:
                try:
                    message = self.connection.receive(TIMEOUT)
                    self._handle_connection_message(message, accept_new)
                except socket_timeout:
                    # do not exit on timeout
                    pass
        except KeyboardInterrupt as e:
            if not accept_new:
                raise e
            else:
                logging.info("Keyboard interrupt detected. Will stop accepting when every connection is established")
                accept_new = False

    def print_all_connections(self):
        i = 1

        for _, v in self.tcp_connections.items():
            print(f"{i}. {v}")
            i += 1

    def sequential_handle(self):
        for _, connection in self.tcp_connections.items():
            connection.begin_transfer()

            while not connection.closed:
                try:
                    message = self.connection.receive(TIMEOUT)

                    if message.ip != connection.ip or message.port != connection.port:
                        logging.info("Wrong packet destination. Dropping ...")
                        continue
                        
                    connection.handle_message(message)
                except socket_timeout:
                    # do not exit on timeout
                    pass

    def parallel_handle(self):
        for connection in self.tcp_connections.values():
            connection.begin_transfer()

        all_completed = False
            
        while not all_completed:
            try:
                message = self.connection.receive(TIMEOUT)
                
                if (message.ip, message.port) in self.tcp_connections:
                    tcp_server = self.tcp_connections[(message.ip, message.port)]

                    tcp_server.handle_message(message)

                    if tcp_server.closed:
                        self.tcp_connections.pop((message.ip, message.port))

                        if len(self.tcp_connections) == 0:
                            all_completed = True
                else:
                    logging.info("Detected packet for unknown connection. Dropping ...")
            except socket_timeout:
                # do not exit on timeout
                pass

    def _handle_connection_message(self, message: MessageInfo, accept_new: bool):
        if (message.ip, message.port) in self.tcp_connections:
            logging.info("Packet for already established connection. Dropping ...")
            return
            
        if self.pending_connections.is_pending(message.ip, message.port):
            self._handle_three_way_handshake(message)
        else:
            if accept_new:
                
                self._handle_three_way_handshake(message)
            else:
                logging.info("Server not accepting new connection. Dropping ...")

    def _resend_syn_ack(self, ip: str, port: int, client_sequence_number:int, server_sequence_number: int):
        time.sleep(TIMEOUT)
        
        while self.pending_connections.is_pending(ip, port):

            current_sequence_number = self.pending_connections.get_init_sequence_number(ip, port)

            if current_sequence_number != server_sequence_number:
                break

            self.connection.send(
                MessageInfo(
                    ip,
                    port,
                    Segment.syn_ack_segment(sequence_number=server_sequence_number, ack=client_sequence_number + 1),
                )
            )

            time.sleep(TIMEOUT)

    def _handle_three_way_handshake(self, message: MessageInfo) -> None:

        segment = message.segment
        if segment.flag == FlagEnum.SYN_FLAG:
            logging.info(f"[Client {message.ip}:{message.port}] Initiating three way handshake...")

            server_sequence_number = random.randint(0, 50)
            self.pending_connections.add(message.ip, message.port, server_sequence_number)
            client_sequence_number = message.segment.sequence_number


            logging.info(f"[Client {message.ip}:{message.port}] SYN received with sequence number {client_sequence_number}")

            self.connection.send(
                MessageInfo(
                    message.ip,
                    message.port,
                    Segment.syn_ack_segment(sequence_number=server_sequence_number, ack=client_sequence_number + 1),
                )
            )

            thread = threading.Thread(target=self. _resend_syn_ack, args=(message.ip, message.port, client_sequence_number, server_sequence_number))
            thread.start()

            return
        elif segment.flag == FlagEnum.ACK_FLAG:
            if segment.ack == self.pending_connections.get_init_sequence_number(message.ip, message.port) + 1:
                logging.info(f"[Client {message.ip}:{message.port}] valid ACK received")
                self._establish_connection(message.ip, message.port)
            else:
                logging.info(f"[Client {message.ip}:{message.port}] invalid acknowledgemet number={segment.ack} received")
                return
        else:
            logging.info(f"[Server {message.ip}:{message.port}] getting invalid flag={segment.flag}")
            return
            
    def _establish_connection(self, ip: str, port: int) -> None:
        self.tcp_connections[(ip, port)] = FileSender(self.args.file_path, self.connection, ip, port, self.pending_connections.get_init_sequence_number(ip, port) + 1)
        self.pending_connections.remove(ip, port)
        logging.info(f"[Client {ip}:{port}] Connection established")

        return
