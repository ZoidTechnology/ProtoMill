from pathlib import Path

from tools.utility import run_commands


def _main() -> int:
    files = sorted(Path("resources/qml").rglob("*.qml"))

    commands = (
        ("pyright",),
        ("ruff", "check"),
        ("ruff", "format", "--check"),
        ("pyside6-qmllint", "--max-warnings", "0", *map(str, files)),
    )

    return run_commands(commands)


if __name__ == "__main__":
    raise SystemExit(_main())
