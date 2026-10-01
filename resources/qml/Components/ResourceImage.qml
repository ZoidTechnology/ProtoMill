import QtQuick

Image {
    required property string name

    fillMode: Image.PreserveAspectFit
    mipmap: true
    source: `../../images/${name}.png`
}
