from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum, TIMEOUT
from .tcp import TCPServer
from .tcp_pending import TCPPending
from .handler import FileSender
from socket import timeout as socket_timeout

from typing import List

import logging
import time
import threading

class TCPManager:
    ip: str
    port: int
    tcp_connections: List[FileSender] = []
    pending_connections: TCPPending = TCPPending()
    connection: Connection

    def __init__(self, connection: Connection):
        self.connection = connection
        self.connection.listen()

    def listen_for_connection(self):
        logging.info("Begin listening for connections. Use Ctrl+C to stop new incoming connection")
        accept_new = True

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
                
                logging.info("Keyboard interrupt detected. Will stop accepting when every connection is established")
                accept_new = False

    def print_all_connections(self):
        for i in range(len(self.tcp_connections)):
            print(f"{i+1}. {self.tcp_connections[i]}")

    def sequential_handle(self):
        for connection in self.tcp_connections:
            while not connection.closed:
                message = self.connection.receive(TIMEOUT)

                if message.ip != connection.ip or message.port != connection.port:
                    logging.info("Wrong packet destination. Dropping ...")
                    continue
                    
                connection.handle_message(message)

    def parallel_handle(self):
        while True:
            try:
                message = self.connection.receive(TIMEOUT)
                for tcp_server in self.tcp_connections:
                    if tcp_server.ip == message.ip and tcp_server.port == message.port:
                        # bad implementation because spawn many thread at once but hey it works?
                        thread = threading.Thread(target=tcp_server.handle_message, args=(message))
                        thread.start()
                        return
                
                logging.info("Detected packet for unknown connection. Dropping ...")
            except socket_timeout:
                # do not exit on timeout
                pass

    def _handle_connection_message(self, message: MessageInfo, accept_new: bool):
        for tcp_server in self.tcp_connections:
            if tcp_server.ip == message.ip and tcp_server.port == message.port:
                logging.info("Packet for already established connection. Dropping ...")
                return
            
        if self.pending_connections.is_pending(message.ip, message.port):
            self._handle_three_way_handshake(message)
        else:
            if accept_new:
                self.pending_connections.add(message.ip, message.port, 0)
                self._handle_three_way_handshake(message)
            else:
                logging.info("Server not accepting new connection. Dropping ...")

    def _resend_syn_ack(self, ip: str, port: int, client_sequence_number:int, server_sequence_number: int):
        time.sleep(TIMEOUT)
        
        
        while self.pending_connections.is_pending(ip, port):
            current_sequence_number = self.pending_connections.get_init_sequence_number(ip, port)

            if current_sequence_number != client_sequence_number:
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
                self._establish_connection(message.ip, message.port)
            else:
                logging.info(f"[Client {message.ip}:{message.port}] invalid acknowledgemet number={segment.ack} received")
                return
        else:
            logging.info(f"[Server {message.ip}:{message.port}] getting invalid flag={segment.flag}")
            return
            
    def _establish_connection(self, ip: str, port: int) -> None:
        self.tcp_connections.append(FileSender(self.connection, ip, port))
        self.pending_connections.remove(ip, port)
        logging.info(f"[Client {ip}:{port}] Connection established")

        return
