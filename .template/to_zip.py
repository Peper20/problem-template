import datetime


from time import perf_counter
from zipfile import ZipFile, ZIP_BZIP2
from pathlib import Path


from rich.progress import Progress
from rich.console import Console


from core._files import get_tests_names, ROOT_TESTS_DIR



ROOT_ARCHIVES_DIR: Path = Path('archives')
ROOT_ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)


archive_name = f'tests {datetime.datetime.now().strftime('%d-%m-%y %H-%M-%S')}.zip'
tests = get_tests_names()
console = Console()

start_time = perf_counter()
with (
    ZipFile(
        ROOT_ARCHIVES_DIR / Path(archive_name),
        'w',
        ZIP_BZIP2,
    ) as zfile,
    Progress(console=console) as progress,
):
    progress_bar = progress.add_task('[cyan]Creating archive...', total=len(tests))
    
    for test_name in tests:
        zfile.write(ROOT_TESTS_DIR / test_name, arcname=test_name)
        progress.update(progress_bar, advance=1)


end_time = perf_counter()

console.print(f'to_zip:created "{archive_name}" in [not bold][cyan]{end_time - start_time:.3f}s[/not bold]')
