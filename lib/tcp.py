import random
import logging
import threading
import time
from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum, TIMEOUT
from socket import timeout as socket_timeout
from enum import Enum

class TCPStatusEnum(Enum):
    UNINITIALIZED = 0
    WAITING_SYN_ACK = 1
    WAITING_ACK = 2
    WAITING_FIRST_PACKET = 3
    ESTABLISHED = 4
    CLOSED = 5
    ACTIVE_CLOSE = 6
    WAITING_FIN_ACK = 7
    CLOSE_TIME_WAIT = 8
    WAITING_LAST_ACK = 9

class BaseTCP:
    ip: str # IP and Port of the lawan bicara
    port: int 
    connection: Connection
    status: TCPStatusEnum
    
    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.connection = connection
        self.status = TCPStatusEnum.UNINITIALIZED
        
    @property
    def closed(self) -> bool:
        return self.status == TCPStatusEnum.CLOSED

    def __str__(self):
        return f"{self.ip}:{self.port}"

    def handle_message(self, message: MessageInfo):
        raise NotImplementedError("handle_message is an abstract function that need to be implemented")

class TCPClient(BaseTCP):
    handshake_sequence_number: int = 0
    server_sequence_number: int = 0

    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        super().__init__(connection, ip, port)
        self.handshake_sequence_number = random.randint(0, 50)

    def connect(self, init=True):
        if init:
            logging.info("Initiating three-way handshake")

        while self.status != TCPStatusEnum.ESTABLISHED:
            try:
                if self.status == TCPStatusEnum.UNINITIALIZED:

                    self.connection.send(MessageInfo(self.ip, self.port, Segment.syn_segment(self.handshake_sequence_number)))

                    message = self.connection.receive(TIMEOUT)

                    self.status = TCPStatusEnum.WAITING_SYN_ACK

                    if message.segment.flag == FlagEnum.SYN_ACK_FLAG:
                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.server_sequence_number = message.segment.sequence_number + 1
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, self.server_sequence_number)))
                            self.status = TCPStatusEnum.WAITING_FIRST_PACKET
                            break
                        else:
                            logging.info("Invalid ack number. Dropping ...")
                    else:
                        logging.info("Received packet with flag other than SYN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.WAITING_SYN_ACK:
                    message = self.connection.receive(TIMEOUT)

                    if message.segment.flag == FlagEnum.SYN_ACK_FLAG:
                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.server_sequence_number = message.segment.sequence_number + 1
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, self.server_sequence_number)))
                            self.status = TCPStatusEnum.WAITING_FIRST_PACKET
                            break
                        else:
                            logging.info("Invalid ack number. Dropping ...")
                    else:
                        logging.info("Received packet with flag other than SYN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and not init:
                    self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, self.server_sequence_number)))
                    break

            except socket_timeout:
                logging.info(f"Timeout error during phase {self.status} ... will retry")
                pass

    def handle_message(self, message: MessageInfo):
        # first packet received
        if self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.NO_FLAG:
            logging.info(f"TCP Connection established")
            self.status = TCPStatusEnum.ESTABLISHED
        elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.SYN_ACK_FLAG:
            if message.segment.ack == self.handshake_sequence_number + 1:
                self.connect(False)
            else:
                logging.info(f"Invalid ack number. Dropping ...")
        else:
            logging.info("Received unrelated packet. Dropping ...")
    
    def close(self):
        # connection termination
        self.status = TCPStatusEnum.ACTIVE_CLOSE

        while not self.closed:
            try:
                if self.status == TCPStatusEnum.ACTIVE_CLOSE:
                    self.connection.send(MessageInfo(self.ip, self.port, Segment.fin_segment(self.handshake_sequence_number)))

                    message = self.connection.receive(TIMEOUT)

                    self.status = TCPStatusEnum.WAITING_FIN_ACK

                    if message.segment.flag == FlagEnum.FIN_ACK_FLAG:
                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.server_sequence_number = message.segment.sequence_number + 1
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, self.server_sequence_number)))
                            self.status = TCPStatusEnum.CLOSE_TIME_WAIT
                        else:
                            logging.info("Invalid ack number. Dropping ...")
                    else:
                        logging.info("Received packet with flag other than FIN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.WAITING_FIN_ACK:
                    message = self.connection.receive(TIMEOUT)

                    if message.segment.flag == FlagEnum.FIN_ACK_FLAG:
                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.server_sequence_number = message.segment.sequence_number + 1
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, self.server_sequence_number)))
                            self.status = TCPStatusEnum.CLOSE_TIME_WAIT
                        else:
                            logging.info("Invalid ack number. Dropping ...")
                    else:
                        logging.info("Received packet with flag other than FIN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.CLOSE_TIME_WAIT:
                    logging.info("Waiting 10 seconds before closing connection ...")
                    try:
                        message = self.connection.receive(10)

                        if message.segment.flag == FlagEnum.FIN_ACK_FLAG:
                            if message.segment.ack == self.handshake_sequence_number + 1:
                                self.server_sequence_number = message.segment.sequence_number + 1
                                self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, self.server_sequence_number)))
                                self.status = TCPStatusEnum.CLOSE_TIME_WAIT
                            else:
                                logging.info("Invalid ack number. Dropping ...")
                        else:
                            logging.info("Received packet with flag other than FIN-ACK. Dropping ...")
                            
                    except socket_timeout:
                        logging.info("Connection closed")
                        self.status = TCPStatusEnum.CLOSED
            except socket_timeout:
                pass


