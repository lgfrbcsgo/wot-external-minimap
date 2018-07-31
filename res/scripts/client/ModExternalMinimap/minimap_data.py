from abc import ABCMeta, abstractproperty
from itertools import chain
from Math import Matrix
from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent

from ModExternalMinimap.hooks import run_before, run_after


def hook_minimap(func, after=False):
    def _decorate_with(decorator_):
        return decorator_(MinimapComponent, func.__name__)(func)

    return _decorate_with(run_after) if after else _decorate_with(run_before)


class JSONSerializable(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def as_json_serializable(self):
        return None


class Container(JSONSerializable):
    def __init__(self, name):
        super(Container, self).__init__()
        self.name = name
        self._entries = dict()

    def __contains__(self, entry_id):
        return entry_id in self._entries

    def add_entry(self, entry):
        if not isinstance(entry, Entry):
            raise TypeError()
        self._entries[entry.id] = entry

    def get_entry(self, entry_id):
        return self._entries.get(entry_id)

    def remove_entry(self, entry_id):
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False

    def clear(self):
        self._entries = dict()

    @property
    def entries(self):
        return self._entries.itervalues()

    @property
    def as_json_serializable(self):
        return dict(
            name=self.name,
            entries=map(lambda e: e.as_json_serializable, self.entries)
        )


class Entry(JSONSerializable):
    def __init__(self, id, symbol, matrix_or_provider=None, active=False):
        super(Entry, self).__init__()
        self.id = id
        self.symbol = symbol
        self.active = active
        self.matrix_or_provider = matrix_or_provider
        self.invocations = list()

    def push_invocation(self, invocation):
        if not isinstance(invocation, Invocation):
            return TypeError()
        self.invocations.append(invocation)

    def clear_invocations(self):
        self.invocations = list()

    @property
    def matrix(self):
        if self.matrix_or_provider:
            return Matrix(self.matrix_or_provider)
        return None

    @property
    def position(self):
        if self.matrix:
            return self.matrix.translation.list()
        return None

    @property
    def orientation(self):
        if self.matrix:
            return self.matrix.pitch, self.matrix.roll, self.matrix.yaw
        return None

    @property
    def as_json_serializable(self):
        return dict(
            id=self.id,
            symbol=self.symbol,
            position=self.position,
            orientation=self.orientation,
            active=self.active,
            invocations=map(lambda i: i.as_json_serializable, self.invocations)
        )


class Invocation(JSONSerializable):
    def __init__(self, fn_name, *args):
        super(Invocation, self).__init__()
        self.fn_name = fn_name
        self.args = args

    @property
    def as_json_serializable(self):
        return dict(
            function=self.fn_name,
            arguments=self.args
        )


class MinimapData(JSONSerializable):
    def __init__(self):
        self._containers = dict()
        self._setup_hooks()

    def clear(self):
        self._containers = dict()

    def clear_invocations(self):
        for entry in self._entries:
            entry.clear_invocations()

    def addEntry(self, entryID, component, symbol, container, matrix=None, active=False, **kwargs):
        self._remove_from_containers(entryID)
        entry = Entry(entryID, symbol, matrix, active)
        self._add_to_container(entry, container)

    def delEntry(self, component, entryID):
        self._remove_from_containers(entryID)

    def invoke(self, component, entryID, *signature):
        entry = self._find_entry(entryID)
        if entry:
            entry.push_invocation(Invocation(*signature))

    def move(self, component, entryID, container):
        entry = self._find_entry(entryID)
        if entry:
            self._remove_from_containers(entryID)
            self._add_to_container(entry, container)

    def setMatrix(self, component, entryID, matrix):
        entry = self._find_entry(entryID)
        if entry:
            entry.matrix_or_provider = matrix

    def setActive(self, component, entryID, active):
        entry = self._find_entry(entryID)
        if entry:
            entry.active = active

    def _find_entry(self, entry_id):
        for container in self._containers.itervalues():
            if entry_id in container:
                return container.get_entry(entry_id)

    def _add_to_container(self, entry, container_name):
        container = self._containers.get(container_name, Container(container_name))
        container.add_entry(entry)
        self._containers[container.name] = container

    def _remove_from_containers(self, entry_id):
        for container in self._containers.itervalues():
            container.remove_entry(entry_id)

    @property
    def as_json_serializable(self):
        return map(lambda c: c.as_json_serializable, self._containers.itervalues())

    @property
    def _entries(self):
        return chain(*(container.entries for container in self._containers.itervalues()))

    def _setup_hooks(self):
        hook_minimap(self.addEntry, after=True)
        hook_minimap(self.delEntry)
        hook_minimap(self.invoke)
        hook_minimap(self.move)
        hook_minimap(self.setMatrix)
        hook_minimap(self.setActive)
