
import operator

class Term(object):
    is_id      = False
    is_keyword = False
    is_string  = False
    is_binsel  = False

    def __init__(self, value, flag):
        self.value = value
        setattr(self, 'is_%s' % flag, True)


class Classifier(object):
    def __init__(self):
        self._classifiers = []

    def add_func(self, func, names):
        self._classifiers.append((func, names))

    def add_test(self, testname, names):
        self.add_func(operator.methodcaller(testname), names)

    def add_chars(self, chars, names):
        self.add_func(chars.__contains__, names)

    def classify(self, char):
        cls = set()
        for cl_func, cl_names in self._classifiers:
            if cl_func(char):
                cls.update(cl_names)
        return cls

    def init_class(self, char):
        for cl_func, cl_names in self._classifiers:
            if cl_func(char):
                return cl_names[0]


_default_classifier = Classifier()
_default_classifier.add_test('isspace', ['space'])
_default_classifier.add_chars('"', ['comment'])
_default_classifier.add_chars("'", ['string'])
_default_classifier.add_test('isalpha', ['idchar'])
_default_classifier.add_test('isdigit', ['digit', 'idchar'])
_default_classifier.add_chars("~!@%&*-+=|\\?/<>,", ['binsel'])
_default_classifier.add_chars('_!?', ['idchar'])


class ReadError(Exception):
    pass


class Reader(object):
    _classifier = _default_classifier

    def __init__(self, stream):
        self._stream = stream

    def is_at_end(self):
        return self._stream.is_empty

    def current_char(self):
        if self.is_at_end():
            return ''
        return self._stream.first

    def current_class(self):
        if self.is_at_end():
            return set(['eof'])
        return self._classifier.classify(self.current_char())

    def init_class(self):
        if self.is_at_end():
            return 'eof'
        return self._classifier.init_class(self.current_char())

    def step(self):
        self._stream = self._stream.rest

    def __getattr__(self, name):
        if name[:3] == 'is_':
            char_class = name[3:]
            def check_class():
                return char_class in self.current_class()
            setattr(self, name, check_class)
            return check_class
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, name))

    def read_space(self):
        while self.is_space():
            self.step()

    def read_comment(self):
        self.step()
        while not self.is_eof() and not self.is_comment():
            self.step()
        if self.is_eof():
            raise ReadError('eof encountered in comment')
        self.step()

    def read_string(self):
        s = ''
        self.step()
        while not self.is_eof() and not self.is_string():
            s += self.current_char()
            self.step()
        if self.is_eof():
            raise ReadError('eof encountered in string')
        self.step()
        return Term(s, 'string')

    def read_id_or_kw(self):
        s = ''
        while self.is_idchar():
            s += self.current_char()
            self.step()

        kind = 'id'
        if self.current_char() == ':':
            s += self.current_char()
            self.step()
            kind = 'keyword'
        return Term(s, kind)

    def read_binsel(self):
        s = ''
        while self.is_binsel():
            s += self.current_char()
            self.step()
        return Term(s, 'binsel')


