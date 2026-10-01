pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import "Components"

Rectangle {
    id: root

    required property string caption
    required property var step
    required property list<string> steps

    color: Style.colors.accentBackground
    implicitHeight: column.implicitHeight + Style.sizes.large * 2
    implicitWidth: column.implicitWidth + Style.sizes.large * 2

    ColumnLayout {
        id: column

        anchors.fill: parent
        anchors.margins: Style.sizes.large
        spacing: Style.sizes.medium

        Repeater {
            model: root.steps

            RowLayout {
                id: row

                required property int index
                required property string modelData

                opacity: index === root.step.index ? 1 : 0.5
                spacing: Style.sizes.small

                Icon {
                    color: Style.colors.accentForeground
                    name: {
                        if (row.index > root.step.index) {
                            return "circle";
                        }

                        if (row.index < root.step.index || root.step.status === "success") {
                            return "check_circle";
                        }

                        if (root.step.status === "error") {
                            return "cancel";
                        }

                        return "adjust";
                    }
                }

                Text {
                    color: Style.colors.accentForeground
                    font: Style.fonts.accent
                    text: row.modelData
                }
            }
        }

        Item {
            Layout.fillHeight: true
            Layout.fillWidth: true
            implicitHeight: Style.sizes.large

            Text {
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                color: Style.colors.accentForeground
                font: Style.fonts.caption
                height: Style.sizes.large
                opacity: 0.5
                text: root.caption
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}
