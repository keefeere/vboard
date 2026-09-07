"""Read physical-key labels from the system XKB data via libxkbcommon."""

import ctypes
import ctypes.util


XKB_KEYCODE_INVALID = 0xFFFFFFFF

KEY_EVENT_TO_XKB_NAME = {
    "`": "TLDE",
    **{str(number): f"AE{number:02d}" for number in range(1, 10)},
    "0": "AE10",
    "-": "AE11",
    "=": "AE12",
    **{
        key: f"AD{index:02d}"
        for index, key in enumerate("QWERTYUIOP", start=1)
    },
    "[": "AD11",
    "]": "AD12",
    "\\": "BKSL",
    **{
        key: f"AC{index:02d}"
        for index, key in enumerate("ASDFGHJKL", start=1)
    },
    ";": "AC10",
    "'": "AC11",
    **{
        key: f"AB{index:02d}"
        for index, key in enumerate("ZXCVBNM", start=1)
    },
    ",": "AB08",
    ".": "AB09",
    "/": "AB10",
}


class XkbRuleNames(ctypes.Structure):
    _fields_ = (
        ("rules", ctypes.c_char_p),
        ("model", ctypes.c_char_p),
        ("layout", ctypes.c_char_p),
        ("variant", ctypes.c_char_p),
        ("options", ctypes.c_char_p),
    )


class XkbLabelReader:
    def __init__(self, library=None):
        library_name = ctypes.util.find_library("xkbcommon")
        if library is None and not library_name:
            raise OSError("libxkbcommon is not installed")
        self.library = library or ctypes.CDLL(library_name)
        self._configure_api()

    def _configure_api(self):
        library = self.library
        library.xkb_context_new.argtypes = [ctypes.c_int]
        library.xkb_context_new.restype = ctypes.c_void_p
        library.xkb_context_unref.argtypes = [ctypes.c_void_p]
        library.xkb_context_unref.restype = None
        library.xkb_keymap_new_from_names.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(XkbRuleNames),
            ctypes.c_int,
        ]
        library.xkb_keymap_new_from_names.restype = ctypes.c_void_p
        library.xkb_keymap_unref.argtypes = [ctypes.c_void_p]
        library.xkb_keymap_unref.restype = None
        library.xkb_keymap_key_by_name.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        library.xkb_keymap_key_by_name.restype = ctypes.c_uint32
        library.xkb_keymap_key_get_syms_by_level.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)),
        ]
        library.xkb_keymap_key_get_syms_by_level.restype = ctypes.c_int
        library.xkb_keysym_to_utf32.argtypes = [ctypes.c_uint32]
        library.xkb_keysym_to_utf32.restype = ctypes.c_uint32

    def get_level_labels(self, layout, variant=""):
        context = self.library.xkb_context_new(0)
        if not context:
            raise RuntimeError("could not create an XKB context")

        keymap = None
        try:
            names = XkbRuleNames(
                None,
                None,
                layout.encode("utf-8"),
                variant.encode("utf-8") if variant else None,
                None,
            )
            keymap = self.library.xkb_keymap_new_from_names(
                context,
                ctypes.byref(names),
                0,
            )
            if not keymap:
                raise ValueError(
                    f"could not compile XKB layout {layout!r} variant {variant!r}"
                )

            return {
                level: self._read_level(keymap, level)
                for level in range(4)
            }
        finally:
            if keymap:
                self.library.xkb_keymap_unref(keymap)
            self.library.xkb_context_unref(context)

    def _read_level(self, keymap, level):
        labels = {}
        for key_event, xkb_name in KEY_EVENT_TO_XKB_NAME.items():
            keycode = self.library.xkb_keymap_key_by_name(
                keymap,
                xkb_name.encode("ascii"),
            )
            if keycode == XKB_KEYCODE_INVALID:
                continue

            symbols = ctypes.POINTER(ctypes.c_uint32)()
            symbol_count = self.library.xkb_keymap_key_get_syms_by_level(
                keymap,
                keycode,
                0,
                level,
                ctypes.byref(symbols),
            )
            label = "".join(
                chr(codepoint)
                for index in range(max(0, symbol_count))
                if (codepoint := self.library.xkb_keysym_to_utf32(symbols[index]))
            )
            if label:
                labels[key_event] = label
        return labels


def get_xkb_level_labels(layout, variant=""):
    return XkbLabelReader().get_level_labels(layout, variant)
