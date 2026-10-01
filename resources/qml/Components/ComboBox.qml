pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Effects
import QtQuick.Templates
import ".."

ComboBox {
    id: root

    required property var input

    enabled: count > 1
    implicitHeight: Style.sizes.large
    layer.enabled: !enabled
    leftPadding: Style.sizes.small
    model: input.labels
    opacity: enabled ? 1 : 0.5
    rightPadding: indicator.width + Style.sizes.small * 2

    background: Rectangle {
        border.color: Style.colors.foreground
        color: Style.colors.variant(Style.colors.background, root.hovered || root.visualFocus, root.down, root.enabled)
        radius: Style.sizes.small
    }
    contentItem: ContentItem {
        text: root.displayText
    }
    delegate: ItemDelegate {
        id: delegate

        required property int index
        required property string modelData

        height: Style.sizes.large
        leftPadding: root.leftPadding
        rightPadding: root.rightPadding
        text: modelData
        width: ListView.view.width

        background: Rectangle {
            color: Style.colors.variant(Style.colors.background, delegate.index === root.highlightedIndex, delegate.pressed, root.enabled)
        }
        contentItem: ContentItem {
            text: delegate.text
        }
        indicator: Indicator {
            name: "check"
            visible: delegate.index === root.currentIndex
        }
    }
    indicator: Indicator {
        name: root.popup.visible ? "keyboard_arrow_up" : "keyboard_arrow_down"
    }
    popup: Popup {
        height: Math.min(contentItem.implicitHeight, Overlay.overlay.height - topMargin - bottomMargin)
        margins: Style.sizes.large
        width: root.width
        y: root.height + Style.sizes.small

        contentItem: Item {
            implicitHeight: list.contentHeight

            ListView {
                id: list

                anchors.fill: parent
                boundsBehavior: Flickable.StopAtBounds
                currentIndex: root.highlightedIndex
                layer.enabled: true
                model: root.delegateModel

                layer.effect: MultiEffect {
                    maskEnabled: true
                    maskSource: mask
                    maskSpreadAtMin: 1
                    maskThresholdMin: 0.5
                }
            }

            Item {
                id: mask

                anchors.fill: parent
                layer.enabled: true
                visible: false

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 1
                    radius: Style.sizes.small - anchors.margins
                }
            }

            Rectangle {
                anchors.fill: parent
                border.color: Style.colors.foreground
                color: "transparent"
                radius: Style.sizes.small
            }
        }
    }

    Component.onCompleted: currentIndex = input.index
    onActivated: input.index = currentIndex

    component ContentItem: Text {
        color: Style.colors.foreground
        elide: Text.ElideRight
        font: Style.fonts.accent
        verticalAlignment: Text.AlignVCenter
    }
    component Indicator: Icon {
        anchors.right: parent.right
        anchors.rightMargin: Style.sizes.small
        anchors.verticalCenter: parent.verticalCenter
        color: Style.colors.foreground
        size: Style.sizes.medium
    }
}
