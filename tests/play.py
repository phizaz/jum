from jum import cache


@cache(cache_dir='.jum-play')
def plus(a, b):
    print('output:', a, b)
    return a + b


print(plus(1, 2))
