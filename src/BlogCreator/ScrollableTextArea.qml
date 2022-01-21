import QtQuick 2.12
import QtQuick.Controls 2.12

Flickable {
    id: flickable

    property string richText

    function appendText(newText) {
        flickable.richText += "<br/>"
        flickable.richText += newText
    }

    function getPlainText() {
        return textArea.getText(0, textArea.length);
    }

    TextArea.flickable: TextArea {
        id: textArea
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

        text: flickable.richText

        Binding {
            target: flickable
            property: "richText"
            value: textArea.text
        }

        MouseArea {
            acceptedButtons: Qt.RightButton
            anchors.fill: parent
            onClicked: contextMenu.open()
        }

        onLinkActivated: Qt.openUrlExternally(link)
    }

    ScrollBar.vertical: ScrollBar { }
}
