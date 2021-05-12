from multiprocessing import Process, Pipe

from .utils import callable_module


class Message():
    pass


class Request(Message):

    def __init__(self, *args, **kwargs):
        self.name = None
        self.call = False
        self.args = args
        self.kwargs = kwargs


class Response(Message):

    def __init__(self, data=None):
        self.data = data
        self.error = None


def run(*args, **kwargs):
    pipe = kwargs.pop('_pipe')
    target = kwargs.pop('_target')
    target = target(*args, **kwargs)
    while True:
        req = pipe.recv()
        if req.name is None:
            break
        res = Response()
        try:
            value = getattr(target, req.name)
            if req.call:
                res.data = value(*req.args, **req.kwargs)
            else:
                res.data = value
            pipe.send(res)
        except Exception as e:
            res.error = e
            pipe.send(res)
    pipe.close()


def close_pipe(pipe):
    # Send empty request to stop process
    pipe.send(Request())


class Attribute():

    def __init__(self, pipe, name):
        self.pipe = pipe
        self.name = name

    def get(self):
        req = Request()
        return self.send(req)

    def __call__(self, *args, **kwargs):
        req = Request(*args, **kwargs)
        req.call = True
        return self.send(req)

    def send(self, req):
        req.name = self.name
        pipe = self.pipe
        pipe.send(req)
        res = pipe.recv()
        if res.error:
            raise res.error
        return res.data


class Stub():

    def __init__(self, pipe):
        self._pipe = pipe

    def __getattr__(self, name):
        return Attribute(self._pipe, name)

    def __del__(self):
        close_pipe(self._pipe)


def make(target):

    class Class():

        def __init__(self, *args, **kwargs):
            local, remote = Pipe()
            kwargs = dict(_pipe=remote, _target=target, **kwargs)
            self._process = Process(target=run, args=args, kwargs=kwargs)
            self._stub = Stub(local)

        def __enter__(self):
            self._process.start()
            return self

        def __exit__(self, *args, **kwargs):
            del self._stub
            return self._process.join()

        def __getattr__(self, name):
            return getattr(self._stub, name)

    return Class


callable_module(make)
