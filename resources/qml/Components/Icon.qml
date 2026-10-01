import QtQuick
import ".."

Item {
    id: root

    required property color color
    required property string name
    property real size: Style.sizes.medium

    height: size
    width: size

    Text {
        anchors.centerIn: parent
        color: root.color
        font.family: "Material Symbols Rounded"
        font.pixelSize: root.size
        font.variableAxes: {
            "opsz": root.size
        }
        font.weight: 300
        text: root.name
    }
}
