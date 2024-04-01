import time
from itertools import islice


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print(
            "{:s} function took {:.3f} ms".format(f.__name__, (time2 - time1) * 1000.0)
        )
        return ret
    return wrap


@timing
def use_generator():
    return list(islice((time.sleep(x) for x in range(5)), 1))


@timing
def use_list():
    return list(islice([time.sleep(x) for x in range(5)], 1))


print(use_generator())
# use_generator function took 0.048 ms
# [None]
print(use_list())
# use_list function took 3003.090 ms
# [None]
print(type((time.sleep(x) for x in range(3))))
# <class 'generator'>
print(type([time.sleep(x) for x in range(3)]))
# <class 'list'>
