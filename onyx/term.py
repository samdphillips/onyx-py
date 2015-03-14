

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

    def __init__(self, value, flag, shape=None):
        self.value = value
        self.shape = shape
        setattr(self, 'is_%s' % flag, True)

    def as_identifier(self):
        if self.is_id:
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
