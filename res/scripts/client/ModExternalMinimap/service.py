import json
import BigWorld

from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IGameController

from ModExternalMinimap.server import ConcurrentHTTPServer, ConcurrentWebSocketServer
from ModExternalMinimap.minimap_data import MinimapData


class IExternalMinimapController(IGameController):
    pass


class ExternalMinimapController(IExternalMinimapController):
    session_provider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ExternalMinimapController, self).__init__()
        self._http_server = ConcurrentHTTPServer(port=13370, directory='mods/minimap-ui/dist')
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

    @property
    def arena(self):
        arena_type = self.session_provider.arenaVisitor.type
        bottom_left, upper_right = arena_type.getBoundingBox()
        width = upper_right[0] - bottom_left[0]
        height = upper_right[1] - bottom_left[1]
        return dict(
            name=arena_type.getName(),
            size=(width, height)
        )

    def _push_update(self):
        self.broadcast(dict(
            entries=self.map_data.entries,
            events=self.map_data.events,
            arena=self.arena
        ))
        self.map_data.clear_events()
