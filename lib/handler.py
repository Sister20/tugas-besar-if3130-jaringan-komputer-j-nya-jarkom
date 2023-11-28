from mimetypes import init
from .connection import MessageInfo, Connection
from .segment import FlagEnum
from .segment import Segment
from .tcp import TCPClient, TCPStatusEnum, TCPServer
from .segment_sender import SenderBuffer
import logging
from .metadata import Metadata
from os import path
from .file import FileBuilder

class FileReceiver(TCPClient):
    file_handle: FileBuilder

    def __init__(self, connection: Connection, ip: str, port: int, file_path: str) -> None:
        super().__init__(connection, ip, port)
        self.file_path = file_path
        self.is_metadata_received = False
        self.is_file_received = False

    def handle_message(self, message: MessageInfo):
        # initial three-way handshake
        if self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.SYN_ACK_FLAG:
            super().handle_message(message)
            return

        # data transfer
        elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.NO_FLAG:
            super().handle_message(message)
            self.handle_data(message.segment)

        elif self.status == TCPStatusEnum.ESTABLISHED and message.segment.flag == FlagEnum.NO_FLAG:
            self.handle_data(message.segment)

    def handle_data(self, segment: Segment):
        if self.is_file_received:
            logging.info("File already received")
            return
        
        if segment.sequence_number == self.server_sequence_number:
            if not self.is_metadata_received:
                self._handle_metadata(segment)
                self.is_metadata_received = True
                return
            
            self.file_handle.write(segment.data)

            self.server_sequence_number += 1

            # send ACK for the received segment
            ack_segment = Segment.ack_segment(0, segment.sequence_number + 1)
            self.connection.send(MessageInfo(self.ip, self.port, ack_segment))

            if self.file_handle.bytes_written >= self.file_size_bytes:
                self.is_file_received = True
                self.close()

        elif segment.sequence_number < self.server_sequence_number:
            ack_segment = Segment.ack_segment(0, self.server_sequence_number)
            self.connection.send(MessageInfo(self.ip, self.port, ack_segment))
        else:
            logging.info(f"Ignoring out-of-order with sequence number {segment.sequence_number}")

    def _handle_metadata(self, segment: Segment):
        (filename, extension, file_size_bytes) = Metadata.get_metadata(segment.data)
        self.file_size_bytes = file_size_bytes
        self.server_sequence_number += 1

        self.file_path = path.join(self.file_path, filename + extension)
        self.file_handle = FileBuilder(self.file_path, file_size_bytes)

        # send ACK for the received segment
        ack_segment = Segment.ack_segment(0, segment.sequence_number + 1)
        self.connection.send(MessageInfo(self.ip, self.port, ack_segment))
        
class FileSender(TCPServer):
    sender_buffer: SenderBuffer
    receiver_ack_number: int

    def __init__(self, filePath: str, connection: Connection, ip: str, port: int, ack_number: int) -> None:
        super().__init__(connection, ip, port)
        self.receiver_ack_number = ack_number
        self.sender_buffer = SenderBuffer(connection, ip, port, filePath, ack_number)

    def begin_transfer(self):
        self.sender_buffer.send(self.receiver_ack_number)

    def handle_message(self, message: MessageInfo):
        if self.status == TCPStatusEnum.ESTABLISHED and message.segment.flag != FlagEnum.FIN_FLAG:
            self.sender_buffer.send(message.segment.ack)
        else:
            super().handle_message(message)

            if self.closed:
                self.sender_buffer.set_all_thread()