import QtQuick
import QtQuick.Layouts
import QtQuick.Templates
import ".."

Button {
    id: root

    readonly property color color: primary ? Style.colors.accentForeground : Style.colors.foreground
    property string iconName
    property bool primary

    horizontalPadding: Style.sizes.medium
    implicitHeight: Style.sizes.large
    implicitWidth: implicitContentWidth + leftPadding + rightPadding
    layer.enabled: !enabled
    opacity: enabled ? 1 : 0.5

    background: Rectangle {
        border.color: root.primary ? "transparent" : root.color
        color: Style.colors.variant(root.primary ? Style.colors.accentBackground : Style.colors.background, root.hovered || root.visualFocus, root.pressed, enabled)
        radius: height / 2
    }
    contentItem: RowLayout {
        spacing: Style.sizes.small

        Text {
            color: root.color
            font: Style.fonts.accent
            text: root.text
        }

        Icon {
            color: root.color
            name: root.iconName
            visible: root.iconName !== ""
        }
    }
}
