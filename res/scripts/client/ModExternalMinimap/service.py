import json

from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.arena_info.interfaces import IVehiclesAndPositionsController
from skeletons.gui.game_control import IGameController

from ModExternalMinimap.server import DirectoryServingHTTPServer, BroadcastingWebSocketServer


class IExternalMinimapController(IGameController):
    pass


class ExternalMinimapController(IExternalMinimapController, IVehiclesAndPositionsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ExternalMinimapController, self).__init__()
        self._isBattleCtrlInit = False
        self._http_server = DirectoryServingHTTPServer(port=13370, directory='mods/files/external_minimap')
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
