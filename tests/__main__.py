

import os.path

from coverage import coverage
from unittest import defaultTestLoader as test_loader, \
                     TestSuite, \
                     TextTestResult, \
                     TextTestRunner


class PluggableTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity, plugins=None):
        super().__init__(stream, descriptions, verbosity)
        if plugins is None:
            plugins = []
        self.plugins = plugins

    def startTestRun(self):
        for p in self.plugins:
            p.begin()

    def stopTestRun(self):
        for p in self.plugins:
            p.finish()

    def startTest(self, test):
        super().startTest(test)
        for p in self.plugins:
            p.start_test(test)

    def stopTest(self, test):
        super().stopTest(test)
        for p in self.plugins:
            p.stop_test(test)

    def report(self):
        for p in self.plugins:
            p.report()


def results_with_plugins(plugins):
    def make_results(stream, descriptions, verbosity):
        return PluggableTestResult(
                stream, descriptions, verbosity, plugins)
    return make_results


class TestPlugin(object):
    def begin(self):
        pass

    def finish(self):
        pass

    def start_test(self, test):
        pass

    def stop_test(self, test):
        pass

    def report(self):
        pass


class Coverage(TestPlugin):
    def __init__(self, source=None):
        self._cov = coverage(source=source)

    def start_test(self, test):
        self._cov.start()

    def stop_test(self, test):
        self._cov.stop()

    def report(self):
        self._cov.report()

def load_failed_tests():
    tests = None
    if os.path.exists('.test_failures'):
        with open('.test_failures', 'r') as failfile:
            names = [s.strip() for s in failfile]
            tests = test_loader.loadTestsFromNames(names)
    if tests is None or tests.countTestCases() == 0:
        tests = load_all_tests()
    return tests

def load_all_tests():
    return test_loader.discover('tests', top_level_dir='.')

if __name__ == '__main__':
    import sys

    from itertools import chain
    from string import Template

    if len(sys.argv) > 1 and sys.argv[1] == '-f':
        tests = load_failed_tests()
    else:
        tests = load_all_tests()

    plugins = [Coverage(source=['onyx'])]
    runner = TextTestRunner(stream=sys.stdout,
                            verbosity=2,
                            resultclass=results_with_plugins(plugins))
    results = runner.run(tests)
    results.report()

    with open('.test_failures', 'w') as failfile:
        t = Template('$module.$class.$method')
        for failure, message in chain(results.failures, results.errors):
            d ={'module': failure.__class__.__module__,
                'class':  failure.__class__.__name__,
                'method': failure._testMethodName}
            print(t.substitute(d), file=failfile)


