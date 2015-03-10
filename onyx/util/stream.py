

class EmptyStreamError(Exception):
    pass


class EmptyState(object):
    def is_empty(self, stream):
        return True

    def value(self, stream):
        raise EmptyStreamError()

    def rest(self, stream):
        raise EmptyStreamError()


EMPTY = EmptyState()


class PendingState(object):
    __slots__ = ['_iterator']

    def __init__(self, iterator):
        self._iterator = iterator

    def value(self, stream):
        state = self.force(stream)
        return state.value(stream)

    def rest(self, stream):
        state = self.force(stream)
        return state.rest(stream)

    def is_empty(self, stream):
        state = self.force(stream)
        return state.is_empty(stream)

    def force(self, stream):
        try:
            v = self._iterator.next()
            s = ValueState(v, self)
        except StopIteration:
            s = EMPTY
        stream._state = s
        return s


class ValueState(object):
    __slots__ = ['_value', '_rest']

    def __init__(self, value, rest):
        self._value = value
        self._rest = Stream(rest)

    def value(self, stream):
        return self._value

    def rest(self, stream):
        return self._rest

    def is_empty(self, stream):
        return False


class Stream(object):
    __slots__ = ['_state']

    @classmethod
    def from_sequence(cls, it):
        return cls(PendingState(iter(it)))

    @classmethod
    def from_file(cls, filename):
        f = file(filename, 'r')
        it = CharIoIterator(f)
        return cls.from_sequence(it)

    def __init__(self, state):
        self._state = state

    @property
    def first(self):
        return self._state.value(self)

    @property
    def rest(self):
        return self._state.rest(self)

    @property
    def is_empty(self):
        return self._state.is_empty(self)

    def __iter__(self):
        s = self
        while not s.is_empty:
            yield s.first
            s = s.rest
        raise StopIteration


class CharIoIterator(object):
    def __init__(self, io):
        self._io = io

    def __iter__(self):
        return self

    def next(self):
        c = self._io.read(1)
        if c == '':
            raise StopIteration
        return c


