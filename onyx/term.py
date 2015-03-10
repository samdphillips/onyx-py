

class Identifier(object):
    def __init__(self, name):
        self.name = name


class MessageSend(object):
    def __init__(self, receiver, message, arguments=[]):
        self.receiver = receiver
        self.message = message
        self.arguments = arguments


class UnarySend(MessageSend):
    pass


class BinarySend(MessageSend):
    pass


