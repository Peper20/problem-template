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

    min_a:   int = 1
    max_a:   int = 10 ** 9

    min_b:   int = 1
    max_b:   int = 10 ** 9


limit = _Limit()


class TestCase(_TestCase):
    a: int = None
    b: int = None


    def __init__(self, raw_data: tuple) -> None:
        a, b = raw_data


        assert isinstance(a, int)
        assert isinstance(b, int)
        
        self.a = a
        self.b = b


    @staticmethod
    @nonstrict_assertion
    def check(a, b) -> bool:
        assert isinstance(a, int)
        assert isinstance(b, int)

        assert limit.min_a <= a <= limit.max_a
        assert limit.min_b <= b <= limit.max_b
    

    def valid(self):
        return self.check(self.a, self.b)


    def save(self, file: TextIO) -> None:
        assert self.valid()

        print(self.a, self.b, file=file)


class Multytest(_Multytest[TestCase]):
    sum_a: int = 0
    sum_b: int = 0


    @staticmethod
    @nonstrict_assertion
    def check(t, sum_a, sum_b) -> bool:
        assert limit.min_t <= t <= limit.max_t        
        assert limit.min_a <= sum_a <= limit.max_a
        assert limit.min_b <= sum_b <= limit.max_b
    
    
    def valid(self) -> bool:
        return self.check(self.t, self.sum_a, self.sum_b)
    
    
    def can_add(self, test_case: TestCase) -> bool:
        return self.check(self.t + 1, self.sum_a + test_case.a, self.sum_b + test_case.b)


    def add(self, test_case: TestCase) -> None:
        self._test_cases.append(test_case)
        self.sum_a += test_case.a
        self.sum_b += test_case.b


print('WARNING: change limits and test classes')


ct = CreateMultytests(Multytest, TestCase)
