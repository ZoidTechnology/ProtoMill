import QtQuick
import "../Components"

Page {
    id: root

    ResourceImage {
        anchors.horizontalCenter: parent.horizontalCenter
        height: 256
        name: root.page.image
    }

    Title {
        text: root.page.title
    }

    Body {
        body: root.page.body
        textFormat: Text.RichText
    }
}
