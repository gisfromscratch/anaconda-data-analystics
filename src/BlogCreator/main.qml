import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls.Material 2.12

import BlogCreator.BlogGeneratorModel 1.0

ApplicationWindow {
    width: 640
    height: 480
    visible: true
    title: qsTr("Blog Creator")

    Material.theme: Material.Dark
    Material.accent: "#a7ad6d"      // BW Hellgrün
    //Material.accent: "#616847"      // BW Helloliv
    Material.background: "#312d2a"  // BW Schwarz
    Material.foreground: "#d3c2a6"  // BW Beige
    Material.primary: "#434a39"     // BW Dunkelgrün

    BlogGeneratorModel {
        id: genModel

        onTextGenerationFinished: {
            outputTextArea.text = newText
        }
    }

    header: ToolBar {

        RowLayout {
            anchors.fill: parent

            ToolButton {
                text: qsTr("Generate...")
                onClicked: {
                    genModel.generateText(inputTextArea.text);
                }
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 15

        ScrollableTextArea {
            id: inputTextArea
            Layout.fillHeight: parent
            Layout.fillWidth: parent
            text: "Geospatial Intelligence is one of the few"
        }

        ScrollableTextArea {
            id: outputTextArea
            Layout.fillHeight: parent
            Layout.fillWidth: parent
        }
    }

}
