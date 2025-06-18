from typing import Any, Callable, Generator, Iterator, ParamSpec




P = ParamSpec('P')
def nonstrict_assertion(func: Callable[P, None]) -> Callable[P, bool]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
        try:
            func(*args, **kwargs)
        
        except AssertionError:
            return False
        
        else:
            return True
        
    return wrapper


def infinity_gen(gen: Callable[[], Generator[Any]]) -> Iterator[Any]:
    while True:
        yield from gen()
