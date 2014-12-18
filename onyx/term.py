

class Identifier(object):
    def __init__(self, name):
        self.name = name


class UnarySend(object):
    def __init__(self, receiver, message):
        self.receiver = receiver
        self.message  = message


