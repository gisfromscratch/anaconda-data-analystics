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

    Material.accent: "#5c9489" // Theresa-hellgrün
    //Material.accent: "#3f838c" // Theresa-türkisgrün
    //Material.accent: "#f2f163" // Theresa-gelb
    Material.background: "#295294" // Theresa-blau
    Material.foreground: "#f2f163" // Theresa-gelb
    Material.primary: "#3d83be" // Therese-hellblau

    /*
    Material.accent: "#a7ad6d"      // BW Hellgrün
    //Material.accent: "#616847"      // BW Helloliv
    Material.background: "#312d2a"  // BW Schwarz
    Material.foreground: "#d3c2a6"  // BW Beige
    Material.primary: "#434a39"     // BW Dunkelgrün
    */

    BlogGeneratorModel {
        id: genModel

        onTextGenerationFinished: {
            outputTextArea.appendText(newText)
            inputTextArea.richText = ""
        }
    }

    header: ToolBar {

        RowLayout {
            anchors.fill: parent

            ToolButton {
                text: qsTr("Generate")

                onClicked: {
                    if (lengthEnabledSwitch.checked) {
                        genModel.generateText(inputTextArea.getPlainText(), minBox.value, maxBox.value);
                    } else {
                        genModel.generateText(inputTextArea.getPlainText());
                    }
                }
            }

            Switch {
                id: lengthEnabledSwitch
                checked: false
            }

            SpinBox {
                id: minBox
                from: 20
                to: maxBox.value
                value: 50
                enabled: lengthEnabledSwitch.checked
            }

            SpinBox {
                id: maxBox
                from: minBox.value
                to: 500
                value: 120
                enabled: lengthEnabledSwitch.checked
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
        }

        ScrollableTextArea {
            id: outputTextArea
            Layout.fillHeight: parent
            Layout.fillWidth: parent
        }
    }

}
