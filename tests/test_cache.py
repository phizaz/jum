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


class TestCache(unittest.TestCase):
    def setUp(self):
        import shutil
        import os
        if os.path.exists('.jum-test'):
            shutil.rmtree('.jum-test')

    def test_cache_file_path(self):
        res = cache_file_path('test', 'fn_hash', 'arg_hash', 'store')
        print(res)
        self.assertEqual(res, 'store/test|fn_hash/arg_hash')

    def test_cache(self):
        fn = cache(cache_dir='.jum-test')(plus)
        res = fn(1, 2)
        print(res)


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

    def test_hash_nparrray(self):
        import numpy as np
        res = hash_thing(np.random.randint(0, 10, (1000, 1000)))
        print(res)
        self.assertTrue(isinstance(res, bytes))


class TestGetBase64(unittest.TestCase):
    def test_get_base64(self):
        res = get_base64(hash_thing(1))
        print(res)
        self.assertEqual(res, 'G8Grx8hzd9uIhiemo4iFzitA3do=')


class TestHashArgs(unittest.TestCase):
    def test_hash_arg(self):
        res = hash_argument((1, 2, 3), {'a': 10})
        print(res)
        self.assertTrue(isinstance(res, bytes))


class TestFuncName(unittest.TestCase):
    def test_func_name(self):
        res = func_name(plus)
        print(res)
        self.assertEqual(res, 'jum.tests.test_cache.plus')

    def test_func_file(self):
        res = func_file(plus)
        print(res)

    def test_func_full_name(self):
        res = func_full_name(plus, '.jum-test')
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

    def test_hash_func(self):
        a = hash_func(plus)
        print(a)
