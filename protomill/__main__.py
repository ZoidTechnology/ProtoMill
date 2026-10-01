import logging
from asyncio import CancelledError, create_task, get_running_loop, sleep
from os import environ
from signal import SIGINT, signal
from sys import platform
from types import FrameType

from PySide6 import QtAsyncio
from PySide6.QtCore import QMessageLogContext, QtMsgType, qInstallMessageHandler
from PySide6.QtGui import QFontDatabase, QGuiApplication, QIcon, QSurfaceFormat

from protomill.application import Application
from protomill.identity import NAME, VERSION
from protomill.paths import log_path, resource_path
from protomill.utility import escape_path


_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_LOG_DATE_FORMAT = "%H:%M:%S"

_LOG_LEVELS = {
    QtMsgType.QtDebugMsg: logging.DEBUG,
    QtMsgType.QtInfoMsg: logging.INFO,
    QtMsgType.QtWarningMsg: logging.WARNING,
    QtMsgType.QtCriticalMsg: logging.ERROR,
    QtMsgType.QtFatalMsg: logging.CRITICAL,
}

_POLL_INTERVAL = 0.01

_logger = logging.getLogger(__spec__.parent)
_interrupted = False


def _main() -> int:
    signal(SIGINT, _on_interrupt)

    try:
        _configure_logging()
        _start_application()
    except BaseException:
        _logger.critical("Fatal application error", exc_info=True)
        return 1

    _logger.info("Exiting")
    return 0


def _on_interrupt(signal: int, frame: FrameType | None) -> None:
    global _interrupted
    _interrupted = True


def _configure_logging() -> None:
    logging.basicConfig(format=_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT, level=logging.INFO)
    path = log_path()

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(path, "w")
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, _LOG_DATE_FORMAT))
        logging.getLogger().addHandler(handler)

        _logger.info("Saving log to %s", escape_path(path))
    except OSError:
        _logger.exception("Failed to save log to %s", escape_path(path))

    qInstallMessageHandler(_on_qt_message)


def _on_qt_message(type: QtMsgType, context: QMessageLogContext, message: str) -> None:
    category = context.category or "default"
    name = category if category.partition(".")[0] == "qt" else f"qt.{category}"
    logger = logging.getLogger(name)
    logger.log(_LOG_LEVELS[type], message)


def _start_application() -> None:
    _logger.info("Starting %s version %s", NAME, VERSION)

    environ["QML_DISABLE_DISK_CACHE"] = "1"
    environ["QT_DISABLE_SHADER_DISK_CACHE"] = "1"

    format = QSurfaceFormat()
    format.setSamples(8)
    QSurfaceFormat.setDefaultFormat(format)

    application = QGuiApplication()
    application.setApplicationName(NAME)

    if platform != "darwin":
        application.setWindowIcon(QIcon(str(resource_path("images/icon.png"))))

    for font in resource_path("fonts").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))

    QtAsyncio.run(_run_application(), False)  # pyright: ignore[reportUnknownMemberType]


async def _run_application() -> None:
    get_running_loop().set_exception_handler(None)
    application = Application()

    async def poll() -> None:
        while not _interrupted:
            await sleep(_POLL_INTERVAL)

        application.exit()

    poll_task = create_task(poll())

    try:
        await application.run()
    finally:
        poll_task.cancel()

        try:
            await poll_task
        except CancelledError:
            pass


if __name__ == "__main__":
    raise SystemExit(_main())
