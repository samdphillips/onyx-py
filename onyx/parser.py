

from .term import BinarySend, CascadeSend, Identifier, KeywordSend, UnarySend
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

    def assert_at_end(self):
        if not self.at_end():
            raise ParseError(
                "Expected no more terms.  Got: {0}".format(self.stream.first))

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

    def make_sub_parser(self, shape):
        self.assert_term_compound(shape)
        parser = self.__class__(self.stream.first.value)
        return parser

    def parse_primary(self):
        try:
            term = self.stream.first

            if term.is_id:
                term = Identifier(term.value)
            elif term.is_compound:
                if term.shape == '()':
                    parser = self.make_sub_parser('()')
                    term = parser.parse_expression()
                    parser.assert_at_end()
                else:
                    raise ParseError('should write this...')
            else:
                raise ParseError('Expected primary')
            self.step()
            while not self.at_end():
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

        while not self.at_end():
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
        name, arguments = self.parse_keyword_extension(self.parse_binary)

        if name != "":
            term = KeywordSend(term, name, arguments)
        return term

    def parse_keyword_extension(self, parse_argument):
        name = []
        arguments = []
        while not self.at_end():
            term = self.stream.first
            if not term.is_keyword:
                break
            name.append(term.value)
            self.step()
            arguments.append(parse_argument())
        name = ''.join(name)
        return name, arguments

    def parse_cascade(self):
        term = self.parse_keyword()
        messages = []
        while not self.at_end():
            next_term = self.stream.first
            if not (next_term.is_delimiter and next_term.value == ';'):
                break
            self.step()
            next_term = self.stream.first
            arguments = []
            name = next_term.value
            if next_term.is_id:
                self.step()
                message = UnarySend(None, name, arguments)
            elif next_term.is_binsel:
                self.step()
                arguments.append(self.parse_primary())
                message = BinarySend(None, name, arguments)
            elif next_term.is_keyword:
                name, arguments = \
                    self.parse_keyword_extension(self.parse_binary)
                message = KeywordSend(None, name, arguments)
            else:
                raise ParseError('Expected message cascade part')

            messages.append(message)

        if messages != []:
            receiver = term.receiver
            term.receiver = None
            term = CascadeSend(receiver, [term] + messages)
        return term

    def parse_expression(self):
        return self.parse_keyword()

    def parse_identifier(self):
        self.assert_term_kind('is_id')
        identifier = self.stream.first.as_identifier()
        self.step()
        return identifier

    def parse_method_header(self):
        term = self.stream.first
        arguments = []
        if term.is_id:
            name = term.value
            self.step()
        elif term.is_binsel:
            name = term.value
            self.step()
            arguments.append(self.parse_identifier())
        elif term.is_keyword:
            name, arguments = \
                self.parse_keyword_extension(self.parse_identifier)
        else:
            raise ParseError(
                "Expected id, binary selector, or keyword. "
                "got: {0}".format(term))
        return name, arguments

