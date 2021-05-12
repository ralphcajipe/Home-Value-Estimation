import inspect


def callable_module(fn):
    caller = inspect.stack()[1][0]
    module = inspect.getmodule(caller)

    class Module(module.__class__):

        def __call__(self, *args, **kwargs):
            return fn(*args, **kwargs)

    module.__class__ = Module
