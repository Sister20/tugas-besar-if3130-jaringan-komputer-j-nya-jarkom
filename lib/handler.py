from .connection import MessageInfo
from .segment import FlagEnum
from .tcp import TCPClient, TCPStatusEnum, TCPServer
import logging

class FileReceiver(TCPClient):
    def handle_message(self, message: MessageInfo):
        if self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.SYN_ACK_FLAG:
            super().handle_message(message)
            return
        elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.NO_FLAG:
            # called but not returned
            super().handle_message(message)
        # todo add condition if closing connection and pass to parent class

        # handle file here
        
class FileSender(TCPServer):
    def begin_transfer(self):
        logging.info("Transfer started")

    def handle_message(self, message: MessageInfo):
        logging.info("Received data")