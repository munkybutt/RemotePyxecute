from __future__ import annotations

import asyncore
import logging
import traceback

from . import logger
from Qt import QtCore


class ThreadBridgeReceiver(QtCore.QObject):
    response = QtCore.Signal(str)

class ThreadResponder(QtCore.QObject):
    response = QtCore.Signal(str)


class Server(asyncore.dispatcher):
    """
    Receives connections and establishes handlers for each client.
    """

    def __init__(self, address: tuple[str, int], thread:ServerThread) -> None:
        super().__init__()
        self.thread = thread
        self.logger.log_to("Server")
        self.response_handler = None
        self.create_socket()
        self.bind(address)
        _address = self.socket.getsockname()
        self.logger.log_to(f"binding to {_address}")
        self.listen(1)

    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = self.thread.logger#

        return self._logger

    def handle_accepted(self, sock, address) -> None:
        self.logger.log_to("handle_accepted()")
        self.logger.log_to(f"[Server] Connection from: {address}")
        self.response_handler = ResponseHandler(sock, self.thread)

    def handle_close(self) -> None:
        self.logger.log_to("Shutting down Server")
        if self.response_handler:
            self.response_handler.handle_close()
        self.close()
        self.logger.log_to("Server shut down")


class ResponseHandler(asyncore.dispatcher):
    """
    Handles responding to messages from a single client.
    """

    def __init__(self, socket, thread: ServerThread, chunk_size: int = 4096):

        self.thread = thread
        self.thread.response.connect(self.on_response)
        self.logger.log_to("ResponseHandler")
        self.logger.log_to(f"ResponseHandler: {socket.getsockname()}")
        self.chunk_size = chunk_size
        super().__init__(socket)
        self.response_data: bytes = b""

    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = self.thread.logger#

        return self._logger

    @QtCore.Slot(str)
    def on_response(self, data: str):
        self.logger.log_to("on_response")
        self.response_data = bytes(f"{data}<<<END<<<--", "ascii")

    def writable(self):
        """
        We want to write if we have received data.
        """

        self.logger.log_to(f"writable() -> {self.response_data}")
        return bool(self.response_data)

    def handle_write(self):
        """
        Write as much as possible of the most recent message we have received.
        """

        data = self.response_data
        sent = self.send(data)
        if sent < len(data):
            self.response_data = data[sent:]

        # self.logger.log_to('handle_write() -> (%d) "%s"', sent, data[:sent])
        # if not self.writable():
        #     self.handle_close()

    def handle_read(self):
        """
        Read an incoming message from the client and put it into our outgoing queue.
        """

        self.logger.log_to("handle_read()")
        data = self.recv(self.chunk_size)
        data = str(data, encoding="ascii")
        self.logger.log_to(f"data: {data}")
        # if data.endswith("<<<END<<<--"):
        if "<<<END<<<--" in data:
            _data = data.split("<<<END<<<--")[0]
            self.thread.received.emit(_data)
            self.logger.log_to(
                f"handle_read() -> ({len(_data)}) '{_data}'"
            )

    def handle_close(self):
        self.logger.log_to("Shutting down ResponseHandler")
        self.close()
        self.thread.response.disconnect(self.on_response)


class ServerThread(QtCore.QThread):
    """
    Thread to run the asyncore.loop on.

        This prevents the interpreter the server is running on
        from being blocked.
        It is currently a QThread to make use of signals and
        slots. These allow for thread safe communication as the
        received data needs to be executed in the main thread.
    """

    received = QtCore.Signal(str)
    response = QtCore.Signal(str)

    def __init__(self, address: tuple[str, int]):
        super().__init__()
        self.logger = logger.get_logger("ServerThread")
        # self.logger.enable_file_log(logging.DEBUG)
        self.logger.log_to("ServerThread")
        self.server = Server(address, self)
        self.received.connect(self.on_received)

    def run(self):
        asyncore.loop()

    def stop(self):
        self.server.handle_close()

    @QtCore.Slot(str)
    def on_received(self, data:str):
        try:
            self.logger.log_to(f"Received data:\n'{data}'")
            exec(data)
        except Exception:
            _traceback = traceback.format_exc()
            self.logger.log_to("Exception occured:\n{_traceback}")
            self.response.emit(_traceback)
            return

        self.response.emit("SUCCESS")


if __name__ == "__main__":

    try:
        st.stop()
    except: pass
    st = ServerThread(("localhost", 2001))
    st.start()
    # st.response.emit("SUCCESS")