import QtQuick
import QtQuick.Layouts
import ".."

ColumnLayout {
    property alias label: label.text

    spacing: Style.sizes.tiny

    Text {
        id: label

        Layout.fillHeight: true
        Layout.fillWidth: true
        color: Style.colors.foreground
        font: Style.fonts.accent
        verticalAlignment: Text.AlignBottom
        wrapMode: Text.Wrap
    }
}
