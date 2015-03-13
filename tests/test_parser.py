import unittest

from onyx.term import BinarySend, Identifier, KeywordSend, UnarySend


# noinspection PyPep8Naming
class _ParserTestCase(object):
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


# noinspection PyPep8Naming
class _FailingParserTestCase(object):
    def setUp(self):
        from onyx.util.stream import Stream
        from onyx.parser import Parser
        from onyx.reader import Reader

        stream = Stream.from_sequence(self.read_string)
        reader = Reader(stream)
        self.parser = Parser(reader)

    def shortDescription(self):
        return self.__class__.__doc__

    def check(self):
        pass

    def runTest(self):
        from onyx.parser import ParseError

        parse_method = getattr(self.parser, 'parse_' + self.parse_method)
        with self.assertRaises(ParseError):
            parse_method()


class ParsePrimaryId(_ParserTestCase, unittest.TestCase):
    read_string = 'name'
    parse_method = 'primary'
    term_cls = Identifier

    def check(self):
        self.assertEqual(self.term.name, 'name')


class ParsePrimaryUnary(_ParserTestCase, unittest.TestCase):
    read_string = 'foo bar'
    parse_method = 'primary'
    term_cls = UnarySend

    def check(self):
        self.assertIsInstance(self.term.receiver, Identifier)
        self.assertEqual(self.term.receiver.name, 'foo')
        self.assertEqual(self.term.message, 'bar')


class ParsePrimaryUnaryChain(_ParserTestCase, unittest.TestCase):
    read_string = 'a b c'
    parse_method = 'primary'
    term_cls = UnarySend

    def check(self):
        r = self.term.receiver
        self.assertIsInstance(r, UnarySend)
        self.assertIsInstance(r.receiver, Identifier)
        self.assertEqual(r.receiver.name, 'a')
        self.assertEqual(r.message, 'b')
        self.assertEqual(self.term.message, 'c')


class ParseBinaryPrimary(ParsePrimaryUnaryChain, unittest.TestCase):
    parse_method = 'binary'


class ParseBinaryBasic(_ParserTestCase, unittest.TestCase):
    read_string = 'a + b'
    parse_method = 'binary'
    term_cls = BinarySend

    def check(self):
        self.assertIsInstance(self.term.receiver, Identifier)
        self.assertEqual(self.term.receiver.name, 'a')
        self.assertEqual(self.term.message, '+')
        self.assertIsInstance(self.term.arguments[0], Identifier)
        self.assertEqual(self.term.arguments[0].name, 'b')


class ParseBinaryExtended(_ParserTestCase, unittest.TestCase):
    read_string = 'a + b * c'
    parse_method = 'binary'
    term_cls = BinarySend


class ParseBinaryFailStart(_FailingParserTestCase, unittest.TestCase):
    read_string = '+ b'
    parse_method = 'binary'


class ParseBinaryFailEnd(_FailingParserTestCase, unittest.TestCase):
    read_string = 'a +'
    parse_method = 'binary'


class ParseKeywordPrimary(ParsePrimaryUnaryChain, unittest.TestCase):
    parse_method = 'keyword'


class ParseKeywordBinary(ParseBinaryBasic, unittest.TestCase):
    parse_method = 'keyword'


class ParseKeywordBasic(_ParserTestCase, unittest.TestCase):
    read_string = 'a foo: b'
    parse_method = 'keyword'
    term_cls = KeywordSend


class ParseKeywordFailStart(_FailingParserTestCase, unittest.TestCase):
    read_string = 'foo: bar'
    parse_method = 'keyword'


class ParseKeywordFailEnd(_FailingParserTestCase, unittest.TestCase):
    read_string = 'foo bar:'
    parse_method = 'keyword'

