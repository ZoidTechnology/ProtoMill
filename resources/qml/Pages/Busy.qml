import "../Components"

Page {
    id: root

    Progress {
        anchors.horizontalCenter: parent.horizontalCenter
        determinate: root.page.determinate
        progress: root.page.progress
    }

    Title {
        text: root.page.title
    }
}
