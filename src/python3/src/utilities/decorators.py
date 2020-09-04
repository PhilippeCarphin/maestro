import json

def cache(function):
    """
    later versions of Python have 'functools.cache'
    """
    memo = {}

    def wrapper(*args, **kwargs):
        key=(str(args),json.dumps(kwargs,sort_keys=1))
        if key in memo:
            return memo[key]
        else:
            rv = function(*args,**kwargs)
            memo[key] = rv
            return rv
    return wrapper