from .connection import Connection, MessageInfo

# notes
# simulate a tcp connection?
# need a manager that could forward the connections

class BaseTCP:
    connection: Connection
    
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def handle_message(self, message: MessageInfo):
        raise NotImplementedError("handle_message is an abstract function that need to be implemented")
    
    def send_message(self, message: MessageInfo):
        self.connection.send(message)