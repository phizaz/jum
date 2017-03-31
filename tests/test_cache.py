import unittest
from jum.cache import *


def plus(a, b):
    print('plus')
    return a + b


def multi(a, b):
    print('multi')
    return a * b


def sum(objects):
    a = 0
    for each in objects:
        a += each
    return a


def large_output():
    import numpy as np
    return np.random.randint(0, 10, (10000, 1000))


def large_input(args):
    return


class TestCache(unittest.TestCase):
    def setUp(self):
        import shutil
        import os
        if os.path.exists('.jum-test'):
            shutil.rmtree('.jum-test')

    def test_cache_file_path(self):
        res = cache_file_path('file', 'test', 'fn_hash', 'arg_hash', 'store')
        print(res)
        self.assertEqual(res, 'store/file/test/fn_hash/arg_hash')

    def test_cache(self):
        fn = cache(cache_dir='.jum-test')(plus)
        res = fn(1, 2)
        print(res)
        res = fn(1, 2)
        print(res)
        res = fn(2, 2)
        print(res)

    def test_cache_on_large_output(self):
        fn = cache(cache_dir='.jum-test', verbose='v')(large_output)
        fn()
        fn()

    def test_cache_on_large_input(self):
        import numpy as np
        a = np.random.randint(0, 10, (100000, 1000))
        fn = cache(cache_dir='.jum-test', verbose='vv')(large_input)
        fn(a)
        fn(a)


class TestHashObject(unittest.TestCase):
    def test_hash_int(self):
        res = hash_thing(1)
        print(res)
        self.assertTrue(isinstance(res, bytes))

    def test_hash_string(self):
        res = hash_thing('aoeu')
        print(res)
        self.assertTrue(isinstance(res, bytes))

    def test_hash_list(self):
        res = hash_thing([1, 2, 3])
        print(res)
        self.assertTrue(isinstance(res, bytes))

    def test_hash_ndarray(self):
        import numpy as np
        from profiler import TimeElapsed

        a = np.random.randint(0, 10, (1000, 1000))
        b = np.random.randint(0, 10, (10000, 1000)).T
        c = np.random.randint(0, 10, (30000, 1000)).T  # after transposed ndarray will not be contiguous anymore
        with TimeElapsed('1000x1000'):
            res = hash_thing(a)
            print(res)
            self.assertTrue(isinstance(res, bytes))
        with TimeElapsed('10000x1000'):
            res = hash_thing(b)
            print(res)
            self.assertTrue(isinstance(res, bytes))
        with TimeElapsed('30000x1000'):
            res = hash_thing(c)
            print(res)
            self.assertTrue(isinstance(res, bytes))


class TestGetBase64(unittest.TestCase):
    def test_get_base64(self):
        res = get_base64(hash_thing(1))
        print(res)
        self.assertEqual(res, 'G8Grx8hzd9uIhiemo4iFzitA3do=')


class TestHashArgs(unittest.TestCase):
    def test_hash_arg_no_arg(self):
        res = hash_argument(args=(), kwargs={})
        print(res)
        self.assertEqual(res, b'\xd4\xe8\x8a\xbb\x97:*\xef')

    def test_hash_arg(self):
        res = hash_argument((1, 2, 3), {'a': 10})
        print(res)
        self.assertTrue(isinstance(res, bytes))

    def test_hash_very_large_arg(self):
        import numpy as np
        from profiler import TimeElapsed
        a = np.random.randint(0, 10, (10000, 1000))
        b = np.random.randint(0, 10, (10000, 1000))
        c = np.random.randint(0, 10, (10000, 1000))
        d = np.random.randint(0, 10, (10000, 1000))
        with TimeElapsed(name='hash-args'):
            hash_argument(args=(a, b, c, d), kwargs={})


class TestFuncName(unittest.TestCase):
    def test_func_name(self):
        res = func_name(plus)
        print(res)
        self.assertEqual(res, 'jum.tests.test_cache.plus')

    def test_func_file(self):
        res = func_file(plus, base_path='.jum-test')
        print(res)


class TestHashNDArray(unittest.TestCase):
    import numpy as np
    arr = np.random.randint(0, 10, (50000, 1000))
    arr_t = np.random.randint(0, 10, (50000, 1000)).T

    def test_hash_by_xxhash(self):
        from profiler import TimeElapsed

        with TimeElapsed('xxhash'):
            res = hash_xxhash(self.arr)
            print(res)

    def test_hash_transpose(self):
        from profiler import TimeElapsed

        with TimeElapsed('xxhash'):
            res = hash_xxhash(self.arr_t.T)
            print(res)

    def test_hash_by_pickle(self):
        from profiler import TimeElapsed
        with TimeElapsed('pickle + xxhash'):
            import pickle
            res = hash_xxhash(pickle.dumps(self.arr))
            print(res)

    def test_hash_by_dill(self):
        from profiler import TimeElapsed
        with TimeElapsed('dill + xxhash'):
            import dill
            res = hash_xxhash(dill.dumps(self.arr))
            print(res)

    def test_hash_by_flatten(self):
        from profiler import TimeElapsed
        with TimeElapsed('flatten + xxhash'):
            res = hash_xxhash(self.arr.flatten())
            print(res)


class TestSHA1Hash(unittest.TestCase):
    def test_sha1_hash(self):
        res = hash_sha1(to_bytes('test'))
        print(res)


class TestHashFuncBody(unittest.TestCase):
    def test_hash_func_body(self):
        res = hash_func_body(plus)
        print(res)
        res = hash_func_body(multi)
        print(res)
        res = hash_func_body(sum)
        print(res)
