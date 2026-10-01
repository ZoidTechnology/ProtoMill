import QtQuick
import "../Components"
import ".."

Page {
    id: root

    Item {
        anchors.horizontalCenter: parent.horizontalCenter
        height: tool.height
        width: tool.width

        ResourceImage {
            id: tool

            height: 256
            name: "tool"
        }

        ResourceImage {
            id: clip

            name: "clip"
            width: 128
            y: 169

            ParallelAnimation {
                loops: Animation.Infinite
                running: true

                NumberAnimation {
                    readonly property int targetX: 48 + Style.sizes.small

                    duration: 2000
                    easing.type: Easing.InOutSine
                    from: targetX + (root.page.reverse ? 0 : Style.sizes.large)
                    property: "x"
                    target: clip
                    to: targetX + (root.page.reverse ? Style.sizes.large : 0)
                }

                SequentialAnimation {
                    NumberAnimation {
                        duration: 500
                        from: 0
                        property: "opacity"
                        target: clip
                        to: 1
                    }

                    PauseAnimation {
                        duration: 1000
                    }

                    NumberAnimation {
                        duration: 500
                        property: "opacity"
                        target: clip
                        to: 0
                    }

                    PauseAnimation {
                        duration: 500
                    }
                }
            }
        }
    }

    Title {
        text: root.page.title
    }

    Body {
        body: root.page.body
        textFormat: Text.RichText
    }
}
