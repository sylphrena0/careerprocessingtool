import QtQuick 6.4
import QtQuick.Controls 6.4
import QtQuick.Layouts 6.4
import QtQuick.Controls.Material 2.12
import QtQuick.Dialogs 6.4

ApplicationWindow {
    visible: true
    width: 520
    height: 420
    maximumWidth: 520
    maximumHeight: 420
    minimumWidth: 520
    minimumHeight: 420
    
    Material.theme: Material.System
    Material.accent: Material.Purple
    
    color: "#252525"
    title: "APS Career Processing Tool"

    objectName: "Application"

    property string selected: "import-job-data_example.csv"
    property string home

    Rectangle {
        id: rectangle

        StackView {
            id: stackView
            x: 0
            y: 0
            width: 520
            height: 420
            state: "Meni"
            font.family: "Arial"
            hoverEnabled: true
            enabled: true

            Image {
                id: logo
                y: 50
                source: "logo.png"
                anchors.horizontalCenter: parent.horizontalCenter
                fillMode: Image.PreserveAspectFit
            }
            Text {
                id: text1
                x: -318
                y: 237
                width: 441
                height: 62
                color: "#ffffff"
                text: qsTr("Welcome to the APS Career Data Processing Tool!")
                font.pixelSize: 18
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                wrapMode: Text.Wrap
                anchors.horizontalCenterOffset: 1
                anchors.horizontalCenter: parent.horizontalCenter
                font.family: "Arial"
            }

            RowLayout {
                id: mainMenuButtons
                x: -221
                y: 324
                anchors.horizontalCenterOffset: 1
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: importData
                    width: 110
                    text: qsTr("Import Data")
                    Layout.preferredHeight: 48
                    Layout.preferredWidth: 125
                    layer.enabled: true
                    focusPolicy: Qt.StrongFocus
                    display: AbstractButton.TextOnly
                    highlighted: false
                    font.family: "Arial"
                    font.capitalization: Font.Capitalize

                    Connections {
                        target: importData
                        function onClicked() {
                            rectangle.state = "Import"
                        }
                    }
                }

                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: analyzeData
                    text: qsTr("Analyze Data")
                    display: AbstractButton.TextOnly
                    flat: false
                    highlighted: false
                    checkable: false
                    font.family: "Arial"
                    font.capitalization: Font.Capitalize
                    autoExclusive: false
                    Layout.preferredHeight: 48
                    Layout.preferredWidth: 125
        

                    Connections {
                        target: analyzeData
                        function onClicked() {
                            rectangle.state = "Analyze"
                        }
                    }
                }
            }

            RowLayout {
                id: importButtons
                x: -225
                y: 320
                visible: false
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                anchors.horizontalCenterOffset: 1
                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: selectInput
                    width: 110
                    text: qsTr("Select Input")
                    font.family: "Arial"
                    Layout.preferredWidth: 125
                    Layout.preferredHeight: 48
                    font.capitalization: Font.Capitalize
                    highlighted: false
                    display: AbstractButton.TextOnly
                    layer.enabled: true
                    focusPolicy: Qt.StrongFocus
                    onClicked: fileDialog.open()

                }

                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: startImport
                    text: qsTr("Start Import")
                    font.family: "Arial"
                    Layout.preferredWidth: 125
                    Layout.preferredHeight: 48
                    font.capitalization: Font.Capitalize
                    highlighted: false
                    display: AbstractButton.TextOnly
                    flat: false
                    autoExclusive: false
                    checkable: false
                }

                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: importBack
                    text: qsTr("Back")
                    font.family: "Arial"
                    Layout.preferredWidth: 55
                    Layout.preferredHeight: 48
                    font.capitalization: Font.Capitalize
                    highlighted: false
                    display: AbstractButton.TextOnly
                    flat: true
                    autoExclusive: false

                    Connections {
                        target: importBack
                        function onClicked() {
                            rectangle.state = ""
                    }
                    }
                    
                    checkable: false
                }
            }

            RowLayout {
                id: analyzeButtons
                x: -222
                y: 323
                visible: false
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                anchors.horizontalCenterOffset: 1
                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: textInput
                    width: 110
                    text: qsTr("Text Input")
                    font.family: "Arial"
                    Layout.preferredWidth: 125
                    Layout.preferredHeight: 48
                    font.capitalization: Font.Capitalize
                    highlighted: false
                    display: AbstractButton.TextOnly
                    layer.enabled: true
                    focusPolicy: Qt.StrongFocus
                    Connections {
                        target: importData
                        function onClicked() {
                            rectangle.state = "Import"
                        }
                    }
                }

                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: fileInput
                    text: qsTr("File Input")
                    font.family: "Arial"
                    Layout.preferredWidth: 125
                    Layout.preferredHeight: 48
                    font.capitalization: Font.Capitalize
                    highlighted: false
                    display: AbstractButton.TextOnly
                    flat: false
                    autoExclusive: false
                    checkable: false
                    onClicked: fileDialog.open()
                }

                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: searchInput
                    text: qsTr("Search Input")
                    font.family: "Arial"
                    Layout.preferredWidth: 125
                    Layout.preferredHeight: 48
                    font.capitalization: Font.Capitalize
                    highlighted: false
                    display: AbstractButton.TextOnly
                    flat: false
                    autoExclusive: false
                    checkable: false
                }

                Button {
                    Material.roundedScale: Material.ExtraSmallScale
                    id: analyzeBack
                    text: qsTr("Back")
                    font.family: "Arial"
                    Layout.preferredWidth: 55
                    Layout.preferredHeight: 48
                    font.capitalization: Font.Capitalize
                    highlighted: false
                    display: AbstractButton.TextOnly
                    flat: true
                    autoExclusive: false
                    Connections {
                        target: analyzeBack
                        function onClicked() { 
                            rectangle.state = ""
                        }
                    }
                    checkable: false
                }
            }
        }
        states: [
            State {
                name: "Import"

                PropertyChanges {
                    target: text1
                    y: 252
                    width: 385
                    height: 42
                    text: qsTr("Ready to import default file to database.")
                    horizontalAlignment: Text.AlignHCenter
                }

                PropertyChanges {
                    target: mainMenuButtons
                    visible: false
                }

                PropertyChanges {
                    target: importButtons
                    visible: true
                }

                PropertyChanges {
                    target: importBack
                    text: qsTr("Back")
                    flat: true
                }
            },
            State {
                name: "Analyze"

                PropertyChanges {
                    target: mainMenuButtons
                    visible: false
                }

                PropertyChanges {
                    target: analyzeButtons
                    visible: true
                }

                PropertyChanges {
                    target: text1
                    y: 229
                    width: 415
                    height: 66
                    text: qsTr("You may analyze with text input, via a comma seperated text file, or you may search for common words to use in the analysis.")
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.Wrap
                    anchors.horizontalCenterOffset: 1
                }
            }
        ]
    }

    FileDialog {
        id: fileDialog
        currentFolder: home
        onAccepted: selected = selectedFile
    }


}