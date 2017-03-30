# Jum

*"jum" means "remember" in Thai*

*An alternative to Joblib's Memory to cache python function in-file*

It uses [**dill**](https://github.com/uqfoundation/dill) package to **pickle** objects and also to help hashing function arguments, so it supports any kind of objects as long as dill supports it.

## Use cases

```
import jum

@jum.cache(cache_dir='.jum')
def a_long_running_function(array):
    ... do some cpu intensive things ...
    return value


import numpy as np
a_long_running_fn(<some_large_np_array>)

## to configure compression level (default 2)
@jum.cache(cache_dir='.jum', compresslevel=<0-9>)
```

## Installation

```
pip install jum
```

### Features

1. It supports almost any kind of objects including numpy's ndarray which is its main use case.
2. Faster and lighter and **smaller** cache footprints than Joblib's Memory.
3. It supports file compression using Python's Gzip library.
4. It uses SHA1 as the main hashing algorithm, to provide the large 256 bit hashing space.
5. It now uses xxhash to hash the ndarray (specifically) for speed boost.

### To be improved

- [x] use dill to hash the function body instead of the function code, because some function's code cannot be retrieve, esp. in the case of python console.
- [x] function file path might not work in case of python console, put some default values for it.
- [x] using some faster hash, xxhash, (update) I have profiled it, found that the slowest, bottleneck, is rather the "pickle" process not hash itself.
- [x] favor the slower hash (very negligible) to the safer for collisions.
- [x] by directing hash the ndarray via xxhash, ndarray hashing performance is increased ten-fold.
- [x] add a verbose mode, showing the time elapsed for hashing (mainly the overhead of caching).
- [ ] Take function dependencies (i.e. functions that this function calls) into account.

### Known Problem

- [x] null arg problem where a function as no argument.
- [x] `ValueError: ndarray is not C-contiguous` happens with some specific ndarray, not all ndarrays can be fed to xxhash directly: be treated by pickle for now.

