

import unittest


class IteratorStreamTests(unittest.TestCase):
    def setUp(self):
        from onyx.util.stream import Stream
        self.stream = Stream.from_sequence(range(10))

    def test_first(self):
        self.assertEqual(self.stream.first, 0)
        self.assertEqual(self.stream.first, 0)

    def test_rest_first(self):
        self.assertEqual(self.stream.rest.first, 1)
        self.assertEqual(self.stream.rest.first, 1)

    def test_rest_rest_first(self):
        self.assertEqual(self.stream.rest.rest.first, 2)
        self.assertEqual(self.stream.rest.rest.first, 2)

    def test_is_empty(self):
        self.assertFalse(self.stream.is_empty)

    def test_all_read_is_empty(self):
        s = self.stream
        for n in range(10):
            self.assertEqual(s.first, n)
            s = s.rest
        self.assertTrue(s.is_empty)


class EmptyStreamTests(unittest.TestCase):
    def setUp(self):
        from onyx.util.stream import Stream
        self.stream = Stream.from_sequence([])

    def test_is_empty(self):
        self.assertTrue(self.stream.is_empty)

    def test_first(self):
        from onyx.util.stream import EmptyStreamError
        with self.assertRaises(EmptyStreamError):
            self.stream.first

    def test_rest(self):
        from onyx.util.stream import EmptyStreamError
        with self.assertRaises(EmptyStreamError):
            self.stream.rest


class IteratorTests(unittest.TestCase):
    def setUp(self):
        from onyx.util.stream import Stream
        self.stream = Stream.from_sequence(range(10))

    def test_iterate_over_values(self):
        for x, y in zip(self.stream, range(10)):
            self.assertEqual(x, y)
        self.assertEqual(self.stream.first, 0)


class CharIoIteratorTests(unittest.TestCase):
    def setUp(self):
        from io import StringIO
        from onyx.util.stream import CharIoIterator
        sio = StringIO(u'0123456789')
        self.cio_iter = CharIoIterator(sio)

    def test_iteration(self):
        s = '0123456789'
        cio_iter = self.cio_iter
        for c1, c2 in zip(cio_iter, s):
            self.assertEqual(c1, c2)
        

