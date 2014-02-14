

import unittest


class SimplePatternTests(unittest.TestCase):
    def test_any_id_pattern(self):
        from onyx.pattern     import SimplePattern
        from onyx.reader      import Term
        from onyx.util.stream import Stream

        pat = SimplePattern('identifier')
        s = Stream.from_sequence([Term('a', 'identifier')])
        match = pat.match(s)

        self.assertTrue(match.is_success)
        self.assertFalse(match.is_failure)
        self.assertTrue(match.after_stream.is_empty)

    def test_no_matching_pattern(self):
        from onyx.pattern     import SimplePattern
        from onyx.reader      import Term
        from onyx.util.stream import Stream

        pat = SimplePattern('integer')
        s = Stream.from_sequence([Term('a', 'identifier')])
        match = pat.match(s)

        self.assertFalse(match.is_success)
        self.assertTrue(match.is_failure)

    def test_binding_pattern(self):
        from onyx.pattern     import SimplePattern
        from onyx.reader      import Term
        from onyx.util.stream import Stream

        pat = SimplePattern('identifier', bind='name')
        t = Term('a', 'identifier')
        s = Stream.from_sequence([t])
        match = pat.match(s)

        self.assertTrue(match.is_success)
        self.assertFalse(match.is_failure)
        self.assertEqual(t, match.binding_value('name'))

    def test_value_pattern(self):
        from onyx.pattern     import SimplePattern
        from onyx.reader      import Term
        from onyx.util.stream import Stream

        pat = SimplePattern('identifier', value='class')
        s = Stream.from_sequence([Term('class', 'identifier')])
        match = pat.match(s)

        self.assertTrue(match.is_success)
        self.assertFalse(match.is_failure)

    def test_wrong_value_pattern(self):
        from onyx.pattern     import SimplePattern
        from onyx.reader      import Term
        from onyx.util.stream import Stream

        pat = SimplePattern('identifier', value='class')
        s = Stream.from_sequence([Term('a', 'identifier')])
        match = pat.match(s)

        self.assertTrue(match.is_failure)
        self.assertFalse(match.is_success)
