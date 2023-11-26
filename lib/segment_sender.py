import logging
from threading import Thread, Event
from time import sleep
from .segment import Segment
from .connection import Connection
from .file import FilePayload
from .connection import MessageInfo

from collections import deque

class SenderBuffer:
    ip_dest: str
    port_dest: int
    connection: Connection
    segment_buffer: deque[Segment] = deque()
    event_buffer: deque[Event] = deque()
    window_size: int = 5
    last_byte_acked: int

    def __init__(self,
                 connection: Connection,
                 ip_dest: str,
                 port_dest: int,
                 path: str,
                 init_sequence_number: int,
                 ) -> None:
        print("INIT SENDER BUFFER")
        self.connection = connection
        self.ip_dest = ip_dest
        self.port_dest = port_dest
        file_payload = FilePayload(path)
        self.segment_buffer = deque(file_payload.get_segments())
        self.last_byte_acked = init_sequence_number - 1
        self.last_byte_send = init_sequence_number - 1

    def send(self, ack_number: int) -> None:
        if ack_number <= self.last_byte_acked:
            return
        
        try:
            self._end_task(ack_number - self.last_byte_acked - 1)
            self._start_task(self.window_size - (self.last_byte_send - self.last_byte_acked))
            self.last_byte_acked = ack_number - 1
        except IndexError:
            logging.info("INDEX ERROR PLIS HAJDLE")
            # todo index error


    def _send_segment_with_backoff_timeout(self, event: Event, segment: Segment, timeout:int = 2) -> None:
        while not event.is_set():
            self.connection.send(
                MessageInfo(
                    self.ip_dest,
                    self.port_dest,
                    segment,
                )
            )
            logging.info(f"Sent packet {segment} to {self.ip_dest}:{self.port_dest} with timeout {timeout}")
            sleep(timeout)


    def _start_task(self, count: int) -> None:
        for i in range(count):
            segment = self.segment_buffer.popleft()
            segment.ack = self.last_byte_acked + 1 + i
            event = Event()
            thread = Thread(target=self._send_segment_with_backoff_timeout, args=(event, segment,))
            thread.start()
            self.event_buffer.append(event)
            
        self.last_byte_send += count

    def _end_task(self, count: int) -> None:
        for _ in range(count):
            event = self.event_buffer.popleft()
            event.set()
        self.last_byte_acked += count