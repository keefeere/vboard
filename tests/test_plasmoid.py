import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLASMOID_ROOT = PROJECT_ROOT / "plasmoid" / "package"


class PlasmoidLauncherTest(unittest.TestCase):
    def test_toggle_command_detaches_vboard_from_the_executable_engine(self):
        qml = (PLASMOID_ROOT / "contents" / "ui" / "main.qml").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "/usr/bin/gapplication action io.github.archisman-panigrahi.vboard toggle",
            qml,
        )
        self.assertIn("|| /usr/bin/nohup /usr/bin/env vboard --toggle", qml)
        self.assertIn("/usr/bin/nohup /usr/bin/env vboard --toggle", qml)
        self.assertIn("</dev/null >/dev/null 2>&1 &", qml)

    def test_widget_version_marks_full_touch_target(self):
        metadata = json.loads(
            (PLASMOID_ROOT / "metadata.json").read_text(encoding="utf-8")
        )

        self.assertEqual(metadata["KPlugin"]["Version"], "1.0.3")

    def test_root_tap_handler_covers_the_whole_widget(self):
        qml = (PLASMOID_ROOT / "contents" / "ui" / "main.qml").read_text(
            encoding="utf-8"
        )

        root_handler = qml.index("    TapHandler {")
        compact_representation = qml.index("    compactRepresentation:")
        self.assertLess(root_handler, compact_representation)
        self.assertIn("onTapped: root.toggleKeyboard()", qml)
        self.assertNotIn("onClicked: root.toggleKeyboard()", qml)


if __name__ == "__main__":
    unittest.main()
