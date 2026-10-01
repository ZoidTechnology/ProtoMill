import QtQuick
import ".."

Text {
    required property string body

    color: Style.colors.foreground
    font: Style.fonts.body
    horizontalAlignment: Text.Center
    text: textFormat === Text.RichText ? `<style>b{color:${Style.colors.accentBackground};font-weight:600;}</style>${body}` : body
    textFormat: Text.PlainText
    width: parent.width
    wrapMode: Text.Wrap
}
