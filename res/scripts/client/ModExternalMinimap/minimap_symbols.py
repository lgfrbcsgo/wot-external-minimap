from Math import Matrix


_SYMBOLS = dict()


def register_symbol(clazz):
    _SYMBOLS[clazz.__name__] = clazz
    return clazz


def get_symbol(name):
    symbol = _SYMBOLS.get(name)
    if symbol:
        return symbol

    class BasicSymbol(Symbol):
        pass
    BasicSymbol.__name__ = name
    return register_symbol(BasicSymbol)


class Symbol(object):
    def __init__(self, id, container, active=False, matrix_or_mprovider=None):
        self._id = id
        self.container = container
        self.active = active
        self._matrix_or_mprovider = matrix_or_mprovider
        self.unhandled_invocations = []

    def invoke(self, func_name, *args):
        func = getattr(self, 'handle_%s' % func_name, False)
        if func:
            return func(*args)
        self.unhandled_invocations.append(dict(name=func_name, args=args))

    def clear_invocations(self):
        self.unhandled_invocations = []

    def set_matrix(self, matrix_or_mprovider):
        self._matrix_or_mprovider = matrix_or_mprovider

    @property
    def id(self):
        return self._id

    @property
    def matrix(self):
        if self._matrix_or_mprovider:
            return Matrix(self._matrix_or_mprovider)

    @property
    def position(self):
        if self.matrix:
            return self.matrix.translation.list()

    @property
    def orientation(self):
        if self.matrix:
            return self.matrix.pitch, self.matrix.roll, self.matrix.yaw

    @property
    def plain_object(self):
        return dict(
            id=self.id,
            active=self.active,
            position=self.position,
            orientation=self.orientation,
            invocations=self.unhandled_invocations,
            symbol=self.__class__.__name__,
            container=self.container
        )


@register_symbol
class ViewRangeCirclesEntry(Symbol):
    arena_size = (1000, 1000)

    show_max_render_range = False
    max_render_range = 50

    show_max_view_range = False
    max_view_range = 50

    show_view_range = False
    view_range = 50

    def handle_as_initArenaSize(self, x, y):
        self.arena_size = (x, y)

    def handle_as_addDrawRange(self, _id, _min, max):
        self.show_max_render_range = True
        self.max_render_range = max

    def handle_as_addMaxViewRage(self, _id, _min, max):
        self.show_max_view_range = True
        self.max_view_range = max

    def handle_as_addDynamicViewRange(self, _id, _min, actual):
        self.show_view_range = True
        self.view_range = actual

    def handle_as_updateDynRange(self, actual):
        self.view_range = actual

    @property
    def plain_object(self):
        obj = super(ViewRangeCirclesEntry, self).plain_object
        obj.update(
            arenaSize=self.arena_size,
            showMaxRenderRange=self.show_max_render_range,
            maxRenderRange=self.max_render_range,
            showMaxViewRange=self.show_max_view_range,
            maxViewRange=self.max_view_range,
            showViewRange=self.show_view_range,
            viewRange=self.view_range
        )
        return obj


class TeamBaseEntry(Symbol):
    number = 0

    def handle_setPointNumber(self, number):
        self.number = number

    @property
    def plain_object(self):
        obj = super(TeamBaseEntry, self).plain_object
        obj.update(number=self.number)
        return obj


@register_symbol
class AllyTeamBaseEntry(TeamBaseEntry):
    pass


@register_symbol
class EnemyTeamBaseEntry(TeamBaseEntry):
    pass


@register_symbol
class VehicleEntry(Symbol):
    player_id = 0
    type = 'heavyTank'
    name = ''
    team = 'enemy'
    spotted = False
    alive = True

    def handle_setVehicleInfo(self, player_id, vehicle_type, vehicle_name, team, _):
        self.player_id = player_id
        self.type = vehicle_type
        self.name = vehicle_name
        self.team = team

    def handle_setInAoI(self, spotted):
        self.spotted = spotted

    def handle_setDead(self, alive):
        self.alive = alive

    @property
    def plain_object(self):
        obj = super(VehicleEntry, self).plain_object
        obj.update(
            playerID=self.player_id,
            type=self.type,
            name=self.name,
            team=self.team,
            spotted=self.spotted,
            alive=self.alive
        )
        return obj
