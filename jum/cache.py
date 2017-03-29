def func_file(fn):
    import inspect
    file = inspect.getfile(fn)
    return file


def func_name(fn):
    '''works only with picklable objects'''
    import inspect
    module = inspect.getmodule(fn)
    return module.__name__ + "." + fn.__name__


def escape_path(path: str):
    return path.replace('/', '|').replace('\\', '|')


def func_full_name(fn, base_path: str):
    import os.path
    file = os.path.relpath(func_file(fn),
                           base_path)
    name = func_name(fn)
    return '{path}|{name}'.format(
        path=escape_path(file),
        name=name)


def hash_sha1(bytes) -> bytes:
    import hashlib
    m = hashlib.sha1()
    m.update(bytes)
    return m.digest()


def to_bytes(string) -> bytes:
    return string.encode('utf8')


def func_dependescies(fn):
    raise NotImplementedError


def hash_func_body(fn):
    import inspect
    string = inspect.getsource(fn)
    bytes = to_bytes(string)
    return hash_sha1(bytes)


def hash_func_name(name):
    return hash_sha1(to_bytes(name))


def hash_func(fn):
    name_hash = hash_func_name(func_name(fn))
    body_hash = hash_func_body(fn)
    return hash_sha1(name_hash + body_hash)


def hash_arbitrary(thing):
    import dill
    bytes = dill.dumps(thing)
    return hash_sha1(bytes)


def hash_thing(thing) -> bytes:
    return hash_arbitrary(thing)


def hash_argument(args, kwargs):
    res = b''
    for each in args:
        res += hash_thing(each)
        res = hash_sha1(res)
    for key, val in kwargs.items():
        res += hash_thing(key)
        res += hash_thing(val)
        res = hash_sha1(res)
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


def cache_file_path(fn_name: str, fn_hash: str, arg_hash: str, store_path: str):
    import os.path
    first_dir = '{}|{}'.format(fn_name, fn_hash)
    file_path = os.path.join(store_path, first_dir, arg_hash)
    return file_path


def cache_hit(fn_name: str, fn_hash: str, arg_hash: str,
              store_path: str, compresslevel: int):
    import os.path
    file_path = cache_file_path(fn_name=fn_name,
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


def cache_save(fn_name: str, fn_hash: str, arg_hash: str,
               val, store_path: str, compresslevel: int):
    import os
    file_path = cache_file_path(fn_name=fn_name,
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
            fn_name = func_full_name(fn, base_path=cache_dir)
            fn_hash = get_base64(hash_func(fn))
            arg_hash = get_base64(hash_argument(args=args, kwargs=kwargs))
            hit, val = cache_hit(
                fn_name=fn_name,
                fn_hash=fn_hash,
                arg_hash=arg_hash,
                store_path=cache_dir, compresslevel=compresslevel)
            if not hit:
                val = fn(*args, **kwargs)
                cache_save(
                    fn_name=fn_name,
                    fn_hash=fn_hash,
                    arg_hash=arg_hash,
                    val=val,
                    store_path=cache_dir, compresslevel=compresslevel)
            return val

        return cached_fn

    return cache_wrap
