import timeit as it


def timeit(func):
    def wrapper(self, *args, **kwargs):
        ts = it.time.time()
        result = func(self, *args, **kwargs)
        te = it.time.time()
        print('%r  %2.2f ms' % \
                  (func.__name__, (te - ts) * 1000))
    return wrapper
