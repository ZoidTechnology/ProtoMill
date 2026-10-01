pragma Singleton

import QtQuick

QtObject {
    readonly property Colors colors: Colors {}
    readonly property Fonts fonts: Fonts {}
    readonly property Sizes sizes: Sizes {}

    component Colors: QtObject {
        readonly property color accentBackground: "#2080c8"
        readonly property color accentForeground: "#ffffff"
        readonly property color background: "#ffffff"
        readonly property color error: "#e02040"
        readonly property color foreground: "#202020"
        readonly property color success: "#20b880"

        function variant(base, weak = true, strong = false, enabled = true) {
            if (enabled) {
                if (strong) {
                    return Qt.darker(base, 1.2);
                }

                if (weak) {
                    return Qt.darker(base, 1.1);
                }
            }

            return base;
        }
    }
    component Fonts: QtObject {
        readonly property font accent: Qt.font({
            family: "Outfit",
            pixelSize: 16
        })
        readonly property font body: Qt.font({
            family: "Inter",
            pixelSize: 16,
            weight: 300
        })
        readonly property font caption: Qt.font({
            family: "Outfit",
            pixelSize: 12
        })
        readonly property font title: Qt.font({
            family: "Outfit",
            pixelSize: 24
        })
    }
    component Sizes: QtObject {
        readonly property int huge: 96
        readonly property int large: 48
        readonly property int medium: 24
        readonly property int small: 12
        readonly property int tiny: 6
    }
}
