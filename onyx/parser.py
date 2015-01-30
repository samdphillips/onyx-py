

from .term import BinarySend, Identifier, UnarySend
from .util.stream import EmptyStreamError, Stream


class ParseError(Exception):
    pass


class Parser(object):
    def __init__(self, reader):
        self.stream = Stream.from_sequence(reader)

    def step(self):
        self.stream = self.stream.rest

    def parse_primary(self):
        try:
            term = self.stream.first
            if not term.is_id:
                raise ParseError('Expected primary')
            term = Identifier(term.value)
            self.step()
            while True:
                next_term = self.stream.first
                if not next_term.is_id:
                    break
                term = UnarySend(term, next_term.value)
                self.step()
            return term
        except EmptyStreamError as e:
            raise ParseError('End of stream encountered, expected primary', e)


    def parse_binary(self):
        term = self.parse_primary()

        while True:
            next_term = self.stream.first
            if not next_term.is_binsel:
                break
            message = next_term.value
            self.step()
            argument = self.parse_primary()
            term = BinarySend(term, message, [argument])
        return term


