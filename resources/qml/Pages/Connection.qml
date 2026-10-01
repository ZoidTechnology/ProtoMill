import QtQuick
import QtQuick.Layouts
import "../Components"

Page {
    id: root

    Title {
        text: "Connect to CNC machine"
    }

    FormColumn {
        label: "Controller"
        width: parent.width

        ComboBox {
            Layout.fillWidth: true
            input: root.page.controller
        }
    }

    FormRow {
        FormColumn {
            Layout.preferredWidth: 2
            label: "Serial port"

            ComboBox {
                Layout.fillWidth: true
                input: root.page.port
            }
        }

        FormColumn {
            Layout.preferredWidth: 1
            label: "Baud rate"

            NumberField {
                Layout.fillWidth: true
                input: root.page.baudRate
            }
        }
    }
}
