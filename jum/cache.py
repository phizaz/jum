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
    '''deprecated'''
    import hashlib
    m = hashlib.sha1()
    m.update(bytes)
    return m.digest()


def hash_xxhash(bytes) -> bytes:
    '''should be faster than sha1'''
    import xxhash
    m = xxhash.xxh64()
    m.update(bytes)
    return m.digest()


def to_bytes(string) -> bytes:
    return string.encode('utf8')


def func_dependescies(fn):
    raise NotImplementedError


def hash_func_body(fn) -> bytes:
    # switch to dill, might be more reliable ? 
    import dill
    return hash_xxhash(dill.dumps(fn))


def hash_func_name(name):
    return hash_xxhash(to_bytes(name))


def hash_arbitrary(thing):
    import dill
    bytes = dill.dumps(thing)
    return hash_xxhash(bytes)


def hash_thing(thing) -> bytes:
    return hash_arbitrary(thing)


def hash_argument(args, kwargs):
    res = hash_thing(b'')
    for each in args:
        res += hash_thing(each)
        res = hash_xxhash(res)
    for key, val in kwargs.items():
        res += hash_thing(key)
        res += hash_thing(val)
        res = hash_xxhash(res)
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


def cache(cache_dir: str, compresslevel: int = 2):
    import os.path
    cache_dir = os.path.join(cache_dir)

    def cache_wrap(fn):
        from functools import wraps

        @wraps(fn)
        def cached_fn(*args, **kwargs):
            fn_file = escape_path(func_file(fn, base_path=cache_dir))
            fn_name = func_name(fn)
            fn_hash = get_base64(hash_func_body(fn))
            arg_hash = get_base64(hash_argument(args=args, kwargs=kwargs))
            hit, val = cache_hit(
                fn_file=fn_file,
                fn_name=fn_name,
                fn_hash=fn_hash,
                arg_hash=arg_hash,
                store_path=cache_dir, compresslevel=compresslevel)
            if not hit:
                val = fn(*args, **kwargs)
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
