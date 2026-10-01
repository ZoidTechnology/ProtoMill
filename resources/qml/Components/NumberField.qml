import QtQuick
import QtQuick.Templates
import ".."

TextField {
    id: root

    required property var input
    property string unit

    color: Style.colors.foreground
    font: Style.fonts.accent
    implicitHeight: Style.sizes.large
    layer.enabled: !enabled
    leftPadding: Style.sizes.small
    opacity: enabled ? 1 : 0.5
    rightPadding: Style.sizes.small + (unit ? Style.sizes.small + label.width : 0)
    selectedTextColor: Style.colors.accentForeground
    selectionColor: Style.colors.accentBackground
    verticalAlignment: TextInput.AlignVCenter

    background: Rectangle {
        border.color: Style.colors.foreground
        color: Style.colors.variant(Style.colors.background, root.hovered, root.activeFocus, root.enabled)
        radius: Style.sizes.small
    }
    validator: RegularExpressionValidator {
        regularExpression: root.input.real ? /\d*\.?\d*/ : /\d*/
    }

    Component.onCompleted: text = input.text
    onTextEdited: input.text = text

    Text {
        id: label

        anchors.right: parent.right
        anchors.rightMargin: Style.sizes.small
        anchors.verticalCenter: parent.verticalCenter
        color: root.color
        font: root.font
        opacity: 0.5
        text: root.unit
    }
}
