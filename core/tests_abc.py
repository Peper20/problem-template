from typing import Any, Callable, Generator, TextIO, Type
from abc import ABC, abstractmethod
from time import perf_counter
from pathlib import Path



from .utils import infinity_gen
from ._files import get_group_and_number, get_tests_names, ROOT_TESTS_DIR




class Test(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError


    @staticmethod
    def check() -> bool:
        raise NotImplementedError


    @abstractmethod
    def valid(self) -> bool:
        raise NotImplementedError


    @abstractmethod
    def save(self, file: TextIO) -> None:
        raise NotImplementedError



class CreateTests:
    test_cls: Type[Test] = None


    def __init__(self, test_cls: Type[Test]) -> None:
        self.test_cls = test_cls
    

    def _save(self, tests: list[Test], test_group: int):
        for test_number, test in enumerate(tests):
            with open(ROOT_TESTS_DIR / Path(f'{test_group:02}_{test_number:02}.txt'), 'w') as f:
                test.save(f)


    def save(self, test_group: int, limit: int = 10, cycle: bool = False) -> Callable:
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


        tests: list[Test] = []
        def dec(gen: Callable[[], Generator[Any]]) -> Callable[[], Generator[Any]]:
            start_time: float = perf_counter()

            for test in map(self.test_cls, infinity_gen(gen) if cycle else gen()):
                assert test.valid()

                if len(tests) == limit:
                    break

                tests.append(test)
            
            self._save(tests, test_group)
            end_time: float = perf_counter()

            print(f'gen:test group {test_group}: created in {end_time - start_time:.3f}s ({len(tests)} tests total)')

            return gen
        return dec


