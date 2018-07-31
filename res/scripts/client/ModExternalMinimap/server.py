import os
import urllib
import posixpath
from abc import ABCMeta, abstractmethod

from threading import Thread
from SocketServer import ThreadingTCPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

from ModExternalMinimap.lib.websocket_server import WebsocketServer


class ConcurrentServer(object):
    __metaclass__ = ABCMeta

    def __init__(self, host='', port=8000):
        self.host = host
        self.port = port
        self.__thread = None

    def start(self):
        if self.__thread is not None:
            return
        self.__thread = Thread(target=self._run_function)
        self.__thread.start()

    def stop(self):
        self._close_function()
        self.__thread.join()
        self.__thread = None

    @abstractmethod
    def _run_function(self):
        pass

    @abstractmethod
    def _close_function(self):
        pass


class ConcurrentHTTPServer(ConcurrentServer):
    def __init__(self, host='', port=8000, directory='.'):
        super(ConcurrentHTTPServer, self).__init__(host=host, port=port)

        class RequestHandler(SimpleHTTPRequestHandler):
            def translate_path(self, path):
                path = path.split('?', 1)[0]
                path = path.split('#', 1)[0]
                trailing_slash = path.rstrip().endswith('/')
                path = posixpath.normpath(urllib.unquote(path))
                words = path.split('/')
                words = filter(None, words)
                path = directory  # patch SimpleHTTPRequestHandler to use different directory than working dir
                for word in words:
                    if os.path.dirname(word) or word in (os.curdir, os.pardir):
                        continue
                    path = os.path.join(path, word)
                if trailing_slash:
                    path += '/'
                return path

        self._request_handler = RequestHandler
        self._server = None

    def _run_function(self):
        self._server = ThreadingTCPServer((self.host, self.port), self._request_handler)
        self._server.daemon_threads = True
        self._server.serve_forever()

    def _close_function(self):
        self._server.shutdown()
        self._server.server_close()
        self._server = None


class ConcurrentWebSocketServer(ConcurrentServer):
    def __init__(self, host='', port=8001, allowed_origins=None):
        super(ConcurrentWebSocketServer, self).__init__(host=host, port=port)
        self._server = None
        self._allowed_origins = allowed_origins

    def _run_function(self):
        self._server = WebsocketServer(host=self.host, port=self.port)
        self._server.daemon_threads = True
        self._server.set_fn_new_client(lambda c, _: self.on_client_connect(c))
        self._server.set_fn_client_left(lambda c, _: self.on_client_disconnect(c))
        self._server.set_fn_message_received(lambda c, _, m: self.on_message(c, m))
        self._server.set_fn_allow_connection(self.allow_connection)
        self._server.serve_forever()

    def _close_function(self):
        self._server.shutdown()
        self._server.server_close()
        self._server = None

    def send_message(self, client, message):
        if self._server:
            self._server.send_message(client, message)

    def broadcast(self, message):
        if self._server:
            self._server.send_message_to_all(message)

    def on_client_connect(self, client):
        pass

    def on_client_disconnect(self, client):
        pass

    def on_message(self, client, message):
        pass
    
    def allow_connection(self, origin):
        return self._allowed_origins is None or origin in self._allowed_origins
