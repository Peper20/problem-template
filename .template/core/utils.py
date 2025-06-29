from typing import Any, Callable, Generator, Iterator, ParamSpec, TypeVar
from random import getstate, setstate
from random import seed as setseed




P1 = ParamSpec('P1')
def nonstrict_assertion(func: Callable[P1, None]) -> Callable[P1, bool]:
    def wrapper(*args: P1.args, **kwargs: P1.kwargs) -> bool:
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


P2 = ParamSpec('P2')
R2 = TypeVar('R2')
def safe_seed_change(seed: str) -> Callable[[Callable[P2, R2]], Callable[P2, R2]]:
    def dec(func: Callable[P2, R2]) -> Callable[P2, R2]:
        def wrapper(*args: P2.args, **kwargs: P2.kwargs) -> R2:
            try:
                state = getstate()
                setseed(seed)
                return func(*args, **kwargs)
            finally:
                setstate(state)
        return wrapper
    return dec
