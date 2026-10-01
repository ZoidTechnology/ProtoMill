from pathlib import Path

from tools.utility import run_commands


def _main() -> int:
    files = sorted(Path("resources/qml").rglob("*.qml"))

    commands = (
        ("ruff", "check", "--select", "I", "--fix-only"),
        ("ruff", "format"),
        ("pyside6-qmlformat", "--inplace", *map(str, files)),
    )

    return run_commands(commands)


if __name__ == "__main__":
    raise SystemExit(_main())
