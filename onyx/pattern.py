

import operator as op


class Match(object):
    is_success = True
    is_failure = False

    def __init__(self, after_stream):
        self._bindings = {}
        self.after_stream = after_stream

    def add_binding(self, name, value):
        self._bindings[name] = value

    def binding_value(self, name):
        return self._bindings.get(name)


class FailedMatch(object):
    is_success = False
    is_failure = True

    def __init__(self, stream, pattern):
        self.stream = stream
        self.pattern = pattern


class SimplePattern(object):
    def __init__(self, kind, bind=None):
        self.kind = kind
        self._bind = bind
        self.check_kind = op.attrgetter('is_%s' % kind)

    def match(self, stream):
        value = stream.first

        if self.check_kind(value):
            match = Match(stream.rest)
            if self._bind is not None:
                match.add_binding(self._bind, value)
            return match
        return FailedMatch(stream, self)


