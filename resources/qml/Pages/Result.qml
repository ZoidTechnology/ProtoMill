import QtQuick
import "../Components"
import ".."

Page {
    id: root

    Icon {
        readonly property bool error: root.page.status === "error"

        anchors.horizontalCenter: parent.horizontalCenter
        color: error ? Style.colors.error : Style.colors.success
        name: error ? "cancel" : "check_circle"
        scale: 1.25
        size: Style.sizes.huge
    }

    Title {
        text: root.page.title
    }

    Body {
        body: root.page.body
    }
}
