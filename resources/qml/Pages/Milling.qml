import QtQml
import QtQuick.Layouts
import "../Components"

Page {
    id: root

    Title {
        text: "Configure milling parameters"
    }

    FormRow {
        FormColumn {
            Layout.preferredWidth: 1
            label: "Slot depth"

            NumberField {
                Layout.fillWidth: true
                input: root.page.depth
                unit: "mm"
            }
        }

        FormColumn {
            Layout.preferredWidth: 1
            label: "Passes"

            NumberField {
                Layout.fillWidth: true
                input: root.page.passes
            }
        }
    }

    FormRow {
        FormColumn {
            Layout.preferredWidth: 1
            label: "Spindle speed"

            NumberField {
                Layout.fillWidth: true
                input: root.page.spindleSpeed
                unit: "rpm"
            }
        }

        FormColumn {
            Layout.preferredWidth: 1
            label: "Spindle acceleration time"

            NumberField {
                Layout.fillWidth: true
                input: root.page.spindleAccelerationTime
                unit: "s"
            }
        }
    }

    FormRow {
        FormColumn {
            Layout.preferredWidth: 1
            label: "Plunge rate"

            NumberField {
                Layout.fillWidth: true
                input: root.page.plungeRate
                unit: "mm/min"
            }
        }

        FormColumn {
            Layout.preferredWidth: 1
            label: "Feed rate"

            NumberField {
                Layout.fillWidth: true
                input: root.page.feedRate
                unit: "mm/min"
            }
        }
    }
}
