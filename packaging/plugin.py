# type: ignore
# ruff: noqa: ANN201, ANN202


from functools import cached_property
from pathlib import Path
from sys import platform

from nuitka.plugins.PluginBase import NuitkaPluginBase


_QT_PLUGINS = {"darwin": ("platforms/libqcocoa.dylib",), "win32": ("platforms/qwindows.dll",)}

_QML_MODULES = (
    "QtQuick",
    "QtQuick/Effects",
    "QtQuick/Layouts",
    "QtQuick/Shapes",
    "QtQuick/Templates",
)


class ProtoMillPlugin(NuitkaPluginBase):
    plugin_name = "protomill"
    plugin_gui_toolkit = True
    binding_name = "PySide6"

    def considerDataFiles(self, module):
        if module.getFullName() != "PySide6":
            return ()

        return [
            self.makeIncludedDataFile(str(path), self._destination(path), "QML module file")
            for path, binary in self._qml_files
            if not binary
        ]

    def getExtraDlls(self, module):
        if module.getFullName() != "PySide6":
            return ()

        return [
            self._make_dll_entry_point(self._qt_directory / "plugins" / plugin, "Qt plugin")
            for plugin in _QT_PLUGINS[platform]
        ] + [
            self._make_dll_entry_point(path, "QML module plugin")
            for path, binary in self._qml_files
            if binary
        ]

    @cached_property
    def _pyside_directory(self):
        return Path(self.locateModule("PySide6"))

    @cached_property
    def _qt_directory(self):
        return self._pyside_directory / ("" if platform == "win32" else "Qt")

    @cached_property
    def _qml_files(self):
        return [
            (path, binary)
            for module in _QML_MODULES
            for path in (self._qt_directory / "qml" / module).iterdir()
            if (binary := path.suffix in (".dll", ".dylib", ".so")) or path.name == "qmldir"
        ]

    def _destination(self, path):
        return str(path.relative_to(self._pyside_directory.parent))

    def _make_dll_entry_point(self, path, reason):
        return self.makeDllEntryPoint(
            str(path), self._destination(path), "PySide6", "PySide6", reason
        )
