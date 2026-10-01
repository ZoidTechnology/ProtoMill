import QtQuick
import QtQuick.Layouts
import "../Components"

Page {
    id: root

    Title {
        text: "Import KiCad design"
    }

    FormRow {
        FormColumn {
            Layout.preferredWidth: 1
            label: "Grid tolerance"

            NumberField {
                Layout.fillWidth: true
                input: root.page.tolerance
                unit: "%"
            }
        }

        FormColumn {
            Layout.preferredWidth: 1
            label: "Slot length"

            NumberField {
                Layout.fillWidth: true
                input: root.page.slotLength
                unit: "mm"
            }
        }
    }

    FormColumn {
        label: "Path optimization"
        width: parent.width

        ComboBox {
            Layout.fillWidth: true
            input: root.page.optimization
        }
    }
}
