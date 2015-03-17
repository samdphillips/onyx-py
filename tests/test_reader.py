import unittest


# noinspection PyPep8Naming
class _ReaderTestCase(object):
    def init_reader(self, s):
        from onyx.util.stream import Stream
        from onyx.reader import Reader, ReadError
        stream = Stream.from_sequence(s)
        self.reader = Reader(stream)
        self.ReadError = ReadError

    def setUp(self):
        self.init_reader(self.read_string)

    def assert_reader_at_end(self):
        if not self.reader.is_at_end():
            self.fail('reader is not at end')

    def assert_term_value(self, v):
        if self.term.is_compound:
            actual = [t.value for t in self.term.value]
        else:
            actual = self.term.value
        self.assertEqual(actual, v)


class _ReaderMethod(_ReaderTestCase):
    def setUp(self):
        super(_ReaderMethod, self).setUp()
        reader_method = getattr(self.reader, 'read_' + self.reader_method)
        self.term = reader_method()


# noinspection PyPep8Naming
class _ReadTerm(_ReaderMethod):
    reader_method = 'term'

    def shortDescription(self):
        return self.__class__.__doc__

    def runTest(self):
        self.assertTrue(getattr(self.term, 'is_' + self.term_type))
        self.assert_term_value(self.term_value)
        self.assert_reader_at_end()

    @property
    def term_value(self):
        return self.read_string


class _ReadId(_ReadTerm):
    reader_method = 'id_or_kw'
    term_type = 'id'


class _ReadBinsel(_ReadTerm):
    reader_method = 'binsel'
    term_type = 'binsel'


# noinspection PyPep8Naming
class _ReadErrorTest(_ReaderTestCase):
    def runTest(self):
        reader_method = getattr(self.reader, 'read_' + self.reader_method)
        with self.assertRaises(self.ReadError):
            reader_method()


class ReadSpace(_ReaderMethod, unittest.TestCase):
    read_string = "    a"
    reader_method = "space"

    def runTest(self):
        """reading space just consumes spaces"""
        self.assertEqual(self.reader.current_char(), 'a')


class ReadSpaceAtEnd(_ReadTerm, unittest.TestCase):
    read_string = "    "
    reader_method = "space"

    def runTest(self):
        """reading spaces stops at end"""
        self.assert_reader_at_end()


class ReadNormalId(_ReadId, unittest.TestCase):
    """ids can contain letters"""
    read_string = "abcd"


class ReadUnderscoreId(_ReadId, unittest.TestCase):
    """ids can contain underscore"""
    read_string = '_abcd'


class ReadIdUnderscoreDigit(_ReadId, unittest.TestCase):
    """ids can contain underscore and digits"""
    read_string = 'a_1'


class ReadIdPunctExclaim(_ReadId, unittest.TestCase):
    """ids can contain exclamation points"""
    read_string = 'mutate!'


class ReadIdPunctQuestion(_ReadId, unittest.TestCase):
    """ids can contain question marks"""
    read_string = 'really?'


class ReadKeyword(_ReadTerm, unittest.TestCase):
    read_string = 'do:'
    reader_method = 'id_or_kw'
    term_type = 'keyword'


# noinspection PyPep8Naming
class ReadComment(_ReaderMethod):
    read_string = '"this is a comment"'
    reader_method = 'comment'

    def runTest(self):
        """read a plain old comment"""
        self.assert_reader_at_end()


class ReadCommentError(_ReadErrorTest, unittest.TestCase):
    read_string = '"this is a test'
    reader_method = 'comment'


class ReadString(_ReadTerm, unittest.TestCase):
    read_string = "'this is a test'"
    reader_method = 'string'
    term_type = 'string'
    term_value = read_string[1:-1]


class ReadStringError(_ReadErrorTest, unittest.TestCase):
    read_string = "'this is a test"
    reader_method = 'string'


class ReadBinarySelector1(_ReadBinsel, unittest.TestCase):
    """read a binary selector"""
    read_string = '+'


class ReadBinarySelector2(_ReadBinsel, unittest.TestCase):
    """read a binary selector"""
    read_string = '->'


class ReadBinarySelector3(_ReadBinsel, unittest.TestCase):
    """read a binary selector"""
    read_string = '==>'


class ReadInteger(_ReadTerm, unittest.TestCase):
    """read a simple integer"""
    read_string = '12345'
    reader_method = 'number'
    term_type = 'integer'
    term_value = 12345


class ReadAssign(_ReadTerm, unittest.TestCase):
    """read an assignment term"""
    read_string = ":="
    reader_method = "assignment_or_block_argument"
    term_type = 'assignment'
    term_value = None


