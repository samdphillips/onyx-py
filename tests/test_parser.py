

import unittest

from onyx.term import Identifier, UnarySend


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

    def check(self):
        pass

    def runTest(self):
        self.assertIsInstance(self.term, self.term_cls)
        self.assertTrue(self.parser.stream.first.is_eof)
        self.check()


class ParsePrimaryId(_ParserTestCase):
    read_string  = 'name'
    parse_method = 'primary'
    term_cls     = Identifier

    def check(self):
        self.assertEqual(self.term.name, 'name')

class ParsePrimaryUnary(_ParserTestCase):
    read_string  = 'foo bar'
    parse_method = 'primary'
    term_cls     = UnarySend

    def check(self):
        self.assertIsInstance(self.term.receiver, Identifier)
        self.assertEqual(self.term.receiver.name, 'foo')
        self.assertEqual(self.term.message, 'bar')


class ParsePrimaryUnaryChain(_ParserTestCase):
    read_string  = 'a b c'
    parse_method = 'primary'
    term_cls     = UnarySend

    def check(self):
        r = self.term.receiver
        self.assertIsInstance(r, UnarySend)
        self.assertIsInstance(r.receiver, Identifier)
        self.assertEqual(r.receiver.name, 'a')
        self.assertEqual(r.message, 'b')
        self.assertEqual(self.term.message, 'c')


