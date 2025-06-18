from typing import TextIO, NamedTuple


from core.utils import nonstrict_assertion
from core.tests_abc import (
    Test as _Test,
    CreateTests,
)




class _Limit(NamedTuple):
    min_t:   int = 1
    max_t:   int = 4 * 10 ** 4

    min_n:   int = 1
    max_n:   int = 2 * 10 ** 5

    min_ai:  int = 1
    max_ai:  int = 10 ** 9


limit = _Limit()


class Test(_Test):
    n: int = None
    a: list[int] = None


    def __init__(self, raw_data: list) -> None:
        n, a = len(raw_data), raw_data
        a = list(a)


        for i in a:
            assert isinstance(i, int)
        
        self.a = a
        self.n = n


    @staticmethod
    @nonstrict_assertion
    def check(n, a) -> bool:
        assert isinstance(n, int)
        assert isinstance(a, list)

        assert limit.min_n <= n <= limit.max_n
        assert n == len(a)

        for i in a:
            assert isinstance(i, int)
            assert limit.min_ai <= i <= limit.max_ai
    

    def valid(self):
        return self.check(self.n, self.a)


    def save(self, file: TextIO) -> None:
        assert self.valid()

        print(self.n, file=file)
        print(*self.a, file=file)


print('WARNING: change limits and test classes')


ct = CreateTests(Test)
