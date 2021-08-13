import QtQuick 2.12
import QtQuick.Controls 2.12

Flickable {
    id: flickable

    property string text: "..."

    TextArea.flickable: TextArea {
        textFormat: Qt.RichText
        wrapMode: TextArea.Wrap
        focus: true
        selectByMouse: true
        persistentSelection: true
        // Different styles have different padding and background
        // decorations, but since this editor is almost taking up the
        // entire window, we don't need them.
        leftPadding: 6
        rightPadding: 6
        topPadding: 10
        bottomPadding: 10
        //background: null

        text: flickable.text

        MouseArea {
            acceptedButtons: Qt.RightButton
            anchors.fill: parent
            onClicked: contextMenu.open()
        }

        onLinkActivated: Qt.openUrlExternally(link)
    }

    ScrollBar.vertical: ScrollBar { }
}
