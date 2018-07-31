from contextlib import contextmanager
from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent

from ModExternalMinimap.hooks import run_before, run_after
from ModExternalMinimap.minimap_symbols import get_symbol


@contextmanager
def ignore(*Errors):
    try:
        yield None
    except Exception as err:
        if not reduce(lambda t, Error: t or isinstance(err, Error), Errors, False):
            raise err


def hook_minimap(func, after=False):
    def _decorate_with(decorator_):
        return decorator_(MinimapComponent, func.__name__)(func)

    return _decorate_with(run_after) if after else _decorate_with(run_before)


class MinimapData(object):
    def __init__(self):
        self._entries = dict()
        self._setup_hooks()

    def clear(self):
        self._entries = dict()

    def clear_invocations(self):
        for entry in self._entries.itervalues():
            entry.clear_invocations()

    def addEntry(self, entryID, component, symbol, container, matrix=None, active=False, **kwargs):
        Symbol = get_symbol(symbol)
        self._entries[entryID] = Symbol(entryID, container, active, matrix)

    def delEntry(self, component, entryID):
        with ignore(KeyError):
            del self._entries[entryID]

    def invoke(self, component, entryID, *signature):
        with ignore(KeyError):
            self._entries[entryID].invoke(*signature)

    def move(self, component, entryID, container):
        with ignore(KeyError):
            self._entries[entryID].container = container

    def setMatrix(self, component, entryID, matrix):
        with ignore(KeyError):
            self._entries[entryID].set_matrix(matrix)

    def setActive(self, component, entryID, active):
        with ignore(KeyError):
            self._entries[entryID].active = active

    @property
    def plain_list(self):
        return [entry.plain_object for entry in self._entries.itervalues()]

    def _setup_hooks(self):
        hook_minimap(self.addEntry, after=True)
        hook_minimap(self.delEntry)
        hook_minimap(self.invoke)
        hook_minimap(self.move)
        hook_minimap(self.setMatrix)
        hook_minimap(self.setActive)
