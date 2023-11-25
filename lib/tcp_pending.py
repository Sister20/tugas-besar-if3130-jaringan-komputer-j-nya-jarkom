from typing import  Dict, Tuple

class TCPPending:
    tcp_client: Dict[Tuple[str, int], int] = {}

    def __init__(self) -> None:
        pass

    def add(self, ip: str, port: int, init_sequence_number: int) -> None:
        self.tcp_client.update({(ip, port): init_sequence_number})

    def remove(self, ip: str, port: int) -> None:
        self.tcp_client.pop((ip, port))

    def is_pending(self, ip: str, port: int) -> bool:
        return (ip, port) in self.tcp_client
    
    def get_init_sequence_number(self, ip: str, port: int) -> int:      
        return self.tcp_client[(ip, port)]