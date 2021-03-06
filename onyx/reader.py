import operator

from onyx.term import Term


class Classifier(object):
    def __init__(self):
        self._classifiers = []

    def add_func(self, func, names):
        self._classifiers.append((func, names))

    def add_test(self, test_name, names):
        self.add_func(operator.methodcaller(test_name), names)

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
_default_classifier.add_chars(":", ['assignment'])
_default_classifier.add_test('isalpha', ['idchar'])
_default_classifier.add_test('isdigit', ['digit', 'idchar'])
_default_classifier.add_chars("~!@%&*-+=|\\?/<>,", ['binsel'])
_default_classifier.add_chars(".;^", ['delimiter'])
_default_classifier.add_chars('_!?', ['idchar'])
_default_classifier.add_chars('[{(', ['opener'])
_default_classifier.add_chars(']})', ['closer'])


class ReadError(Exception):
    pass


class Reader(object):
    _classifier = _default_classifier
    _closers = {'[': ']', '(': ')', '{': '}'}

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
            return {'eof'}
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

    def skip_spaces(self):
        init_class = self.init_class()

        while True:
            if init_class == 'space':
                self.read_space()
            elif init_class == 'comment':
                self.read_comment()
            else:
                return init_class
            init_class = self.init_class()

    def __iter__(self):
        return self

    def next(self):
        term = self.read_term()
        if term.is_eof:
            raise StopIteration
        return term

    def read_term(self):
        init_class = self.skip_spaces()

        if init_class == 'eof':
            return Term(None, 'eof')
        elif init_class == 'idchar':
            return self.read_id_or_kw()
        elif init_class == 'binsel':
            return self.read_binsel()
        elif init_class == 'digit':
            return self.read_number()
        elif init_class == 'string':
            return self.read_string()
        elif init_class == 'delimiter':
            return self.read_delimiter()
        elif init_class == 'assignment':
            return self.read_assignment_or_block_argument()
        elif init_class == 'opener':
            return self.read_compound()
        elif init_class == 'closer':
            raise ReadError('unbalanced term: %s' % repr(self.current_char()))

        raise ReadError('Unknown character: %s (%s)' %
                        (repr(self.current_char()), init_class))

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

    def read_delimiter(self):
        c = self.current_char()
        self.step()
        return Term(c, 'delimiter')

    def read_number(self):
        s = ''
        while self.is_digit():
            s += self.current_char()
            self.step()
        return Term(int(s), 'integer')

    def scan_id_or_kw(self):
        s = ''
        while self.is_idchar():
            s += self.current_char()
            self.step()
        kind = 'id'
        if self.current_char() == ':':
            s += self.current_char()
            self.step()
            kind = 'keyword'
        return s, kind

    def read_id_or_kw(self):
        s, kind = self.scan_id_or_kw()
        return Term(s, kind)

    def read_binsel(self):
        s = ''
        while self.is_binsel():
            s += self.current_char()
            self.step()
        return Term(s, 'binsel')

    def read_assignment_or_block_argument(self):
        self.step()
        if self.current_char() == '=':
            term = Term(None, 'assignment')
            self.step()
        elif self.is_idchar():
            value, kind = self.scan_id_or_kw()
            if kind == 'keyword':
                raise ReadError('expected id not keyword')
            term = Term(value, 'block_argument')
        else:
            raise ReadError('Unexpected character: %s (%s)' %
                            (repr(self.current_char()), self.init_class()))
        return term

    def read_compound(self):
        start = self.current_char()
        end = self._closers[start]
        self.step()

        terms = []
        self.skip_spaces()
        while self.current_char() != end:
            if self.is_eof():
                raise ReadError('eof encountered in compound (%s)' %
                                repr(start))
            t = self.read_term()
            terms.append(t)
            self.skip_spaces()

        self.step()
        return Term(terms, 'compound', start+end)

