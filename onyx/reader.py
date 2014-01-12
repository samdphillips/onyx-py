
import operator

class Term(object):
    is_id = False
    is_keyword = False
    is_string = True


class NamedTerm(Term):
    def __init__(self, name):
        self.name = name


class IdTerm(NamedTerm):
    is_id = True


class KeywordTerm(NamedTerm):
    is_keyword = True


class StringTerm(Term):
    is_string = True

    def __init__(self, value):
        self.value = value


class Classifier(object):
    def __init__(self):
        self._classifiers = []

    def add_func(self, func, names):
        self._classifiers.append((func, set(names)))

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


_default_classifier = Classifier()
_default_classifier.add_test('isspace', ['space'])
_default_classifier.add_test('isalpha', ['idchar'])
_default_classifier.add_test('isdigit', ['idchar', 'digit'])
_default_classifier.add_chars('_!?', ['idchar'])
_default_classifier.add_chars('"', ['comment'])
_default_classifier.add_chars("'", ['string'])


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

    def step(self):
        self._stream = self._stream.rest

    def is_space(self):
        return 'space' in self.current_class()

    def is_idchar(self):
        return 'idchar' in self.current_class()

    def is_comment(self):
        return 'comment' in self.current_class()

    def is_eof(self):
        return 'eof' in self.current_class()

    def is_string(self):
        return 'string' in self.current_class()


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
        return StringTerm(s)

    def read_id_or_kw(self):
        s = ''
        while self.is_idchar():
            s += self.current_char()
            self.step()

        if self.current_char() == ':':
            s += self.current_char()
            self.step()
            return KeywordTerm(s)
        return IdTerm(s)


