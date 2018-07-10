import os
import json
import urllib
import posixpath

from helpers import dependency
from helpers.dependency import _g_manager as dependency_manager

from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.arena_info.interfaces import IVehiclesAndPositionsController
from skeletons.gui.game_control import IGameController, IGameStateTracker

from threading import Thread, RLock
from SocketServer import TCPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


class ConcurrentServer(object):
    def __init__(self):
        self._server = None
        self.__thread = None
        self.__while_running_lock = RLock()
        self.__closed = False

    def start(self):
        if self.__thread is not None:
            return

        self.__closed = False
        self._server = self._create_server()
        self.__thread = Thread(target=self.__serve)
        self.__thread.start()

    def stop(self):
        if self._server is None:
            return

        self.__closed = True

        with self.__while_running_lock:
            self._close_server(self._server)

        self.__thread.join()
        self.__thread = None
        self._server = None

    def _create_server(self):
        raise NotImplementedError()

    def _serve_once(self, server):
        raise NotImplementedError()

    def _close_server(self, server):
        raise NotImplementedError()

    def __serve(self):
        with self.__while_running_lock:
            while not self.__closed:
                self._serve_once(self._server)


class ConcurrentHTTPServer(ConcurrentServer):
    def __init__(self, host='', port=8000, handler_factory=SimpleHTTPRequestHandler):
        super(ConcurrentHTTPServer, self).__init__()
        self._host = host
        self._port = port
        self._handler_factory = handler_factory

    def _create_server(self):
        return TCPServer((self._host, self._port), self._handler_factory)

    def _serve_once(self, server):
        server.handle_request()

    def _close_server(self, server):
        server.server_close()


class ConcurrentWebSocketServer(ConcurrentServer):
    def __init__(self, host='', port=8001, ws_factory=WebSocket):
        super(ConcurrentWebSocketServer, self).__init__()
        self._host = host
        self._port = port
        self._ws_factory = ws_factory

    def _create_server(self):
        return SimpleWebSocketServer(self._host, self._port, self._ws_factory)

    def _serve_once(self, server):
        server.serveonce()

    def _close_server(self, server):
        server.close()


class DirectoryServingHTTPServer(ConcurrentHTTPServer):
    def __init__(self, host='', port=8000, directory='.'):
        handler_factory = DirectoryServingHTTPServer._make_handler_factory(directory)
        super(DirectoryServingHTTPServer, self).__init__(host, port, handler_factory)

    @staticmethod
    def _make_handler_factory(directory):
        directory = os.path.abspath(directory)

        class HandlerFactory(SimpleHTTPRequestHandler):
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

        return HandlerFactory


class BroadcastingWebSocketServer(ConcurrentWebSocketServer):
    def broadcast(self, msg):
        for client in self._server.connections.itervalues():
            client.sendMessage(msg)


class IExternalMinimapController(IGameController):
    pass


class ExternalMinimapController(IExternalMinimapController, IVehiclesAndPositionsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ExternalMinimapController, self).__init__()
        self._isBattleCtrlInit = False
        self._http_server = DirectoryServingHTTPServer(port=13370, directory='mods/files/minimap_frontend')
        self._broadcaster = BroadcastingWebSocketServer(port=13371)

    def start(self):
        self._http_server.start()
        self._broadcaster.start()

    def stop(self):
        self._http_server.stop()
        self._broadcaster.stop()

    def onAvatarBecomePlayer(self):
        if not self._isBattleCtrlInit:
            self.sessionProvider.addArenaCtrl(self)
            self._isBattleCtrlInit = True

    def onAccountBecomePlayer(self):
        if self._isBattleCtrlInit:
            self.sessionProvider.removeArenaCtrl(self)
            self._isBattleCtrlInit = False

    def updatePositions(self, iterator):
        result = {}
        for v_info, coord in iterator():
            result[v_info.player.name] = list(coord)
        self._broadcaster.broadcast(json.dumps(result))


def register(manager):
    tracker = manager.getService(IGameStateTracker)
    controller = ExternalMinimapController()
    tracker.addController(controller)
    controller.start()
    manager.addInstance(IExternalMinimapController, controller, finalizer='stop')


dependency_manager.addConfig(register)
