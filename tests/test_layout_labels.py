import unittest
from types import SimpleNamespace

from vboard.layouts import get_layout_short_label, get_layout_switch_label
from vboard.window import VirtualKeyboard
from vboard.xkb_labels import get_xkb_level_labels


class LayoutSwitchLabelTest(unittest.TestCase):
    def test_uses_ukrainian_xkb_code(self):
        self.assertEqual(get_layout_switch_label("en", "uk"), "UA/EN")

    def test_redraws_for_a_russian_secondary_layout(self):
        self.assertEqual(get_layout_switch_label("en", "ru"), "RU/EN")

    def test_uses_uppercase_short_layout_ids(self):
        self.assertEqual(get_layout_short_label("de"), "DE")

    def test_falls_back_to_a_globe_for_an_unknown_long_id(self):
        self.assertEqual(get_layout_switch_label("en", "custom"), "🌐")


class AlternateLevelLabelTest(unittest.TestCase):
    def make_keyboard(self, alt=False, shift=False, caps=False):
        keyboard = SimpleNamespace(
            primary_keyboard_layout="en",
            secondary_keyboard_layout="uk",
            caps_lock_active=caps,
            modifiers={
                "Shift_L": shift,
                "Shift_R": False,
                "Alt_L": alt,
                "Alt_R": False,
            },
            system_key_levels={
                2: {"S": "ы", "3": "§"},
                3: {"S": "Ы", "3": "₴"},
            },
            get_active_key_labels=lambda: {"S": "і", "3": "3"},
            get_active_shifted_map=lambda: {"S": "І", "3": "№"},
        )
        keyboard.get_alternate_key_label = lambda key_event, shift_active: (
            VirtualKeyboard.get_alternate_key_label(
                keyboard,
                key_event,
                shift_active,
            )
        )
        return keyboard

    def test_alt_displays_third_level_ukrainian_letter(self):
        keyboard = self.make_keyboard(alt=True)

        self.assertEqual(VirtualKeyboard.get_button_label(keyboard, "S"), "ы")

    def test_alt_shift_displays_fourth_level_ukrainian_letter(self):
        keyboard = self.make_keyboard(alt=True, shift=True)

        self.assertEqual(VirtualKeyboard.get_button_label(keyboard, "S"), "Ы")

    def test_alt_displays_system_symbol_on_number_row(self):
        keyboard = self.make_keyboard(alt=True)

        self.assertEqual(VirtualKeyboard.get_button_label(keyboard, "3"), "§")

    def test_default_ukrainian_levels_come_from_system_xkb(self):
        levels = get_xkb_level_labels("ua")

        self.assertEqual(levels[2]["S"], "ы")
        self.assertEqual(levels[3]["S"], "Ы")
        self.assertEqual(levels[2]["T"], "ё")
        self.assertEqual(levels[2]["]"], "ъ")
        self.assertEqual(levels[2]["'"], "э")


if __name__ == "__main__":
    unittest.main()
