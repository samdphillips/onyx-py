import unittest

from onyx.term import (AssignTerm, BinarySend, BlockTerm, Identifier,
                       KeywordSend, UnarySend)


# noinspection PyPep8Naming,PyAttributeOutsideInit
class _ParserTestCase(object):
    term_cls = None

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
        if self.term_cls is not None:
            self.assertIsInstance(self.term, self.term_cls)
        self.assertTrue(self.parser.at_end())
        self.check()


# noinspection PyPep8Naming,PyAttributeOutsideInit
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


class TermTestCase(unittest.TestCase):
    def runTest(self):
        from onyx.term import Term, TermError
        term = Term('Object', 'id')
        id_term = term.as_identifier()
        self.assertIsInstance(id_term, Identifier)

        with self.assertRaises(TermError):
            term = Term('+', 'binsel')
            term.as_identifier()


class ParsePrimaryId(_ParserTestCase, unittest.TestCase):
    read_string = 'name'
    parse_method = 'primary'
    term_cls = Identifier

    def check(self):
        self.assertEqual(self.term.name, 'name')


class ParsePrimaryNested(_ParserTestCase, unittest.TestCase):
    read_string = '(foo)'
    parse_method = 'primary'
    term_cls = Identifier

    def check(self):
        self.assertEqual(self.term.name, 'foo')


class ParsePrimaryUnary(_ParserTestCase, unittest.TestCase):
    read_string = 'foo bar'
    parse_method = 'primary'
    term_cls = UnarySend

    def check(self):
        self.assertIsInstance(self.term.receiver, Identifier)
        self.assertEqual(self.term.receiver.name, 'foo')
        self.assertEqual(self.term.message, 'bar')


class ParsePrimaryUnaryNested(_ParserTestCase, unittest.TestCase):
    read_string = '(foo bar)'
    parse_method = 'primary'
    term_cls = UnarySend

    def check(self):
        self.assertIsInstance(self.term.receiver, Identifier)
        self.assertEqual(self.term.receiver.name, 'foo')
        self.assertEqual(self.term.message, 'bar')


class ParseBlock(_ParserTestCase, unittest.TestCase):
    read_string = '[ x ]'
    parse_method = 'primary'
    term_cls = BlockTerm


class ParseBlockWithTemps(_ParserTestCase, unittest.TestCase):
    read_string = '[ | e f | a b. c d ]'
    parse_method = 'primary'
    term_cls = BlockTerm

    def check(self):
        self.assertEqual(0, len(self.term.arguments))
        self.assertEqual(2, len(self.term.temporary_variables))
        self.assertEqual(2, len(self.term.statements))


class ParseBlockWithArgs(_ParserTestCase, unittest.TestCase):
    read_string = '[ :a :b | | c d | a]'
    parse_method = 'primary'
    term_cls = BlockTerm


class ParseBlockWithArgs2(_ParserTestCase, unittest.TestCase):
    read_string = '[ :a :b || c d | a]'
    parse_method = 'primary'
    term_cls = BlockTerm

    def check(self):
        self.assertEqual(2, len(self.term.arguments))
        self.assertEqual(2, len(self.term.temporary_variables))
        self.assertEqual(1, len(self.term.statements))


class ParseBlockWithArgsNoTemps(_ParserTestCase, unittest.TestCase):
    read_string = '[ :a :b | a]'
    parse_method = 'primary'
    term_cls = BlockTerm

    def check(self):
        self.assertEqual(2, len(self.term.arguments))
        self.assertEqual(0, len(self.term.temporary_variables))
        self.assertEqual(1, len(self.term.statements))


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


class ParseBinaryPrimaryId(ParsePrimaryId, unittest.TestCase):
    parse_method = 'binary'


class ParseBinaryUnaryChain(ParsePrimaryUnaryChain, unittest.TestCase):
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


class ParseCascade(_ParserTestCase, unittest.TestCase):
    read_string = ("MessageNotUnderstood new receiver: self; "
                   "message: aMessage; signal")
    parse_method = 'cascade'


class ParseCascadePrimary(ParseKeywordPrimary, unittest.TestCase):
    parse_method = 'cascade'


class ParseCascadeBinary(ParseKeywordBinary, unittest.TestCase):
    parse_method = 'cascade'


class ParseCascadeKeyword(ParseKeywordBasic, unittest.TestCase):
    parse_method = 'cascade'


class ParseUnaryMethodHeader(_ParserTestCase, unittest.TestCase):
    read_string = 'foo'
    parse_method = 'method_header'

    def check(self):
        name, arguments = self.term
        self.assertEqual('foo', name)
        self.assertEqual([], arguments)


class ParseBinaryMethodHeader(_ParserTestCase, unittest.TestCase):
    read_string = '+ aNumber'
    parse_method = 'method_header'

    def check(self):
        name, arguments = self.term
        self.assertEqual('+', name)
        self.assertEqual(1, len(arguments))
        self.assertIsInstance(arguments[0], Identifier)
        self.assertEqual('aNumber', arguments[0].name)


class ParseKeywordMethodHeader(_ParserTestCase, unittest.TestCase):
    read_string = 'do: aBlock'
    parse_method = 'method_header'

    def check(self):
        name, arguments = self.term
        self.assertEqual('do:', name)
        self.assertEqual(1, len(arguments))
        self.assertIsInstance(arguments[0], Identifier)
        self.assertEqual('aBlock', arguments[0].name)


class ParseAssignmentExpression(_ParserTestCase, unittest.TestCase):
    read_string = 'a := b'
    parse_method = 'expression'
    term_cls = AssignTerm


class ParseTemporaryVariables(_ParserTestCase, unittest.TestCase):
    read_string = '|a b c|'
    parse_method = 'temporary_variables'

    def check(self):
        self.assertEqual(3, len(self.term))


class ParseTemporaryVariablesEmpty(_ParserTestCase, unittest.TestCase):
    read_string = '| |'
    parse_method = 'temporary_variables'

    def check(self):
        self.assertEqual([], self.term)


class ParseTemporaryVariablesEmptyOneTerm(_ParserTestCase, unittest.TestCase):
    read_string = '||'
    parse_method = 'temporary_variables'

    def check(self):
        self.assertEqual([], self.term)

