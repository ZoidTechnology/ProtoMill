import QtQuick
import QtQuick.Layouts
import "Components"

ColumnLayout {
    id: root

    required property var page

    signal primary
    signal secondary

    spacing: 0

    onPageChanged: {
        loader.setSource(`Pages/${root.page.source}.qml`, {
            page: page
        });
    }

    Item {
        Layout.alignment: Qt.AlignHCenter
        Layout.fillHeight: true
        Layout.fillWidth: true
        Layout.maximumWidth: 640
        Layout.minimumWidth: 480
        implicitHeight: loader.implicitHeight

        Loader {
            id: loader

            anchors.verticalCenter: parent.verticalCenter
            width: parent.width
        }
    }

    RowLayout {
        Layout.topMargin: Style.sizes.large
        spacing: 0

        Button {
            text: root.page.secondaryText

            onClicked: root.secondary()
        }

        Item {
            Layout.fillWidth: true
            Layout.minimumWidth: Style.sizes.large
        }

        Button {
            enabled: root.page.primaryEnabled
            iconName: "arrow_forward"
            primary: true
            text: root.page.primaryText

            onClicked: root.primary()
        }
    }
}
