

import unittest


class TestReader(unittest.TestCase):
    def init_reader(self, s):
        from onyx.util.stream import Stream
        from onyx.reader import Reader, ReadError
        stream = Stream.from_sequence(s)
        self.reader = Reader(stream)
        self.ReadError = ReadError

    def assert_at_end(self):
        if not self.reader.is_at_end():
            self.fail('reader is not at end')

    def test_classify_eof(self):
        "reading at eof should produce the proper classification"
        self.init_reader('')
        self.assertEqual(set(['eof']), self.reader.current_class())
        self.assert_at_end()

    def test_read_space_at_end(self):
        "reading spaces stops at end"
        self.init_reader('    ')
        self.reader.read_space()
        self.assert_at_end()

    def test_read_space_not_at_end(self):
        "reading space just consumes spaces"
        self.init_reader('    a')
        self.reader.read_space()
        self.assertEqual(self.reader.current_char(), 'a')

    def test_read_id(self):
        "ids can contain letters"
        self.init_reader('abcd')
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.value, 'abcd')
        self.assert_at_end()

    def test_read_id_underscore(self):
        "ids can contain underscore"
        self.init_reader('_abcd')
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.value, '_abcd')
        self.assert_at_end()

    def test_read_id_underscore_digit(self):
        "ids can contain underscore and digits"
        self.init_reader('a_1')
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.value, 'a_1')
        self.assert_at_end()

    def test_read_id_punct_exclaim(self):
        "ids can contain exclamation points"
        self.init_reader("mutate!")
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.value, 'mutate!')
        self.assert_at_end()

    def test_read_id_punct_question(self):
        "ids can contain question marks"
        self.init_reader("really?")
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.value, 'really?')
        self.assert_at_end()

    def test_read_keyword(self):
        "a keyword is an identifier with a ':' at the end"
        self.init_reader("do:")
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_keyword)
        self.assertEqual(t.value, 'do:')
        self.assert_at_end()

    def test_read_comments(self):
        "read a plain old comment"
        self.init_reader('"this is a comment"')
        self.reader.read_comment()
        self.assert_at_end()

    def test_read_comment_error(self):
        "an improperly terminated comment is bad"
        self.init_reader('"this is a test')
        with self.assertRaises(self.ReadError):
            self.reader.read_comment()

    def test_reader_string(self):
        "read a string"
        self.init_reader("'this is a test'")
        t = self.reader.read_string()
        self.assertTrue(t.is_string)
        self.assertEqual(t.value, "this is a test")
        self.assert_at_end()

    def test_read_string_error(self):
        "an improperly terminated string is bad"
        self.init_reader("'this is a test")
        with self.assertRaises(self.ReadError):
            self.reader.read_string()

