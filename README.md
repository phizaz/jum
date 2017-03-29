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
```

### Features

1. It supports almost any kind of objects including numpy's ndarray which is its main use case.
2. Faster and lighter and **smaller** cache footprints than Joblib's Memory.
3. It supports file compression using Python's Gzip library.
4. It uses SHA1 as the main hashing algorithm, so it should be quite fast and universal, but not as fast as Python's native hash.

### To be improved

1. Take function dependencies (i.e. functions that this function calls) into account.
