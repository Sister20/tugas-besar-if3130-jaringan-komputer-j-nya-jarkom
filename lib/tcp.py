import random
import logging
import time
from .connection import Connection, MessageInfo
from .segment import Segment
from .constants import FlagEnum, TIMEOUT

from enum import Enum

class TCPStatusEnum(Enum):
    UNINITIALIZED = 0
    WAITING_SYN_ACK = 1
    WAITING_ACK = 2
    WAITING_FIRST_PACKET = 3
    ESTABLISHED = 4

class BaseTCP:
    ip: str # IP and Port of the lawan bicara
    port: int 
    connection: Connection
    closed: bool
    
    status: TCPStatusEnum
    
    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.connection = connection
        self.status = TCPStatusEnum.UNINITIALIZED
        self.closed = False

    def __str__(self):
        return f"{self.ip}:{self.port}"

    def handle_message(self, message: MessageInfo):
        raise NotImplementedError("handle_message is an abstract function that need to be implemented")

class TCPClient(BaseTCP):
    handshake_sequence_number: int = 0

    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        super().__init__(connection, ip, port)

    def connect(self, init=True):
        if init:
            logging.info("Initiating three-way handshake")

        while self.status != TCPStatusEnum.ESTABLISHED:
            try:
                if self.status == TCPStatusEnum.UNINITIALIZED:
                    self.handshake_sequence_number = random.randint(0, 4294967000)

                    self.connection.send(MessageInfo(self.ip, self.port, Segment.syn_segment(self.handshake_sequence_number)))
                    logging.info(f"Sent SYN packet with sequence number {self.handshake_sequence_number}")

                    message = self.connection.receive(TIMEOUT)
                    logging.info(f"Received message during UNINITIALIZED: {message}")

                    self.status = TCPStatusEnum.WAITING_SYN_ACK

                    if message.segment.flag == FlagEnum.SYN_ACK_FLAG:
                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                            logging.info("Sent ACK packet to complete three-way handshake")
                            self.status = TCPStatusEnum.WAITING_FIRST_PACKET
                            break
                        else:
                            logging.info("Invalid ack number. Dropping ...")
                    else:
                        logging.info("Received packet with flag other than SYN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.WAITING_SYN_ACK:
                    message = self.connection.receive(TIMEOUT)
                    logging.info(f"Received message during WAITING_SYN_ACK: {message}")

                    if message.segment.flag == FlagEnum.SYN_ACK_FLAG:
                        if message.segment.ack == self.handshake_sequence_number + 1:
                            self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                            logging.info("Sent ACK packet to complete three-way handshake")
                            self.status = TCPStatusEnum.WAITING_FIRST_PACKET
                            break
                        else:
                            logging.info("Invalid ack number. Dropping ...")
                    else:
                        logging.info("Received packet with flag other than SYN-ACK. Dropping ...")

                elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and not init:
                    self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, self.handshake_sequence_number + 1)))
                    logging.info("Sent ACK packet to complete three-way handshake")
                    break

            except TimeoutError:
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
        elif message.segment.flag == FlagEnum.NO_FLAG:
            logging.info(f"Received data.")

        else:
            logging.info("Received unrelated packet. Dropping ...")
    def close(self):
        TIME_WAIT_DURATION = 2 
        # connection termination
        self.connection.send(MessageInfo(self.ip, self.port, Segment.fin_segment(self.handshake_sequence_number)))
        self.status = TCPStatusEnum.FIN_WAIT_1

        while self.status != TCPStatusEnum.CLOSED:
            try:
                if self.status == TCPStatusEnum.FIN_WAIT_1:
                    message = self.connection.receive(TIMEOUT)
                    logging.info(f"Received message during FIN_WAIT_1: {message}")

                    if message.segment.flag == FlagEnum.ACK_FLAG:
                        # Server acknowledges FIN, transition to FIN_WAIT_2
                        self.status = TCPStatusEnum.FIN_WAIT_2
                        logging.info("Connection in FIN_WAIT_2 state")
                    else:
                        logging.info(f"Received unexpected packet during FIN_WAIT_1. Dropping ...")

                elif self.status == TCPStatusEnum.FIN_WAIT_2:
                    message = self.connection.receive(TIMEOUT)
                    logging.info(f"Received message during FIN_WAIT_2: {message}")

                    if message.segment.flag == FlagEnum.FIN_FLAG:
                        # Server sends FIN, acknowledge and transition to TIME_WAIT
                        self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                        self.status = TCPStatusEnum.TIME_WAIT
                        logging.info("Connection in TIME_WAIT state")
                        break
                    else:
                        logging.info(f"Received unexpected packet during FIN_WAIT_2. Dropping ...")

                elif self.status == TCPStatusEnum.TIME_WAIT:
                    # Sleep for TIME_WAIT duration, transition to CLOSED
                    time.sleep(TIME_WAIT_DURATION)
                    self.status = TCPStatusEnum.CLOSED
                    logging.info("Connection closed successfully")

            except TimeoutError:
                logging.info(f"Timeout error during closing phase ... will retry")
                pass


class TCPServer(BaseTCP):
    ver_seqnum: int = 0

    def __init__(self, connection: Connection, ip: str, port: int) -> None:
        super().__init__(connection, ip, port)

    # todo handle tcp close connection for server here
    # notes: close method must receive message params. do not call receive here since the message could be from other client
    # when parallel option is enabled
    def close(self):
        # connection termination
        self.connection.send(MessageInfo(self.ip, self.port, Segment.fin_segment(self.ver_seqnum)))
        self.status = TCPStatusEnum.CLOSE_WAIT

        while self.status != TCPStatusEnum.CLOSED:
            try:
                if self.status == TCPStatusEnum.CLOSE_WAIT:
                    message = self.connection.receive(TIMEOUT)
                    logging.info(f"Received message during CLOSE_WAIT: {message}")

                    if message.segment.flag == FlagEnum.FIN_FLAG:
                        # Client sends FIN, acknowledge and transition to LAST_ACK
                        self.connection.send(MessageInfo(self.ip, self.port, Segment.ack_segment(0, message.segment.sequence_number + 1)))
                        self.status = TCPStatusEnum.LAST_ACK
                        logging.info("Connection in LAST_ACK state")
                    else:
                        logging.info(f"Received unexpected packet during CLOSE_WAIT. Dropping ...")

                elif self.status == TCPStatusEnum.LAST_ACK:
                    message = self.connection.receive(TIMEOUT)
                    logging.info(f"Received message during LAST_ACK: {message}")

                    if message.segment.flag == FlagEnum.ACK_FLAG:
                        # Client acknowledges FIN, transition to CLOSED
                        self.status = TCPStatusEnum.CLOSED
                        logging.info("Connection closed successfully")
                        break
                    else:
                        logging.info(f"Received unexpected packet during LAST_ACK. Dropping ...")

            except TimeoutError:
                logging.info(f"Timeout error during closing phase ... will retry")
                pass

        