class ReadBlockArgument(_ReadTerm, unittest.TestCase):
    """read a block argument"""
    read_string = ":a"
    reader_method = "assignment_or_block_argument"
    term_type = 'block_argument'
    term_value = 'a'


class ReadTermSkipSpace(_ReadTerm, unittest.TestCase):
    """reading a term skips leading space"""
    read_string = '    '
    term_type = 'eof'
    term_value = None


class ReadTermSkipSpaceComments(_ReadTerm, unittest.TestCase):
    """reading a term skips leading space"""
    read_string = '    " test comment "    '
    term_type = 'eof'
    term_value = None


class _ReadTerm1(_ReadTerm):
    term_shape = None

    def runTest(self):
        self.assertTrue(getattr(self.term, 'is_' + self.term_type))
        self.assert_term_value(self.term_value)
        if self.term_shape is not None:
            self.assertEqual(self.term.shape, self.term_shape)
        self.assertTrue(self.reader.read_term().is_eof)
        self.assert_reader_at_end()


class ReadTermId(_ReadTerm1, unittest.TestCase):
    read_string = '    abc123    '
    term_type = 'id'
    term_value = 'abc123'


class ReadTermKeyword(_ReadTerm1, unittest.TestCase):
    read_string = '    peek:    '
    term_type = 'keyword'
    term_value = 'peek:'


class ReadTermBinsel(_ReadTerm1, unittest.TestCase):
    read_string = '    ->    '
    term_type = 'binsel'
    term_value = '->'


class ReadTermNumber(_ReadTerm1, unittest.TestCase):
    read_string = '    12345    '
    term_type = 'integer'
    term_value = 12345


class ReadTermString(_ReadTerm1, unittest.TestCase):
    read_string = "    'test string'    "
    term_type = 'string'
    term_value = 'test string'


class ReadTermEmptyBlock(_ReadTerm1, unittest.TestCase):
    read_string = '    [    ]    '
    term_type = 'compound'
    term_value = []
    term_shape = '[]'


class ReadTermEmptyCurly(_ReadTerm1, unittest.TestCase):
    read_string = '    {    }    '
    term_type = 'compound'
    term_value = []
    term_shape = '{}'


class ReadTermEmptyParen(_ReadTerm1, unittest.TestCase):
    read_string = '    (    )    '
    term_type = 'compound'
    term_value = []
    term_shape = '()'


class ReadUnterminatedBlock(_ReadErrorTest, unittest.TestCase):
    read_string = '    [    '
    reader_method = 'term'


class ReadUnterminatedCurly(_ReadErrorTest, unittest.TestCase):
    read_string = '    {    '
    reader_method = 'term'


class ReadUnterminatedParen(_ReadErrorTest, unittest.TestCase):
    read_string = '    (    '
    reader_method = 'term'


class ReadWrongCloser(_ReadErrorTest, unittest.TestCase):
    read_string = '    ]    '
    reader_method = 'term'


class ReadBlock(_ReadTerm1, unittest.TestCase):
    read_string = '    [ 1 2 3 4 5 ]    '
    term_type = 'compound'
    term_shape = '[]'
    term_value = [1, 2, 3, 4, 5]


class ReadTermDot(_ReadTerm1, unittest.TestCase):
    read_string = '    .    '
    term_type = 'delimiter'
    term_value = '.'


class ReadTermSemicolon(_ReadTerm1, unittest.TestCase):
    read_string = '    ;    '
    term_type = 'delimiter'
    term_value = ';'


class ReadTermCarat(_ReadTerm1, unittest.TestCase):
    read_string = '    ^    '
    term_type = 'delimiter'
    term_value = '^'


class ReadTermAssignment(_ReadTerm1, unittest.TestCase):
    read_string = '    :=    '
    term_type = 'assignment'
    term_value = None


class ReaderBadAttr(unittest.TestCase):
    def setUp(self):
        from onyx.util.stream import Stream
        from onyx.reader import Reader

        self.reader = Reader(Stream.from_sequence([]))

    def runTest(self):
        with self.assertRaises(AttributeError):
            self.reader.not_found


class ReadCurrentClassEof(unittest.TestCase):
    def init_reader(self, s):
        from onyx.util.stream import Stream
        from onyx.reader import Reader

        stream = Stream.from_sequence(s)
        self.reader = Reader(stream)

    def assert_reader_at_end(self):
        if not self.reader.is_at_end():
            self.fail('reader is not at end')

    def setUp(self):
        self.init_reader('')

    def runTest(self):
        """reading at eof should produce the proper classification"""
        self.assertEqual({'eof'}, self.reader.current_class())
        self.assert_reader_at_end()