class TCPServer(BaseTCP):
    server_seqnum: int

    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        super().__init__(connection, ip, port)
        self.server_seqnum = 0
        self.status = TCPStatusEnum.ESTABLISHED

    def handle_message(self, message: MessageInfo):
        # first packet received
        if message.segment.flag == FlagEnum.FIN_FLAG or self.status in [TCPStatusEnum.CLOSED, TCPStatusEnum.ACTIVE_CLOSE, TCPStatusEnum.CLOSE_TIME_WAIT, TCPStatusEnum.WAITING_LAST_ACK]:
            self._handle_close(message)
        else:
            logging.info("Received unrelated packet. Dropping ...")

    def _handle_close(self, message: MessageInfo):
        while self.status != TCPStatusEnum.CLOSED:
            try:
                if message.segment.flag == FlagEnum.FIN_FLAG and self.status == TCPStatusEnum.ESTABLISHED:
                    logging.info(f"[Client {message.ip}:{message.port}] Initiating graceful disconnection...")
                    self.status = TCPStatusEnum.WAITING_LAST_ACK

                    server_sequence_number = self.server_seqnum
                    client_sequence_number = message.segment.sequence_number

                    self.connection.send(
                        MessageInfo(
                            message.ip,
                            message.port,
                            Segment.fin_ack_segment(sequence_number=server_sequence_number, ack=client_sequence_number + 1),
                    ))

                    thread = threading.Thread(target=self. _resend_fin_ack, args=(message.ip, message.port, client_sequence_number, server_sequence_number))
                    thread.start()
                elif message.segment.flag == FlagEnum.ACK_FLAG and self.status == TCPStatusEnum.WAITING_LAST_ACK:
                    if message.segment.ack == self.server_seqnum + 1:
                        logging.info(f"[Client {message.ip}:{message.port}] valid LAST ACK received. Connection closed")
                        self.status = TCPStatusEnum.CLOSED
                    else:
                        logging.info(f"[Client {message.ip}:{message.port}] invalid acknowledgemet number={message.segment.ack} received")
                        return
                else:
                    logging.info(f"[Server {message.ip}:{message.port}] getting invalid flag={message.segment.flag}")
                    return

            except socket_timeout:
                pass

    def _resend_fin_ack(self, ip: str, port: int, client_sequence_number:int, server_sequence_number: int):
        time.sleep(TIMEOUT)
        
        while self.status == TCPStatusEnum.WAITING_LAST_ACK and not self.closed:
            self.connection.send(
                MessageInfo(
                    ip,
                    port,
                    Segment.fin_ack_segment(sequence_number=server_sequence_number, ack=client_sequence_number + 1),
                )
            )

            time.sleep(TIMEOUT)
