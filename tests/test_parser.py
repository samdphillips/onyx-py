

import unittest

from onyx.term import Identifier


class _ParserTestCase(unittest.TestCase):
    def setUp(self):
        from onyx.util.stream import Stream
        from onyx.parser import Parser
        from onyx.reader import Reader
        stream = Stream.from_sequence(self.read_string)
        reader = Reader(stream)
        self.parser = Parser(reader)
        parse_method = getattr(self.parser, 'parse_' + self.parse_method)
        self.term = parse_method()

    def shortDescription(self):
        return self.__class__.__doc__

    def runTest(self):
        self.assertIsInstance(self.term, self.term_cls)


class ParsePrimaryId(_ParserTestCase):
    read_string  = 'name'
    parse_method = 'primary'
    term_cls     = Identifier


