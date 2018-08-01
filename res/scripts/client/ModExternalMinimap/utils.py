from collections import namedtuple
from contextlib import contextmanager


Event = namedtuple('Event', ['target', 'name', 'data', 'symbol'])


class EventBasket(object):
    def __init__(self):
        self._events = []

    def clear(self):
        del self._events[:]

    def push(self, event):
        if isinstance(event, Event):
            self._events.append(event)

    @property
    def events(self):
        return self._events


@contextmanager
def suppress(*Errors):
    try:
        yield None
    except Exception as err:
        if not reduce(lambda t, Error: t or isinstance(err, Error), Errors, False):
            raise err


def assign(target, *dicts, **kwargs):
    for d in dicts:
        target.update(d)
    target.update(**kwargs)
    return target
