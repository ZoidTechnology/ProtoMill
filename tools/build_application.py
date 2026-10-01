from sys import executable, platform

from protomill.identity import COMPANY, NAME, VERSION
from tools.utility import BUILD_DIRECTORY, run_command


def _main() -> int:
    command = [
        executable,
        "-m",
        "nuitka",
        "--assume-yes-for-downloads",
        f"--company-name={COMPANY}",
        f"--copyright=Copyright {COMPANY}",
        "--deployment",
        f"--file-description={NAME}",
        f"--file-version={VERSION}",
        "--include-data-dir=resources=resources",
        "--lto=yes",
        "--mode=app",
        f"--output-dir={BUILD_DIRECTORY}",
        f"--output-filename={NAME}",
        "--python-flag=package_mode,no_asserts,no_docstrings",
        "--update-check=never",
        "--user-plugin=packaging/plugin.py",
    ]

    match platform:
        case "darwin":
            command += (
                "--macos-app-icon=packaging/icon.icns",
                "--macos-app-macos-min-version=13",
                f"--macos-app-version={VERSION}",
            )
        case "win32":
            command += (
                "--include-windows-runtime-dlls=yes",
                f"--onefile-tempdir-spec={{TEMP}}/{NAME}-{{PID}}",
                "--windows-console-mode=attach",
                "--windows-icon-from-ico=packaging/icon.ico",
            )
        case _:
            raise NotImplementedError("Platform is not supported")

    command += ("protomill",)

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(_main())
