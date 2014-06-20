class Foo(object):
    def __init__(self):
        pass

    @property
    def p(self):
        return 'Foo property'


class FooProxy(object):
    def __init__(self, foo_instance, recursive=False):
        self._instance = foo_instance
        self._recursive = recursive

    def __getattr__(self, item):
        return getattr(self._instance, item)

    @property
    def p(self):
        if self._recursive:
            return FooProxy(Foo()).p

        return 'Decorated ' + self._instance.p
#
#
# foo = Foo()
# print(foo.p)
#
# fooProxy = FooProxy(foo)
# print(fooProxy.p)
#
# fooProxyRecursive = FooProxy(foo, recursive=True)
# print(fooProxyRecursive.p)
