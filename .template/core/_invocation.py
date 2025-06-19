import subprocess


from concurrent.futures import ThreadPoolExecutor
from typing import NamedTuple
from time import perf_counter
from enum import Enum


from rich.progress import Progress
from rich.console import Console
from rich.table import Table


from ._files import SolutionName, TestName, ROOT_SOLS_DIR, ROOT_TESTS_DIR, get_tests_names




type Time = float | int
DELTA = 0.011


def checker_cmp_file(a: str, b: str) -> bool:
    a, b = a.rstrip().split('\n'), b.rstrip().split('\n')

    if len(a) != len(b):
        return False

    for i, j in zip(a, b):
        if i.rstrip() != j.rstrip():
            return False

    return True


class Verdict(Enum):
    OK = 0
    WA = 1
    TL = 2
    RE = 3
    RJ = 4
    # CE = 5 # TODO: add Compilation Error

    def __str__(self):
        match self:
            case self.OK:
                return '[bright_green]OK[/bright_green]'
            case self.WA:
                return '[bright_red]WA[/bright_red]'
            case self.TL:
                return '[bright_blue]TL[/bright_blue]'
            case self.RE:
                return '[bright_red]RE[/bright_red]'
            case self.RJ:
                return '[bright_red]RJ[/bright_red]'


class RunResult(NamedTuple):
    verdict: Verdict
    time: Time = None
    jury_answer: str = None


    def __str__(self):
        return f'{self.verdict} / {float(self.time):.3f}s' if self.time is not None else f'{self.verdict}'


class Invocation:
    model_solution: SolutionName = None
    solutions: tuple[SolutionName] = None


    def __init__(self, model_solution: SolutionName, *solutions: SolutionName) -> None:
        self.model_solution = model_solution
        self.solutions = solutions

    
    @property
    def all_solutions(self) -> tuple[SolutionName]:
        return (self.model_solution,) + self.solutions


    def _run_solution_on_test(
        self,
        solution_name: SolutionName,
        test_name: TestName,
        timeout: Time,
        jury_answer: str = None, # if jury_answer is None, then it is considered that the solution is model
    ):
        test_stdin = open(ROOT_TESTS_DIR / test_name) # it is important to open each time so there is no race condition
        start_time = perf_counter()
        try:
            payload = subprocess.run(
                ['python', ROOT_SOLS_DIR / solution_name],
                stdin=test_stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout + DELTA,
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            # print(e.timeout, timeout, DELTA, timeout + DELTA, perf_counter() - start_time)
            return RunResult(Verdict.TL, e.timeout)
        
        finally:
            test_stdin.close()

        end_time = perf_counter()
        time = end_time - start_time

        if payload.returncode != 0:
            return RunResult(Verdict.RE, time)

        answer = payload.stdout.decode()

        if jury_answer is None:
            return RunResult(Verdict.OK, time, answer)

        if not checker_cmp_file(jury_answer, answer):
            return RunResult(Verdict.WA, time)
        
        return RunResult(Verdict.OK, time)



    def _run_test(self, test_name: TestName, timeout: Time, executor: ThreadPoolExecutor) -> tuple[RunResult]:
        model_result = self._run_solution_on_test(self.model_solution, test_name, timeout)
        
        if model_result.verdict != Verdict.OK:
            return model_result, *(RunResult(Verdict.RJ) for _ in range(len(self.solutions)))
        
        futures = [
            executor.submit(self._run_solution_on_test, solution, test_name, timeout, model_result.jury_answer)
            for solution in self.solutions
        ]

        return model_result, *[future.result() for future in futures]


    def run(self, timeout: Time) -> None:
        console = Console()
        table = Table(title=f'Invocation of {', '.join(self.all_solutions)}')

        table.add_column('#', justify='right')
        table.add_column('Test name')
        
        for solution in self.all_solutions:
            table.add_column(solution)
        

        tests = list(get_tests_names())
        with (
            ThreadPoolExecutor(max_workers=4) as main_executor,
            ThreadPoolExecutor(max_workers=6) as sub_executor,
            Progress(console=console) as progress,
        ):
            progress_bar = progress.add_task('[cyan]Running...', total=len(tests))

            futures = [
                (test_name, main_executor.submit(self._run_test, test_name, timeout, sub_executor))
                for test_name in tests
            ]
            
            for test_number, (test_name, future) in enumerate(futures, start=1):
                table.add_row(str(test_number), test_name, *map(str, future.result()))

                progress.update(progress_bar, advance=1)
            
            progress.remove_task(progress_bar)
        console.print(table)

