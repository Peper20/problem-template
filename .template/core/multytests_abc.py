from typing import Any, Callable, Generator, TextIO, Type
from abc import ABC, abstractmethod
from time import perf_counter
from pathlib import Path


from ._files import get_group_and_number, get_tests_names, ROOT_TESTS_DIR
from .utils import infinity_gen
from .tests_abc import Test as TestCase




class Multytest[TC: TestCase](ABC):
    _test_cases: list[TC] = None


    def __init__(self, test_cases: list[TC] = None) -> None:
        if test_cases is None:
            test_cases = []
        
        self._test_cases = list(test_cases)


    def __len__(self) -> int:
        return len(self._test_cases)

    @property
    def t(self) -> int:
        return len(self)


    @staticmethod
    @abstractmethod
    def check(self) -> bool:
        raise NotImplementedError


    @abstractmethod
    def valid(self) -> bool:
        raise NotImplemented


    @abstractmethod
    def can_add(self, test_case: TC) -> bool:
        raise NotImplementedError


    def add(self, test_case: TC) -> None:
        self._test_cases.append(test_case)
    

    def save(self, file: TextIO) -> None:
        assert self.valid()

        print(self.t, file=file)
        for test_case in self._test_cases:
            test_case.save(file)


class CreateMultytests:
    multytest_cls: Type[Multytest] = None
    test_case_cls: Type[TestCase] = None


    def __init__(self, multytest_cls: Type[Multytest], test_case_cls: Type[TestCase]) -> None:
        self.multytest_cls = multytest_cls
        self.test_case_cls = test_case_cls
    

    def _save(self, tests: list[Multytest], test_group: int):
        old_tests: list[Path] = []
        for test_name in get_tests_names():
            if get_group_and_number(test_name)[0] == test_group:
                old_tests.append(ROOT_TESTS_DIR / test_name)
        
        if old_tests:
            for old_test in old_tests:
                old_test.unlink()
            
            print(f'gen:test group {test_group}: removed old tests ({len(old_tests)} total)')
        
        else:
            print(f'gen:test group {test_group}: old tests has not detected')

        for test_number, test in enumerate(tests):
            with open(ROOT_TESTS_DIR / Path(f'{test_group:02}_{test_number:02}.txt'), 'w') as f:
                test.save(f)


    def save(self, test_group: int, limit: int = 10, cycle: bool = False) -> Callable:
        ROOT_TESTS_DIR.mkdir(parents=True, exist_ok=True)
        tests: list[Multytest] = [self.multytest_cls()]
        def dec(gen: Callable[[], Generator[Any]]) -> Callable[[], Generator[Any]]:
            start_time: float = perf_counter()

            for test_case in map(self.test_case_cls, infinity_gen(gen) if cycle else gen()):
                assert test_case.valid()

                if not tests[-1].can_add(test_case):
                    if len(tests) == limit:
                        break

                    tests.append(self.multytest_cls())
                
                tests[-1].add(test_case)
            
            self._save(tests, test_group)
            end_time: float = perf_counter()

            print(f'gen:test group {test_group}: created in {end_time - start_time:.3f}s ({len(tests)} tests and {sum(map(len, tests))} test cases total)')

            return gen
        return dec


