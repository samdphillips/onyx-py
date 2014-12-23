

from .term import Identifier, UnarySend
from .util.stream import Stream


class Parser(object):
    def __init__(self, reader):
        self.stream = Stream.from_sequence(reader)

    def step(self):
        self.stream = self.stream.rest

    def parse_primary(self):
        term = self.stream.first
        term = Identifier(term.value)
        self.step()
        while True:
            next_term = self.stream.first
            if not next_term.is_id:
                break
            term = UnarySend(term, next_term.value)
            self.step()
        return term



