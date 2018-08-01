from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import TRANSFORM_FLAG

from ModExternalMinimap.hooks import run_before, run_after
from ModExternalMinimap.utils import EventBasket, suppress
from ModExternalMinimap.minimap_symbols import get_symbol


def hook_minimap(func, after=False):
    def _decorate_with(decorator_):
        return decorator_(MinimapComponent, func.__name__)(func)

    return _decorate_with(run_after) if after else _decorate_with(run_before)


class MinimapData(object):
    def __init__(self):
        self._entries = dict()
        self._setup_hooks()
        self._event_basket = EventBasket()

    def clear(self):
        self._entries = dict()
        self.clear_events()

    def clear_events(self):
        self._event_basket.clear()

    def addEntry(self, entryID, component, symbol, container, matrix=None, active=False, transformProps=TRANSFORM_FLAG.DEFAULT):
        Symbol = get_symbol(symbol)
        self._entries[entryID] = Symbol(entryID, container, active, matrix, event_basket=self._event_basket)

    def delEntry(self, component, entryID):
        with suppress(KeyError):
            del self._entries[entryID]

    def invoke(self, component, entryID, *signature):
        with suppress(KeyError):
            self._entries[entryID].invoke(*signature)

    def move(self, component, entryID, container):
        with suppress(KeyError):
            self._entries[entryID].container = container

    def setMatrix(self, component, entryID, matrix):
        with suppress(KeyError):
            self._entries[entryID].set_matrix(matrix)

    def setActive(self, component, entryID, active):
        with suppress(KeyError):
            self._entries[entryID].active = active

    @property
    def entries(self):
        return map(lambda e: e.plain_object, self._entries.itervalues())

    @property
    def events(self):
        return self._event_basket.events

    def _setup_hooks(self):
        hook_minimap(self.addEntry, after=True)
        hook_minimap(self.delEntry)
        hook_minimap(self.invoke)
        hook_minimap(self.move)
        hook_minimap(self.setMatrix)
        hook_minimap(self.setActive)
