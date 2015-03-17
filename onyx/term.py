

class TermError(Exception):
    pass


class Term(object):
    is_id = False
    is_eof = False
    is_compound = False
    is_keyword = False
    is_string = False
    is_binsel = False
    is_integer = False
    is_delimiter = False
    is_assignment = False
    is_block_argument = False

    def __init__(self, value, flag, shape=None):
        self.value = value
        self.shape = shape
        setattr(self, 'is_%s' % flag, True)

    def as_identifier(self):
        if self.is_id or self.is_block_argument:
            return Identifier(self.value)
        raise TermError('Term is not an identifier', self)

    def __repr__(self):
        return '<{0} {1!r}>'.format(self.__class__.__name__, self.value)


class Identifier(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<{0} {1!r}>'.format(self.__class__.__name__, self.name)


class MessageSend(object):
    def __init__(self, receiver, message, arguments=None):
        self.receiver = receiver
        self.message = message
        if arguments is None:
            arguments = []
        self.arguments = arguments


class UnarySend(MessageSend):
    pass


class BinarySend(MessageSend):
    pass


class KeywordSend(MessageSend):
    pass


class CascadeSend(object):
    def __init__(self, receiver, messages):
        self.receiver = receiver
        self.messages = messages


class AssignTerm(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class BlockTerm(object):
    def __init__(self, arguments, temporary_variables, statements):
        self.arguments = arguments
        self.temporary_variables = temporary_variables
        self.statements = statements


class EscapeTerm(object):
    def __init__(self, term):
        self.term = term