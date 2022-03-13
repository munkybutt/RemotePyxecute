import pathlib
import site
import sys


def __setup__():
	current_directory = pathlib.Path(__file__).parent
	site.addsitedir(current_directory.parent)
	import remote_pyxecute

__setup__()

from . import server

server_thread = server.ServerThread(("localhost", 2001))
server_thread.start()