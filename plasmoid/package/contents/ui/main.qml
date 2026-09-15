/*
    SPDX-FileCopyrightText: 2026 Chechulin Serhii
    SPDX-License-Identifier: GPL-3.0-or-later
*/

import QtQuick
import QtQuick.Layouts

import org.kde.kirigami as Kirigami
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as Plasma5Support
import org.kde.plasma.plasmoid

PlasmoidItem {
    id: root

    readonly property string iconName: "input-keyboard"
    readonly property string toggleCommand: "/bin/sh -c '/usr/bin/gapplication action io.github.archisman-panigrahi.vboard toggle >/dev/null 2>&1 || /usr/bin/nohup /usr/bin/env vboard --toggle </dev/null >/dev/null 2>&1 &'"
    property bool busy: false

    Plasmoid.icon: iconName
    Plasmoid.title: i18n("Vboard Keyboard")
    toolTipMainText: Plasmoid.title
    toolTipSubText: i18n("Show or hide the on-screen keyboard")
    preferredRepresentation: Plasmoid.formFactor === PlasmaCore.Types.Planar
        ? fullRepresentation
        : compactRepresentation

    function handleActivationKey(event) {
        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
            root.toggleKeyboard();
            event.accepted = true;
        }
    }

    function toggleKeyboard() {
        if (busy) {
            return;
        }

        busy = true;
        executable.connectSource(toggleCommand);
    }

    Plasma5Support.DataSource {
        id: executable

        engine: "executable"

        onNewData: function(sourceName, data) {
            disconnectSource(sourceName);
            root.busy = false;
        }

        onSourceDisconnected: function(sourceName) {
            root.busy = false;
        }
    }

    TapHandler {
        acceptedButtons: Qt.LeftButton
        gesturePolicy: TapHandler.ReleaseWithinBounds
        onTapped: root.toggleKeyboard()
    }

    HoverHandler {
        id: hoverHandler

        cursorShape: Qt.PointingHandCursor
    }

    compactRepresentation: Item {
        id: compactButton

        implicitWidth: Kirigami.Units.iconSizes.medium
        implicitHeight: Kirigami.Units.iconSizes.medium
        Layout.minimumWidth: Kirigami.Units.iconSizes.medium
        Layout.minimumHeight: Kirigami.Units.iconSizes.medium
        Layout.preferredWidth: Kirigami.Units.iconSizes.medium
        Layout.preferredHeight: Kirigami.Units.iconSizes.medium
        activeFocusOnTab: true

        Accessible.name: root.toolTipSubText
        Accessible.role: Accessible.Button

        Keys.onPressed: function(event) {
            root.handleActivationKey(event);
        }

        Kirigami.Icon {
            anchors.centerIn: parent
            width: Math.min(parent.width, parent.height) * 1.3
            height: width
            source: root.iconName
            active: hoverHandler.hovered || compactButton.activeFocus
            opacity: root.busy ? 0.6 : 1.0
        }
    }

    fullRepresentation: Item {
        id: button

        Layout.minimumWidth: Kirigami.Units.iconSizes.medium
        Layout.minimumHeight: Kirigami.Units.iconSizes.medium
        Layout.preferredWidth: Kirigami.Units.iconSizes.large
        Layout.preferredHeight: Kirigami.Units.iconSizes.large
        activeFocusOnTab: true

        Accessible.name: root.toolTipSubText
        Accessible.role: Accessible.Button

        Keys.onPressed: function(event) {
            root.handleActivationKey(event);
        }

        Kirigami.Icon {
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing
            active: hoverHandler.hovered || button.activeFocus
            opacity: root.busy ? 0.6 : 1.0
            source: root.iconName

            Behavior on opacity {
                NumberAnimation {
                    duration: Kirigami.Units.shortDuration
                }
            }
        }
    }
}
