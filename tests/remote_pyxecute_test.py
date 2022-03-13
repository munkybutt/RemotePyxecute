import inspect
import pathlib
import site

from importlib import reload

proc_spawn_site_path = pathlib.Path(
	inspect.getfile(lambda: None)
).parent.parent
site.addsitedir(str(proc_spawn_site_path))

from proc_spawn import logger
from proc_spawn import server

reload(logger)
reload(server)

server_thread = server.ServerThread(("localhost", 2003))
server_thread.start()
# server_thread.stop()
# del server_thread
