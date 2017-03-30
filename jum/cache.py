def func_file(fn, base_path: str):
    import inspect
    import os
    try:
        file_path = inspect.getfile(fn)
        file_rel_path = os.path.relpath(file_path,
                                        base_path)
        return file_rel_path
    except Exception:
        # some functions don't have filename (maybe?)
        file_path = '<undefined>'
        return file_path


def func_name(fn):
    '''works only with picklable objects'''
    import inspect
    module = inspect.getmodule(fn)
    return module.__name__ + "." + fn.__name__


def escape_path(path: str):
    return path.replace('/', '|').replace('\\', '|')


def hash_sha1(bytes) -> bytes:
    '''it not as fast, but it's so fast for the use'''
    import hashlib
    m = hashlib.sha1()
    m.update(bytes)
    return m.digest()


def hash_xxhash(bytes) -> bytes:
    '''should be faster than sha1, but subject to collisions, using this mainly for hashing ndarray'''
    import xxhash
    m = xxhash.xxh64()
    m.update(bytes)
    return m.digest()


def hash_bytes(bytes) -> bytes:
    '''we can say that the bottleneck is rather the "pickle" process'''
    return hash_sha1(bytes)


def to_bytes(string) -> bytes:
    return string.encode('utf8')


def func_dependescies(fn):
    raise NotImplementedError


def hash_func_body(fn) -> bytes:
    # switch to dill, might be more reliable ? 
    import dill
    return hash_bytes(dill.dumps(fn))


def hash_func_name(name):
    return hash_bytes(to_bytes(name))


def hash_ndarray_contiguous(ndarray):
    '''hash using direct xxhash but it works only on contiguous np array'''
    import numpy as np
    assert isinstance(ndarray, np.ndarray), 'this works only with ndarray'
    assert is_contiguous(ndarray), 'this works only with contiguous arrays'
    return hash_xxhash(ndarray)


def is_contiguous(ndarray):
    try:
        return ndarray.flags['C_CONTIGUOUS'] is True
    except Exception:
        return False


def hash_ndarray_arbitrary(ndarray):
    '''pickel < dill < ndarray.tobytes() = ndarray.tostring()'''
    import pickle
    return hash_xxhash(pickle.dumps(ndarray))


def hash_arbitrary(thing):
    import dill
    bytes = dill.dumps(thing)
    return hash_bytes(bytes)


def hash_thing(thing) -> bytes:
    import numpy as np
    # special case to improve performance (something like 10x)
    if isinstance(thing, np.ndarray):
        if is_contiguous(thing):
            return hash_ndarray_contiguous(thing)
        else:
            return hash_ndarray_arbitrary(thing)

    return hash_arbitrary(thing)


def hash_argument(args, kwargs, verbose: bool = False):
    from .profiler import TimeElapsed
    res = hash_thing(b'')
    for each in args:
        with TimeElapsed('dill-ing an arg', verbose=verbose):
            res += hash_thing(each)
        with TimeElapsed('hashing an arg', verbose=verbose):
            res = hash_bytes(res)
    for key, val in kwargs.items():
        with TimeElapsed('dill-ing an arg', verbose=verbose):
            res += hash_thing(key)
            res += hash_thing(val)
        with TimeElapsed('hashing an arg', verbose=verbose):
            res = hash_bytes(res)
    return res


def get_base64(bytes: bytes):
    import base64
    return base64.urlsafe_b64encode(bytes).decode('utf-8')


def load_cache_file(file, compresslevel: int):
    import dill
    import gzip
    with gzip.open(file, 'rb', compresslevel=compresslevel) as handle:
        return dill.load(handle)


def save_cache_file(file, thing, compresslevel: int):
    import dill
    import gzip
    with gzip.open(file, 'wb', compresslevel=compresslevel) as handle:
        dill.dump(thing, handle)


def cache_file_path(fn_file: str, fn_name: str, fn_hash: str, arg_hash: str, store_path: str):
    import os.path
    first_dir = fn_file
    second_dir = fn_name
    third_dir = fn_hash
    file_path = os.path.join(store_path,
                             first_dir,
                             second_dir,
                             third_dir,
                             arg_hash)
    return file_path


def cache_hit(fn_file: str, fn_name: str, fn_hash: str, arg_hash: str,
              store_path: str, compresslevel: int):
    import os.path
    file_path = cache_file_path(fn_file=fn_file,
                                fn_name=fn_name,
                                fn_hash=fn_hash,
                                arg_hash=arg_hash,
                                store_path=store_path)
    if not os.path.exists(file_path):
        return False, None
    try:
        val = load_cache_file(file_path, compresslevel=compresslevel)
        return True, val
    except Exception:
        # if has problem with reading the cache file
        return False, None


def cache_save(fn_file: str, fn_name: str, fn_hash: str, arg_hash: str,
               val, store_path: str, compresslevel: int):
    import os
    file_path = cache_file_path(fn_file=fn_file,
                                fn_name=fn_name,
                                fn_hash=fn_hash,
                                arg_hash=arg_hash,
                                store_path=store_path)
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    save_cache_file(file_path, thing=val, compresslevel=compresslevel)


def cache(cache_dir: str, compresslevel: int = 2, verbose: str = ''):
    '''
    :param cache_dir: 
    :param compresslevel: 
    :param verbose: None, 'v', 'vv'
    :return: 
    '''
    import os.path
    cache_dir = os.path.join(cache_dir)

    def cache_wrap(fn):
        from functools import wraps
        from .profiler import TimeElapsed

        @wraps(fn)
        def cached_fn(*args, **kwargs):
            with TimeElapsed('hashing functions and arguments', verbose='v' in verbose):
                fn_file = escape_path(func_file(fn, base_path=cache_dir))
                fn_name = func_name(fn)
                fn_hash = get_base64(hash_func_body(fn))
                arg_hash = get_base64(
                    hash_argument(args=args, kwargs=kwargs,
                                  verbose='vv' in verbose))
            with TimeElapsed('cache retrieval', verbose='v' in verbose):
                hit, val = cache_hit(
                    fn_file=fn_file,
                    fn_name=fn_name,
                    fn_hash=fn_hash,
                    arg_hash=arg_hash,
                    store_path=cache_dir, compresslevel=compresslevel)
            if not hit:
                with TimeElapsed('preforming real execution', verbose='v' in verbose):
                    val = fn(*args, **kwargs)
                with TimeElapsed('cache save', verbose='v' in verbose):
                    cache_save(
                        fn_file=fn_file,
                        fn_name=fn_name,
                        fn_hash=fn_hash,
                        arg_hash=arg_hash,
                        val=val,
                        store_path=cache_dir, compresslevel=compresslevel)
            return val

        return cached_fn

    return cache_wrap
