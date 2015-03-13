

from .term import BinarySend, Identifier, KeywordSend, UnarySend
from .util.stream import EmptyStreamError, Stream


class ParseError(Exception):
    pass


class Parser(object):
    def __init__(self, reader):
        self.stream = Stream.from_sequence(reader)

    def step(self):
        self.stream = self.stream.rest

    def at_end(self):
        return self.stream.is_empty

    def assert_term_value(self, value):
        term = self.stream.first
        term_value = term.value
        if term_value != value:
            raise ParseError("Expected term value: {0}, "
                             "got: {1}".format(value, term_value))

    def assert_term_compound(self, shape):
        term = self.stream.first
        if not (term.is_compound and term.shape == shape):
            raise ParseError("Expected compound with shape {0!r}, "
                             "got: {1}".format(shape, term))

    def assert_term_kind(self, kind):
        term = self.stream.first
        value = getattr(term, kind, False)
        if not value:
            raise ParseError(
                "Expected term kind {0!r}, got: {1}".format(kind, term))

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

    def parse_keyword(self):
        term = self.parse_binary()
        message_parts = []
        arguments = []
        while True:
            next_term = self.stream.first
            if not next_term.is_keyword:
                break
            part = next_term.value
            self.step()
            argument = self.parse_binary()
            message_parts.append(part)
            arguments.append(argument)

        if message_parts != []:
            message = ''.join(message_parts)
            term = KeywordSend(term, message, arguments)
        return term

