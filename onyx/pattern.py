

import operator as op


class Binding(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Match(object):
    is_success = True
    is_failure = False

    def __init__(self, after_stream):
        self._bindings = {}
        self.after_stream = after_stream

    def add_binding(self, binding):
        self._bindings[binding.name] = binding

    def merge_bindings(self, matches):
        for m in matches:
            for binding in m.bindings():
                self.add_binding(binding)

    def bindings(self):
        return self._bindings.values()

    def binding(self, name):
        return self._bindings.get(name)

    def binding_value(self, name):
        b = self.binding(name)
        if b is not None:
            return b.value
        return None


class FailedMatch(object):
    is_success = False
    is_failure = True

    def __init__(self, stream, pattern):
        self.stream = stream
        self.pattern = pattern


class SimplePattern(object):
    def __init__(self, kind, value=None, bind=None):
        self.kind   = kind
        self._bind  = bind
        self._value = value
        self.check_kind = op.attrgetter('is_%s' % kind)

    def check_value(self, term):
        if self._value is None:
            return True
        return term.value == self._value

    def match(self, stream):
        term = stream.first

        if self.check_kind(term) and self.check_value(term):
            match = Match(stream.rest)
            if self._bind is not None:
                match.add_binding(Binding(self._bind, term))
            return match
        return FailedMatch(stream, self)


class SequencePattern(object):
    def __init__(self, patterns):
        self._patterns = patterns

    def match(self, stream):
        matches = []

        for pat in self._patterns:
            submatch = pat.match(stream)
            if submatch.is_failure:
                return submatch
            matches.append(submatch)
            stream = submatch.after_stream

        match = Match(stream)
        match.merge_bindings(matches)
        return match


