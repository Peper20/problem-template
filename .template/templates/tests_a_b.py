from typing import TextIO, NamedTuple


from core.utils import nonstrict_assertion
from core.tests_abc import (
    Test as _Test,
    CreateTests,
)




class _Limit(NamedTuple):
    min_t:   int = 1
    max_t:   int = 4 * 10 ** 4

    min_a:   int = 1
    max_a:   int = 10 ** 9

    min_b:   int = 1
    max_b:   int = 10 ** 9


limit = _Limit()


class TestCase(_Test):
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



print('WARNING: change limits and test classes')


ct = CreateTests(TestCase)
