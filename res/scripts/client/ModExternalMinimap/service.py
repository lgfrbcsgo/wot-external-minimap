import json
import BigWorld
from skeletons.gui.game_control import IGameController

from ModExternalMinimap.server import ConcurrentHTTPServer, ConcurrentWebSocketServer
from ModExternalMinimap.minimap_data import MinimapData


class IExternalMinimapController(IGameController):
    pass


class ExternalMinimapController(IExternalMinimapController):
    def __init__(self):
        super(ExternalMinimapController, self).__init__()
        self._http_server = ConcurrentHTTPServer(port=13370, directory='mods/files/external_minimap')
        self._websocket_server = ConcurrentWebSocketServer(port=13371, allowed_origins=[
            'http://localhost:13370',
            'http://127.0.0.1:13370'
        ])
        self.map_data = MinimapData()
        self._callback_id = None

    def start(self):
        self._http_server.start()
        self._websocket_server.start()

    def stop(self):
        self._stop_periodic_update()
        self._http_server.stop()
        self._websocket_server.stop()

    def broadcast(self, *msgs):
        if len(msgs) == 1:
            msgs = msgs[0]
        self._websocket_server.broadcast(json.dumps(msgs))

    def onAvatarBecomePlayer(self):
        self.map_data.clear()
        self._start_periodic_update()

    def onAccountBecomePlayer(self):
        self._stop_periodic_update()

    def _start_periodic_update(self):
        self._push_update()
        # callback on next frame
        self._callback_id = BigWorld.callback(0, self._start_periodic_update)

    def _stop_periodic_update(self):
        if self._callback_id is None:
            return
        BigWorld.cancelCallback(self._callback_id)
        self._callback_id = None

    def _push_update(self):
        self.broadcast(dict(containers=self.map_data.as_json_serializable))
