import json

from helpers import dependency
from helpers.dependency import _g_manager as dependency_manager

from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.arena_info.interfaces import IVehiclesAndPositionsController
from skeletons.gui.game_control import IGameController, IGameStateTracker

from threading import Thread, RLock
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


class ThreadedWebSocketServer:
    def __init__(self, host='', port=8000, ws_factory=WebSocket):
        self._host = host
        self._port = port
        self._ws_server = None
        self._ws_factory = ws_factory
        self._thread = None
        self._close_lock = RLock()
        self._closed = False

    def start(self):
        if self._thread is not None:
            return

        self._ws_server = SimpleWebSocketServer(self._host, self._port, self._ws_factory)
        self._thread = Thread(target=self._serve)
        self._thread.start()

    def stop(self):
        if self._ws_server is None:
            return

        with self._close_lock:
            self._ws_server.close()
            self._closed = True

        self._thread.join()
        self._thread = None

    def _serve(self):
        closed = False
        while not closed:
            with self._close_lock:
                if not self._closed:
                    self._ws_server.serveonce()
                else:
                    closed = True


class BroadcastingWebSocketServer(ThreadedWebSocketServer):
    def broadcast(self, msg):
        for client in self._ws_server.connections.itervalues():
            client.sendMessage(msg)


class IExternalMinimapController(IGameController):
    pass


class ExternalMinimapController(IExternalMinimapController, IVehiclesAndPositionsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ExternalMinimapController, self).__init__()
        self._isBattleCtrlInit = False
        self._broadcaster = BroadcastingWebSocketServer()

    def start(self):
        self._broadcaster.start()

    def stop(self):
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
