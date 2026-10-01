from collections.abc import Sequence
from pathlib import Path
from subprocess import run


BUILD_DIRECTORY = Path("build")


def run_command(command: Sequence[str]) -> int:
    print(" ".join(command))
    return run(command, check=False).returncode


def run_commands(commands: Sequence[Sequence[str]]) -> int:
    code = 0

    for command in commands:
        code = run_command(command) or code

    return code
