import QtQuick
import QtQuick.Layouts

Window {
    id: root

    required property string name
    required property var page
    required property var step
    required property list<string> steps
    required property string version

    signal exit
    signal primary
    signal secondary

    color: Style.colors.background
    minimumHeight: row.implicitHeight
    minimumWidth: row.implicitWidth
    visible: true

    onClosing: close => {
        close.accepted = false;
        exit();
    }

    RowLayout {
        id: row

        anchors.fill: parent
        spacing: 0

        Sidebar {
            Layout.fillHeight: true
            caption: `${root.name} ${root.version}`
            step: root.step
            steps: root.steps
        }

        Content {
            Layout.margins: Style.sizes.large
            Layout.minimumHeight: 480
            page: root.page

            onPrimary: root.primary()
            onSecondary: root.secondary()
        }
    }
}
