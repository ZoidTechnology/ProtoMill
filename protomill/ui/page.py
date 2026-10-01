from PySide6.QtCore import Property, QObject, Signal


_DEFAULT_PRIMARY_ENABLED = True
_DEFAULT_PRIMARY_TEXT = "Continue"
_DEFAULT_SECONDARY_TEXT = "Cancel"


class Page(QObject):
    def __init__(
        self,
        source: str,
        primary_enabled: bool = _DEFAULT_PRIMARY_ENABLED,
        primary_text: str = _DEFAULT_PRIMARY_TEXT,
        secondary_text: str = _DEFAULT_SECONDARY_TEXT,
    ) -> None:
        super().__init__()
        self._source = source
        self._primary_enabled = primary_enabled
        self._primary_text = primary_text
        self._secondary_text = secondary_text

    @Property(str, constant=True)
    def source(self) -> str:
        return self._source

    @Property(bool, constant=True)
    def primaryEnabled(self) -> bool:
        return self._primary_enabled

    @Property(str, constant=True)
    def primaryText(self) -> str:
        return self._primary_text

    @Property(str, constant=True)
    def secondaryText(self) -> str:
        return self._secondary_text


class TextPage(Page):
    titleChanged = Signal()
    bodyChanged = Signal()

    def __init__(
        self,
        source: str,
        title: str,
        body: str = "",
        primary_enabled: bool = _DEFAULT_PRIMARY_ENABLED,
        primary_text: str = _DEFAULT_PRIMARY_TEXT,
        secondary_text: str = _DEFAULT_SECONDARY_TEXT,
    ) -> None:
        super().__init__(source, primary_enabled, primary_text, secondary_text)
        self._title = title
        self._body = body

    @Property(str, notify=titleChanged)
    def title(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self.titleChanged.emit()

    @Property(str, notify=bodyChanged)
    def body(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._body

    @body.setter
    def body(self, value: str) -> None:
        self._body = value
        self.bodyChanged.emit()
