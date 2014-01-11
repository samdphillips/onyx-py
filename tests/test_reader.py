

import unittest


class TestReader(unittest.TestCase):
    def init_reader(self, s):
        from onyx.util.stream import Stream
        from onyx.reader import Reader
        stream = Stream.from_sequence(s)
        self.reader = Reader(stream)

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
        self.assertEqual(t.name, 'abcd')

    def test_read_id_underscore(self):
        "ids can contain underscore"
        self.init_reader('_abcd')
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.name, '_abcd')

    def test_read_id_underscore_digit(self):
        "ids can contain underscore and digits"
        self.init_reader('a_1')
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.name, 'a_1')

    def test_read_id_punct_exclaim(self):
        "ids can contain exclamation points"
        self.init_reader("mutate!")
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.name, 'mutate!')

    def test_read_id_punct_question(self):
        "ids can contain question marks"
        self.init_reader("really?")
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_id)
        self.assertEqual(t.name, 'really?')

    def test_read_keyword(self):
        "a keyword is an identifier with a ':' at the end"
        self.init_reader("do:")
        t = self.reader.read_id_or_kw()
        self.assertTrue(t.is_keyword)
        self.assertEqual(t.name, 'do:')
        self.assert_at_end()

