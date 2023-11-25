from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum, TIMEOUT
from .tcp import TCPServer
from .tcp_pending import TCPPending
from socket import timeout as socket_timeout

from typing import List

import logging
import time
import threading

class TCPManager:
    ip: str
    port: int
    tcp_connections: List[TCPServer] = []
    pending_connections: TCPPending = TCPPending()
    connection: Connection

    def __init__(self, connection: Connection):
        self.connection = connection
        self.connection.listen()

    def always_listen(self):
        while True:
            try:
                message = self.connection.receive(TIMEOUT)
                self.handle_message(message)
            except socket_timeout:
                # do not exit on timeout
                pass

    def handle_message(self, message: MessageInfo):
        for tcp_server in self.tcp_connections:
            if tcp_server.ip == message.ip and tcp_server.port == message.port:
                tcp_server.handle_message(message)
                return
            
        if self.pending_connections.is_pending(message.ip, message.port):
            self.handle_three_way_handshake(message)
        else:
            self.pending_connections.add(message.ip, message.port, 0)
            self.handle_three_way_handshake(message)

    def _resend_syn_ack(self, ip: str, port: int, client_sequence_number:int, server_sequence_number: int):
        time.sleep(TIMEOUT)
        
        while self.pending_connections.is_pending(ip, port):
            self.connection.send(
                MessageInfo(
                    ip,
                    port,
                    Segment.syn_ack_segment(sequence_number=server_sequence_number, ack=client_sequence_number + 1),
                )
            )

            time.sleep(TIMEOUT)

    def handle_three_way_handshake(self, message: MessageInfo) -> None:

        segment = message.segment
        if segment.flag == FlagEnum.SYN_FLAG:
            logging.info(f"[Client {message.ip}:{message.port}] Initiating three way handshake...")

            server_sequence_number = self.pending_connections.get_init_sequence_number(message.ip, message.port)
            client_sequence_number = segment.sequence_number

            logging.info(f"[Client {message.ip}:{message.port}] SYN received with sequence number {client_sequence_number}")

            self.connection.send(
                MessageInfo(
                    message.ip,
                    message.port,
                    Segment.syn_ack_segment(sequence_number=server_sequence_number, ack=client_sequence_number + 1),
                )
            )

            thread = threading.Thread(target=self._resend_syn_ack, args=(message.ip, message.port, client_sequence_number, server_sequence_number))
            thread.start()

            return
        elif segment.flag == FlagEnum.ACK_FLAG:
            if segment.ack == self.pending_connections.get_init_sequence_number(message.ip, message.port) + 1:
                logging.info(f"[Client {message.ip}:{message.port}] valid ACK received")
                self.establish_connection(message.ip, message.port)
            else:
                logging.info(f"[Client {message.ip}:{message.port}] invalid acknowledgemet number={segment.ack} received")
                return
        else:
            logging.info(f"[Server {message.ip}:{message.port}] getting invalid flag={segment.flag}")
            return
            
    def establish_connection(self, ip: str, port: int) -> None:
        self.tcp_connections.append(TCPServer(self.connection, ip, port))
        self.pending_connections.remove(ip, port)
        logging.info(f"[Client {ip}:{port}] Connection established")
        
        self.tcp_connections[-1].begin_file_transfer()
        return
