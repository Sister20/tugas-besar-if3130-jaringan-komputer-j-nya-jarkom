import logging
from threading import Thread, Event
from time import sleep
from .segment import Segment
from .connection import Connection
from .file import FilePayload
from .connection import MessageInfo
from .constants import TIMEOUT

from collections import deque

class SenderBuffer:
    ip_dest: str
    port_dest: int
    connection: Connection
    file_payload: FilePayload
    event_buffer: deque[Event]
    thread_buffer: deque[Thread]
    window_size: int = 4
    last_byte_acked: int
    init_sequence_number: int

    def __init__(self,
                 connection: Connection,
                 ip_dest: str,
                 port_dest: int,
                 path: str,
                 init_sequence_number: int,
                 ) -> None:
        self.connection = connection
        self.ip_dest = ip_dest
        self.port_dest = port_dest
        self.file_payload = FilePayload(path)
        self.last_byte_acked = init_sequence_number - 1
        self.last_byte_send = init_sequence_number - 1
        self.init_sequence_number = init_sequence_number
        self.event_buffer = deque()
        self.thread_buffer = deque()

    def send(self, ack_number: int) -> None:
        if ack_number <= self.last_byte_acked:
            return
        try:
            # print(f"ack_number {ack_number} last_byte_acked {self.last_byte_acked} last_byte_send {self.last_byte_send}")
            self._end_task(ack_number - self.last_byte_acked - 1)
            self._start_task(self.window_size - (self.last_byte_send - self.last_byte_acked))
            self.last_byte_acked = ack_number - 1
        except IndexError:
            logging.info("INDEX ERROR PLIS HAJDLE")
            # todo index error
        except Exception as e:
            logging.info(f"ERROR {e}")
    
    def _send_segment_with_backoff_timeout(self, event: Event, segment: Segment, timeout = TIMEOUT, max_retry: int = 10) -> None:
        retry = 0

        while not event.is_set() and retry < max_retry:
            self.connection.send(
                MessageInfo(
                    self.ip_dest,
                    self.port_dest,
                    segment,
                )
            )
            sleep(timeout)
            retry += 1


    def _start_task(self, count: int) -> None:
        for _ in range(count):
            segment = self.file_payload.get_segment(self.last_byte_send + 1 - (self.init_sequence_number))
            segment.sequence_number = self.last_byte_send + 1
            event = Event()
            thread = Thread(target=self._send_segment_with_backoff_timeout, args=(event, segment,))
            thread.start()
            self.event_buffer.append(event)
            self.thread_buffer.append(thread)
            self.last_byte_send += 1
            

    def _end_task(self, count: int) -> None:
        for _ in range(count):
            event = self.event_buffer.popleft()
            thread = self.thread_buffer.popleft()
            event.set()
            self.last_byte_acked += 1

    def set_all_thread(self):
        for ev in self.event_buffer:
            ev.set()
