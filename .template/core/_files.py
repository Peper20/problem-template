from typing import Annotated, Generator
from pathlib import Path
from os import listdir




ROOT_SOLS_DIR: Path = Path('sols')
ROOT_TESTS_DIR: Path = Path('tests')


SolutionName = Annotated[str, 'Solution file name without path, e. g. sol1.py']
TestName = Annotated[str, 'Test file name without path, e. g. 12_02.txt']


def get_tests_names() -> Generator[TestName]:
    yield from listdir(ROOT_TESTS_DIR)


def get_group_and_number(test_name: TestName) -> tuple[int, int]:
    return tuple(map(int, test_name.split('.')[0].split('_')))


