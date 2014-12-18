

from .term import Identifier
from .util.stream import Stream


class Parser(object):
    def __init__(self, reader):
        self.stream = Stream.from_sequence(reader)

    def parse_primary(self):
        term = self.stream.first
        return Identifier(term.value)


