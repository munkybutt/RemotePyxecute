import asyncore
import logging


class Client(asyncore.dispatcher):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port, message, chunk_size=4096):
        super().__init__()
        self.message = bytes(f"{message}<<<END<<<--", "ascii")
        self.to_send = self.message
        self.received_data = []
        self.chunk_size = chunk_size
        self.logger = logging.getLogger("Client")
        self.create_socket()
        self.logger.debug(f"Connecting to: {host}: {port}")
        self.connect((host, port))

    def handle_connect(self):
        self.logger.debug('handle_connect()')

    def handle_close(self):
        self.logger.debug("handle_close()")
        received_message = "".join(self.received_data)
        if "<<<END<<<--" in received_message:
            received_message = received_message.split("<<<END<<<--")[0]

        self.logger.info(received_message)
        self.close()

    def writable(self) -> bool:
        self.logger.debug(f"writable() -> {bool(self.to_send)}")
        return bool(self.to_send)

    def handle_write(self):
        self.logger.debug("handle_write()")
        sent = self.send(self.to_send)
        self.logger.debug(f"Sent -> ({sent}) {self.to_send[:sent].decode('ascii')}")
        self.to_send = self.to_send[sent:]

    def handle_read(self):
        self.logger.debug("handle_read()")
        data = self.recv(self.chunk_size)
        data = str(data, encoding="ascii")
        self.received_data.append(data)
        if data.endswith("<<<END<<<--"):
            self.handle_close()



if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s: %(message)s",
    )

    ip, port = ('localhost', 2003)
    client = Client(
        ip, port, message="import pymxs; pymxs.runtime.Sphere()"
    )
    asyncore.loop()
