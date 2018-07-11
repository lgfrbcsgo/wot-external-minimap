from helpers.dependency import _g_manager as dependency_manager
from skeletons.gui.game_control import IGameStateTracker

from ModExternalMinimap.service import IExternalMinimapController, ExternalMinimapController


def register(manager):
    tracker = manager.getService(IGameStateTracker)
    controller = ExternalMinimapController()
    tracker.addController(controller)
    controller.start()
    manager.addInstance(IExternalMinimapController, controller, finalizer='stop')


dependency_manager.addConfig(register)
