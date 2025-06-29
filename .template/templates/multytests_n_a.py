from typing import TextIO, NamedTuple


from core.utils import nonstrict_assertion
from core.multytests_abc import (
    Multytest as _Multytest,
    TestCase as _TestCase,
    CreateMultytests,
)




class _Limit(NamedTuple):
    min_t:   int = 1
    max_t:   int = 4 * 10 ** 4

    min_n:   int = 1
    max_n:   int = 2 * 10 ** 5

    min_ai:  int = 1
    max_ai:  int = 10 ** 9


limit = _Limit()


class TestCase(_TestCase):
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


class Multytest(_Multytest[TestCase]):
    sum_n: int = 0


    @staticmethod
    @nonstrict_assertion
    def check(t, sum_n) -> bool:
        assert limit.min_t <= t <= limit.max_t        
        assert limit.min_n <= sum_n <= limit.max_n
    
    
    def valid(self) -> bool:
        return self.check(self.t, self.sum_n)
    
    
    def can_add(self, test_case: TestCase) -> bool:
        return self.check(self.t + 1, self.sum_n + test_case.n)


    def add(self, test_case: TestCase) -> None:
        self._test_cases.append(test_case)
        self.sum_n += test_case.n


print('WARNING: change limits, test classes and random seed base')


ct = CreateMultytests(Multytest, TestCase, random_seed_base='.template')
