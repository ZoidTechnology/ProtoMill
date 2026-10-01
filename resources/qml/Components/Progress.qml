import QtQuick
import QtQuick.Shapes
import ".."

Item {
    id: root

    readonly property int center: size / 2
    required property bool determinate
    readonly property real maximumSweep: 240
    readonly property real minimumSweep: 60
    required property real progress
    readonly property int radius: center - strokeWidth / 2
    readonly property int rotationPeriod: 1000
    property real size: Style.sizes.huge
    readonly property int strokeWidth: Style.sizes.tiny
    readonly property int sweepPeriod: 2500

    height: size
    width: size

    Behavior on progress {
        enabled: root.determinate

        NumberAnimation {
            duration: 500
            easing.type: Easing.InOutSine
        }
    }

    Shape {
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer

        ShapePath {
            fillColor: "transparent"
            strokeColor: Style.colors.variant(Style.colors.background)
            strokeWidth: root.strokeWidth

            PathAngleArc {
                centerX: root.center
                centerY: root.center
                radiusX: root.radius
                radiusY: root.radius
                sweepAngle: 360
            }
        }

        ShapePath {
            capStyle: ShapePath.RoundCap
            fillColor: "transparent"
            strokeColor: Style.colors.accentBackground
            strokeWidth: root.strokeWidth

            PathAngleArc {
                property real spin
                property real sweep

                centerX: root.center
                centerY: root.center
                radiusX: root.radius
                radiusY: root.radius
                startAngle: root.determinate ? -90 : spin - sweep / 2
                sweepAngle: root.determinate ? root.progress * 360 : sweep

                NumberAnimation on spin {
                    duration: root.rotationPeriod
                    from: 0
                    loops: Animation.Infinite
                    running: !root.determinate
                    to: 360
                }
                SequentialAnimation on sweep {
                    loops: Animation.Infinite
                    running: !root.determinate

                    NumberAnimation {
                        duration: root.sweepPeriod / 2
                        easing.type: Easing.InOutSine
                        from: root.minimumSweep
                        to: root.maximumSweep
                    }

                    NumberAnimation {
                        duration: root.sweepPeriod / 2
                        easing.type: Easing.InOutSine
                        to: root.minimumSweep
                    }
                }
            }
        }
    }

    Text {
        anchors.centerIn: parent
        color: Style.colors.foreground
        font: Style.fonts.accent
        text: `${(root.progress * 100).toFixed()}%`
        visible: root.determinate
    }
}
