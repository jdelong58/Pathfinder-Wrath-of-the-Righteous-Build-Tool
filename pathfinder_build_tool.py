#!/usr/bin/env python3
"""
Pathfinder: Wrath of the Righteous Build Tool
Single-file Tkinter GUI backed by SQLite.

Tabs (in order):
  1. View a Build
  2. View Mythic Feat
  3. Create a Build
  4. Add/Update Mythic Feat
  5. Delete a Build
  6. Delete Mythic Feat
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import os
import sys
import sqlite3
import weakref
import tkinter as tk
from tkinter import ttk, messagebox

# ── Constants ─────────────────────────────────────────────────────────────────
DB_PATH = os.path.join("data", "pathfinder.db")
COORDS_PATH = os.path.join("data", "window_coords.txt")

BG = "black"
ACCENT = "#371e32"
ACCENT_HOVER = "#6b3a5e"
FG = "white"
FONT = ("Arial", 10)
FONT_BOLD = ("Arial", 11, "bold")
FONT_TITLE = ("Arial", 13, "bold")
FONT_TAB = ("Arial", 11, "bold")

PAD = {"padx": 5, "pady": 3}
FIRST_COLUMN_SKILL_COUNT = 6

# Ordered field descriptors: (db_column, header_text, short_attr)
STAT_FIELDS = [
    ("stat_strength",     "Strength:",     "str"),
    ("stat_dexterity",    "Dexterity:",    "dex"),
    ("stat_constitution", "Constitution:", "con"),
    ("stat_intelligence", "Intelligence:", "int"),
    ("stat_wisdom",       "Wisdom:",       "wis"),
    ("stat_charisma",     "Charisma:",     "cha"),
]

SKILL_FIELDS = [
    ("skill_Athletics",          "Athletics:",        "athl"),
    ("skill_Mobility",           "Mobility:",         "mobi"),
    ("skill_Trickery",           "Trickery:",         "tric"),
    ("skill_Stealth",            "Stealth:",          "stel"),
    ("skill_Knowledge_Arcana",   "Knwl Arcana:",      "ka"),
    ("skill_Knowledge_World",    "Knwl World:",       "kw"),
    ("skill_Lore_Nature",        "Lore Nature:",      "ln"),
    ("skill_Lore_Religion",      "Lore Religion:",    "lr"),
    ("skill_Perception",         "Perception:",       "perc"),
    ("skill_Persuasion",         "Persuasion:",       "pers"),
    ("skill_Use_Magical_Device", "Use Magic Device:", "umd"),
]

OTHER_FIELDS = [
    ("feat_1",       "Feat 1:",       "f1"),
    ("feat_2",       "Feat 2:",       "f2"),
    ("class_feat_1", "Class Feat 1:", "cf1"),
    ("class_feat_2", "Class Feat 2:", "cf2"),
    ("spells_1",     "Spells 1:",     "sp1"),
    ("spells_2",     "Spells 2:",     "sp2"),
    ("spells_3",     "Spells 3:",     "sp3"),
    ("c_class",      "Class:",        "cls"),
]

MT_STAT_FIELDS = [
    ("mt_stat_strength",     "Mount STR:", "mt_str"),
    ("mt_stat_dexterity",    "Mount DEX:", "mt_dex"),
    ("mt_stat_constitution", "Mount CON:", "mt_con"),
    ("mt_stat_intelligence", "Mount INT:", "mt_int"),
    ("mt_stat_wisdom",       "Mount WIS:", "mt_wis"),
    ("mt_stat_charisma",     "Mount CHA:", "mt_cha"),  # Bug #4 fix: separate from mt_wisdom
]

MT_SKILL_FIELDS = [
    ("mt_skill_Athletics",          "Athletics:",        "mt_athl"),
    ("mt_skill_Mobility",           "Mobility:",         "mt_mobi"),
    ("mt_skill_Trickery",           "Trickery:",         "mt_tric"),
    ("mt_skill_Stealth",            "Stealth:",          "mt_stel"),
    ("mt_skill_Knowledge_Arcana",   "Knwl Arcana:",      "mt_ka"),
    ("mt_skill_Knowledge_World",    "Knwl World:",       "mt_kw"),
    ("mt_skill_Lore_Nature",        "Lore Nature:",      "mt_ln"),
    ("mt_skill_Lore_Religion",      "Lore Religion:",    "mt_lr"),
    ("mt_skill_Perception",         "Perception:",       "mt_perc"),
    ("mt_skill_Persuasion",         "Persuasion:",       "mt_pers"),
    ("mt_skill_Use_Magical_Device", "Use Magic Device:", "mt_umd"),
]

CREATE_BUILD_EXTRA_FIELDS = [
    ("mt_feat_1", "Mount Feat:", "mt_f1"),
    ("mythic_feat", "Mythic Feat:", "myth"),
]

CREATE_BUILD_FIELDS = (
    STAT_FIELDS
    + SKILL_FIELDS
    + OTHER_FIELDS
    + MT_STAT_FIELDS
    + MT_SKILL_FIELDS
    + CREATE_BUILD_EXTRA_FIELDS
)

# Fields whose values must be numeric (or empty) when saving a build
NUMERIC_DB_COLS = frozenset(
    col for col, *_ in STAT_FIELDS + SKILL_FIELDS + MT_STAT_FIELDS + MT_SKILL_FIELDS
)


# ── DB Helpers ────────────────────────────────────────────────────────────────

def resource_path(relative_path: str) -> str:
    """Return absolute path; works for development and PyInstaller bundles."""
    try:
        base = sys._MEIPASS  # Bug #1 fix: was sys._MEIPASS2
    except AttributeError:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)


def get_connection() -> sqlite3.Connection:
    """Open the database and return a connection with Row factory enabled."""
    conn = sqlite3.connect(resource_path(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the data directory and builds table if they do not already exist."""
    os.makedirs("data", exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS builds (
                character_name          TEXT,
                build_type              TEXT,
                character_level         TEXT,
                stat_strength           TEXT,
                stat_dexterity          TEXT,
                stat_constitution       TEXT,
                stat_intelligence       TEXT,
                stat_wisdom             TEXT,
                stat_charisma           TEXT,
                skill_Athletics         TEXT,
                skill_Mobility          TEXT,
                skill_Trickery          TEXT,
                skill_Stealth           TEXT,
                skill_Knowledge_Arcana  TEXT,
                skill_Knowledge_World   TEXT,
                skill_Lore_Nature       TEXT,
                skill_Lore_Religion     TEXT,
                skill_Perception        TEXT,
                skill_Persuasion        TEXT,
                skill_Use_Magical_Device TEXT,
                feat_1                  TEXT,
                feat_2                  TEXT,
                class_feat_1            TEXT,
                class_feat_2            TEXT,
                spells_1                TEXT,
                spells_2                TEXT,
                spells_3                TEXT,
                c_class                 TEXT,
                mt_stat_strength        TEXT,
                mt_stat_dexterity       TEXT,
                mt_stat_constitution    TEXT,
                mt_stat_intelligence    TEXT,
                mt_stat_wisdom          TEXT,
                mt_stat_charisma        TEXT,
                mt_skill_Athletics      TEXT,
                mt_skill_Mobility       TEXT,
                mt_skill_Trickery       TEXT,
                mt_skill_Stealth        TEXT,
                mt_skill_Knowledge_Arcana TEXT,
                mt_skill_Knowledge_World  TEXT,
                mt_skill_Lore_Nature    TEXT,
                mt_skill_Lore_Religion  TEXT,
                mt_skill_Perception     TEXT,
                mt_skill_Persuasion     TEXT,
                mt_skill_Use_Magical_Device TEXT,
                mt_feat_1               TEXT,
                mythic_feat             TEXT
            )
        """)


# ── Styles ────────────────────────────────────────────────────────────────────

def apply_styles(root: tk.Tk) -> None:
    """Register and activate the custom 'pathfinder' ttk theme."""
    style = ttk.Style(root)

    # Bug #2 fix: the original code had two separate "TNotebook.Tab" keys in the
    # settings dict — the first (configure) was silently overwritten by the second
    # (map).  Both directives now live inside a single entry.
    style.theme_create("pathfinder", parent="alt", settings={
        "TNotebook": {
            "configure": {
                "tabmargins": [2, 5, 2, 0],
                "background": BG,
            }
        },
        "TNotebook.Tab": {
            "configure": {         # ← was overwritten in original
                "padding": [10, 5],
                "background": ACCENT,
                "foreground": FG,
                "font": FONT_TAB,
            },
            "map": {               # ← used to be a duplicate key (silently won)
                "background": [("selected", ACCENT_HOVER)],
                "foreground": [("selected", FG)],
            },
        },
        "TCombobox": {
            "configure": {
                "selectbackground": ACCENT,
                "fieldbackground": ACCENT,
                "background": ACCENT,
                "foreground": FG,
                "insertcolor": FG,
            }
        },
        "TScrollbar": {
            "configure": {
                "background": ACCENT,
                "troughcolor": BG,
                "arrowcolor": FG,
            }
        },
        "TSeparator": {
            "configure": {"background": ACCENT}
        },
    })
    style.theme_use("pathfinder")
    root.option_add("*TCombobox*Listbox.background", ACCENT)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT_HOVER)


# ── Shared Widgets ────────────────────────────────────────────────────────────

def make_label(parent, text="", bold=False, title=False, **kw):
    """Return a configured Label with the standard colour scheme."""
    font = FONT_TITLE if title else (FONT_BOLD if bold else FONT)
    return tk.Label(parent, text=text, bg=BG, fg=FG, font=font, **kw)


def make_button(parent, text, command, **kw):
    """Return a configured Button with the standard colour scheme."""
    return tk.Button(
        parent, text=text, command=command,
        bg=ACCENT, fg=FG, font=FONT_BOLD,
        activebackground=ACCENT_HOVER, activeforeground=FG,
        relief="flat", **kw
    )


# ── Base Class: BuildSelector ─────────────────────────────────────────────────

class BuildSelector(tk.Frame):
    """
    Abstract base Frame that provides the standard cascading
    Character Name → Build Type → Character Level comboboxes.

    Concrete tabs inherit from this class and call
    ``_create_selector_row(container_frame)`` during their own ``__init__``.

    Bug #13 fix: all method first-parameters are named ``self`` (the original
    code named them after the module-level frame variables, shadowing them).
    """

    _instances: weakref.WeakSet["BuildSelector"] = weakref.WeakSet()

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.level_var = tk.StringVar()
        # Combobox widgets are created by _create_selector_row
        self.name_combo = None
        self.type_combo = None
        self.level_combo = None
        self.__class__._instances.add(self)

    # ── Widget factory ──────────────────────────────────────────────────────

    def _create_selector_row(self, container: tk.Frame, row: int = 0) -> None:
        """
        Lay out the three standard comboboxes in *container* at grid row *row*.
        """
        make_label(container, "Character Name:", bold=True).grid(
            row=row, column=0, sticky="e", **PAD)
        self.name_combo = ttk.Combobox(container, textvariable=self.name_var,
                                       width=25, state="readonly")
        self.name_combo.grid(row=row, column=1, sticky="w", **PAD)
        self.name_combo.bind("<<ComboboxSelected>>", self.populate_types)

        make_label(container, "Build Type:", bold=True).grid(
            row=row, column=2, sticky="e", **PAD)
        self.type_combo = ttk.Combobox(container, textvariable=self.type_var,
                                       width=25, state="readonly")
        self.type_combo.grid(row=row, column=3, sticky="w", **PAD)
        self.type_combo.bind("<<ComboboxSelected>>", self.populate_levels)

        make_label(container, "Character Level:", bold=True).grid(
            row=row, column=4, sticky="e", **PAD)
        self.level_combo = ttk.Combobox(container, textvariable=self.level_var,
                                        width=8, state="readonly")
        self.level_combo.grid(row=row, column=5, sticky="w", **PAD)

    # ── Populate helpers ────────────────────────────────────────────────────

    def populate_names(self) -> None:
        """Reload the character-name combobox from the database."""
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT character_name FROM builds"
                " ORDER BY character_name"
            ).fetchall()
        self.name_combo["values"] = [r["character_name"] for r in rows]

    def populate_types(self, event=None) -> None:
        """Reload build-type combobox; clear level on change."""
        name = self.name_var.get()
        # Bug #11 fix (partial): clearing downstream dropdowns on every
        # name-selection prevents cross-character contamination.
        self.type_var.set("")
        self.type_combo["values"] = []
        self.level_var.set("")
        self.level_combo["values"] = []
        if not name:
            return
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT build_type FROM builds"
                " WHERE character_name=?"
                " ORDER BY build_type",
                (name,)
            ).fetchall()
        self.type_combo["values"] = [r["build_type"] for r in rows]

    def populate_levels(self, event=None) -> None:
        """
        Reload level combobox.
        Bug #11 fix: filter by BOTH character_name AND build_type so that
        levels from a different character with the same build_type name do not
        appear.
        """
        name = self.name_var.get()
        build_type = self.type_var.get()
        self.level_var.set("")
        self.level_combo["values"] = []
        if not name or not build_type:
            return
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT character_level FROM builds"
                " WHERE character_name=? AND build_type=?"
                " ORDER BY CAST(character_level AS INTEGER)",
                (name, build_type)
            ).fetchall()
        self.level_combo["values"] = [r["character_level"] for r in rows]

    def refresh_names(self) -> None:
        """
        Refresh selector values while preserving valid current selections.
        """
        current_name = self.name_var.get()
        current_type = self.type_var.get()
        current_level = self.level_var.get()
        self.populate_names()
        names = set(self.name_combo["values"]) if self.name_combo else set()
        if not current_name or current_name not in names:
            self.name_var.set("")
            self.type_var.set("")
            self.level_var.set("")
            return
        self.name_var.set(current_name)
        self.populate_types()
        types = set(self.type_combo["values"]) if self.type_combo else set()
        if not current_type or current_type not in types:
            self.type_var.set("")
            self.level_var.set("")
            return
        self.type_var.set(current_type)
        self.populate_levels()
        levels = set(self.level_combo["values"]) if self.level_combo else set()
        if current_level and current_level in levels:
            self.level_var.set(current_level)
        else:
            self.level_var.set("")

    @classmethod
    def refresh_all_selectors(cls) -> None:
        """Refresh all instantiated BuildSelector tabs after DB writes."""
        for selector in list(cls._instances):
            if selector.winfo_exists():
                selector.refresh_names()


# ── Tab 1: View a Build ───────────────────────────────────────────────────────

class LoadBuilds(BuildSelector):
    """
    'View a Build' tab.

    Bug #3 fix : uses named column access (data["skill_Use_Magical_Device"])
                 instead of mismatched numeric indices.
    Bug #4 fix : mt_stat_charisma is read from its own column, not mt_stat_wisdom.
    Bug #5 fix : data-value labels stored as self.<attr>_data; no more
                 AttributeError on the second Load click.
    """

    # Declarative layout: (db_column, header_text, short_attr, grid_row, grid_col)
    # Header labels go at grid_col-1; data labels go at grid_col.
    # Columns 0-1: character stats
    # Columns 2-3: feats / spells / class
    # Columns 4-5: character skills
    _CHAR_LAYOUT = (
        [("stat_strength",     "Strength:",     "str",  0, 1),
         ("stat_dexterity",    "Dexterity:",    "dex",  1, 1),
         ("stat_constitution", "Constitution:", "con",  2, 1),
         ("stat_intelligence", "Intelligence:", "int_", 3, 1),
         ("stat_wisdom",       "Wisdom:",       "wis",  4, 1),
         ("stat_charisma",     "Charisma:",     "cha",  5, 1),
         ("skill_Athletics",        "Athletics:",   "athl", 6, 1),
         ("skill_Mobility",         "Mobility:",    "mobi", 7, 1),
         ("skill_Trickery",         "Trickery:",    "tric", 8, 1),
         ("skill_Stealth",          "Stealth:",     "stel", 9, 1),
         ("skill_Knowledge_Arcana", "Knwl Arcana:", "ka",  10, 1),
         ("skill_Knowledge_World",  "Knwl World:",  "kw",  11, 1)],
        [("skill_Lore_Nature",        "Lore Nature:",      "ln",   0, 3),
         ("skill_Lore_Religion",      "Lore Religion:",    "lr",   1, 3),
         ("skill_Perception",         "Perception:",       "perc", 2, 3),
         ("skill_Persuasion",         "Persuasion:",       "pers", 3, 3),
         ("skill_Use_Magical_Device", "Use Magic Device:", "umd",  4, 3)],
        [("feat_1",       "Feat 1:",       "f1",  0, 5),
         ("feat_2",       "Feat 2:",       "f2",  1, 5),
         ("class_feat_1", "Class Feat 1:", "cf1", 2, 5),
         ("class_feat_2", "Class Feat 2:", "cf2", 3, 5),
         ("spells_1",     "Spells 1:",     "sp1", 4, 5),
         ("spells_2",     "Spells 2:",     "sp2", 5, 5),
         ("spells_3",     "Spells 3:",     "sp3", 6, 5),
         ("c_class",      "Class:",        "cls", 7, 5)],
    )

    # Columns 0-1: mount stats; 2-3: mount feat; 4-5: mount skills
    _MT_LAYOUT = (
        [("mt_stat_strength",     "Mount STR:", "mt_str", 0, 1),
         ("mt_stat_dexterity",    "Mount DEX:", "mt_dex", 1, 1),
         ("mt_stat_constitution", "Mount CON:", "mt_con", 2, 1),
         ("mt_stat_intelligence", "Mount INT:", "mt_int", 3, 1),
         ("mt_stat_wisdom",       "Mount WIS:", "mt_wis", 4, 1),
         ("mt_stat_charisma",     "Mount CHA:", "mt_cha", 5, 1)],  # Bug #4
        [("mt_feat_1", "Mount Feat:", "mt_f1", 0, 3)],
        [("mt_skill_Athletics",          "Athletics:",        "mt_athl", 0, 5),
         ("mt_skill_Mobility",           "Mobility:",         "mt_mobi", 1, 5),
         ("mt_skill_Trickery",           "Trickery:",         "mt_tric", 2, 5),
         ("mt_skill_Stealth",            "Stealth:",          "mt_stel", 3, 5),
         ("mt_skill_Knowledge_Arcana",   "Knwl Arcana:",      "mt_ka",   4, 5),
         ("mt_skill_Knowledge_World",    "Knwl World:",       "mt_kw",   5, 5),
         ("mt_skill_Lore_Nature",        "Lore Nature:",      "mt_ln",   6, 5),
         ("mt_skill_Lore_Religion",      "Lore Religion:",    "mt_lr",   7, 5),
         ("mt_skill_Perception",         "Perception:",       "mt_perc", 8, 5),
         ("mt_skill_Persuasion",         "Persuasion:",       "mt_pers", 9, 5),
         ("mt_skill_Use_Magical_Device", "Use Magic Device:", "mt_umd", 10, 5)],
    )

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()
        self.populate_names()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        sel = tk.Frame(self, bg=BG)
        sel.pack(fill="x", padx=10, pady=(10, 5))
        self._create_selector_row(sel, row=0)
        make_button(sel, "Load", self.load_data).grid(
            row=0, column=6, padx=10, pady=3)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=5)

        # Scrollable data area
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.data_frame = tk.Frame(canvas, bg=BG)
        self.data_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.data_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        vsb.pack(side="right", fill="y")

        # Static section titles and header labels
        make_label(self.data_frame, "CHARACTER BUILD", title=True).grid(
            row=0, column=0, columnspan=6, sticky="w", padx=5, pady=(5, 2))
        self._place_headers(self._CHAR_LAYOUT, row_offset=1)

        make_label(self.data_frame, "MOUNT", title=True).grid(
            row=20, column=0, columnspan=6, sticky="w", padx=5, pady=(10, 2))
        self._place_headers(self._MT_LAYOUT, row_offset=21)

        make_label(self.data_frame, "Mythic Feat:", bold=True, anchor="e").grid(
            row=35, column=0, sticky="e", padx=5, pady=1)

    def _place_headers(self, layout, row_offset: int) -> None:
        """Create static header labels for a section."""
        for column_group in layout:
            for (_, header, _attr, r, c) in column_group:
                make_label(self.data_frame, header, bold=True, anchor="e").grid(
                    row=r + row_offset, column=c - 1,
                    sticky="e", padx=5, pady=1)

    # ── Data helpers ────────────────────────────────────────────────────────

    def set_data_label(self, attr: str, value, row: int, col: int) -> None:
        """
        Create or update the data-value Label for *attr*.

        Bug #5 fix: labels are stored as ``self.<attr>_data``; previously
        ``self.mt_dexterity`` and ``self.mt_charisma`` were referenced
        without the ``_data`` suffix, causing AttributeError on the second
        Load because the original code also destroyed the widgets.
        """
        widget_attr = f"{attr}_data"
        label = getattr(self, widget_attr, None)
        if label is None or not label.winfo_exists():
            label = tk.Label(
                self.data_frame, bg=BG, fg=FG, font=FONT,
                anchor="w", width=22,
            )
            setattr(self, widget_attr, label)
        display = str(value) if (value is not None and value != "") else "—"
        label.config(text=display)
        label.grid(row=row, column=col, sticky="w", padx=5, pady=1)

    # ── Load action ─────────────────────────────────────────────────────────

    def load_data(self) -> None:
        name = self.name_var.get()
        build_type = self.type_var.get()
        level = self.level_var.get()
        if not name or not build_type or not level:
            messagebox.showwarning(
                "Incomplete", "Select Character Name, Build Type, and Level.")
            return

        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM builds"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                (name, build_type, level),
            ).fetchone()

        if row is None:
            messagebox.showinfo("Not Found",
                                "No build data found for the selected options.")
            return

        # Character fields (row_offset=1 to leave room for section title at 0)
        for column_group in self._CHAR_LAYOUT:
            for (db_col, _hdr, attr, r, c) in column_group:
                self.set_data_label(attr, row[db_col], r + 1, c)

        # Mount fields (row_offset=21)
        for column_group in self._MT_LAYOUT:
            for (db_col, _hdr, attr, r, c) in column_group:
                self.set_data_label(attr, row[db_col], r + 21, c)

        # Mythic feat
        self.set_data_label("mythic_feat", row["mythic_feat"], 35, 1)


# ── Tab 2: View Mythic Feat ───────────────────────────────────────────────────

class LoadMythicPath(BuildSelector):
    """
    'View Mythic Feat' tab.

    Bug #6 fix: load_data now stores the result in ``self.level_1`` rather
    than accessing the module-level ``mythic_frame`` variable which is the
    parent container, not the instance.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.level_1 = None          # data label; created lazily in load_data
        self._build_ui()
        self.populate_names()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        sel = tk.Frame(self, bg=BG)
        sel.pack(fill="x", padx=10, pady=(10, 5))
        self._create_selector_row(sel, row=0)
        make_button(sel, "Load", self.load_data).grid(
            row=0, column=6, padx=10, pady=3)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=5)

        self.result_frame = tk.Frame(self, bg=BG)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=10)

        make_label(self.result_frame, "Mythic Feat:", bold=True, anchor="e").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)

    # ── Override populate_levels to show only mythic-feat rows ──────────────

    def populate_levels(self, event=None) -> None:
        """Only list levels that have a mythic feat recorded."""
        name = self.name_var.get()
        build_type = self.type_var.get()
        self.level_var.set("")
        self.level_combo["values"] = []
        if not name or not build_type:
            return
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT character_level FROM builds"
                " WHERE character_name=? AND build_type=?"         # Bug #11
                "   AND mythic_feat IS NOT NULL"
                " ORDER BY CAST(character_level AS INTEGER)",
                (name, build_type),
            ).fetchall()
        self.level_combo["values"] = [r["character_level"] for r in rows]

    # ── Load action ─────────────────────────────────────────────────────────

    def load_data(self) -> None:
        name = self.name_var.get()
        build_type = self.type_var.get()
        level = self.level_var.get()
        if not name or not build_type or not level:
            messagebox.showwarning(
                "Incomplete", "Select Character Name, Build Type, and Level.")
            return

        with get_connection() as conn:
            row = conn.execute(
                "SELECT mythic_feat FROM builds"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                (name, build_type, level),
            ).fetchone()

        feat = row["mythic_feat"] if row else None

        # Bug #6 fix: create/update self.level_1 (was mythic_frame.level_1)
        if self.level_1 is None or not self.level_1.winfo_exists():
            self.level_1 = make_label(self.result_frame, anchor="w", width=40)
            self.level_1.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.level_1.config(
            text=str(feat) if feat else "— no mythic feat recorded —")


# ── Tab 3: Create a Build ─────────────────────────────────────────────────────

class CreateBuild(BuildSelector):
    """
    'Create a Build' tab.

    Bug #15 fix: create_build/update_build validate that stat/skill fields contain
    only numeric (or empty) values before writing to the database.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._entries: dict[str, tk.Widget] = {}
        self._build_ui()
        self.populate_names()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Top selector row — Build Type is writable here (new builds allowed)
        sel = tk.Frame(self, bg=BG)
        sel.pack(fill="x", padx=10, pady=(10, 5))

        make_label(sel, "Character Name:", bold=True).grid(
            row=0, column=0, sticky="e", **PAD)
        self.name_combo = ttk.Combobox(sel, textvariable=self.name_var, width=25)
        self.name_combo.grid(row=0, column=1, sticky="w", **PAD)
        self.name_combo.bind("<<ComboboxSelected>>", self.populate_types)

        make_label(sel, "Build Type:", bold=True).grid(
            row=0, column=2, sticky="e", **PAD)
        self.type_combo = ttk.Combobox(sel, textvariable=self.type_var, width=25)
        self.type_combo.grid(row=0, column=3, sticky="w", **PAD)
        self.type_combo.bind("<<ComboboxSelected>>", self.populate_levels)

        make_label(sel, "Character Level:", bold=True).grid(
            row=0, column=4, sticky="e", **PAD)
        self.level_combo = ttk.Combobox(
            sel, textvariable=self.level_var, width=8,
            values=[str(i) for i in range(1, 41)])
        self.level_combo.grid(row=0, column=5, sticky="w", **PAD)

        make_button(sel, "Create Build", self.create_build).grid(
            row=0, column=6, padx=10, pady=3)
        make_button(sel, "Load Build", self.load_build).grid(
            row=0, column=7, padx=5, pady=3)
        make_button(sel, "Update Build", self.update_build).grid(
            row=0, column=8, padx=5, pady=3)
        make_button(sel, "Clear", self._clear_fields).grid(
            row=0, column=9, padx=5, pady=3)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=5)

        # Scrollable input area
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        vsb.pack(side="right", fill="y")

        # Build input grid sections
        make_label(inner, "CHARACTER STATS & SKILLS", title=True).grid(
            row=0, column=0, columnspan=2, sticky="w", **PAD)
        make_label(inner, "CHARACTER SKILLS", title=True).grid(
            row=0, column=2, columnspan=2, sticky="w", **PAD)
        make_label(inner, "FEATS / SPELLS / CLASS", title=True).grid(
            row=0, column=4, columnspan=2, sticky="w", **PAD)

        row = 1
        row = self._add_field_group(inner, STAT_FIELDS, start_row=row, col_offset=0)
        self._add_field_group(
            inner, SKILL_FIELDS[:FIRST_COLUMN_SKILL_COUNT], start_row=row, col_offset=0)
        self._add_field_group(
            inner, SKILL_FIELDS[FIRST_COLUMN_SKILL_COUNT:], start_row=1, col_offset=2)
        self._add_field_group(inner, OTHER_FIELDS, start_row=1, col_offset=4)

        mount_title_row = 14
        make_label(inner, "MOUNT STATS & SKILLS", title=True).grid(
            row=mount_title_row, column=0, columnspan=2, sticky="w", **PAD)
        make_label(inner, "MOUNT SKILLS", title=True).grid(
            row=mount_title_row, column=2, columnspan=2, sticky="w", **PAD)
        make_label(inner, "MOUNT FEAT / MYTHIC", title=True).grid(
            row=mount_title_row, column=4, columnspan=2, sticky="w", **PAD)

        row = mount_title_row + 1
        row = self._add_field_group(inner, MT_STAT_FIELDS, start_row=row, col_offset=0)
        self._add_field_group(
            inner, MT_SKILL_FIELDS[:FIRST_COLUMN_SKILL_COUNT], start_row=row, col_offset=0)
        self._add_field_group(
            inner, MT_SKILL_FIELDS[FIRST_COLUMN_SKILL_COUNT:], start_row=row, col_offset=2)
        self._add_field_group(
            inner,
            CREATE_BUILD_EXTRA_FIELDS,
            start_row=mount_title_row + 1, col_offset=4)

    def _add_field_group(self, parent, fields, start_row: int,
                         col_offset: int) -> int:
        """Place label+entry pairs and register entries in self._entries."""
        for i, (db_col, header, attr) in enumerate(fields):
            r = start_row + i
            make_label(parent, header, bold=True, anchor="e").grid(
                row=r, column=col_offset, sticky="e", **PAD)
            entry = tk.Entry(parent, bg=ACCENT, fg=FG, font=FONT,
                             insertbackground=FG, width=22)
            entry.grid(row=r, column=col_offset + 1, sticky="w", **PAD)
            self._entries[db_col] = entry
        return start_row + len(fields)

    # ── Actions ─────────────────────────────────────────────────────────────

    def _clear_fields(self) -> None:
        for entry in self._entries.values():
            entry.delete(0, tk.END)

    def _get_values(self) -> dict[str, str]:
        return {col: entry.get().strip()
                for col, entry in self._entries.items()}

    def _get_build_identity(self, *, strict: bool = False) -> tuple[str, str, str] | None:
        name = self.name_var.get().strip()
        build_type = self.type_var.get().strip()
        level = self.level_var.get().strip()

        if not name or not build_type or not level:
            dialog = messagebox.showerror if strict else messagebox.showwarning
            dialog(
                "Missing Required Fields" if strict else "Incomplete",
                "Character Name, Build Type, and Level are required.",
            )
            return None
        return name, build_type, level

    def _validate_values(self) -> dict[str, str] | None:
        """
        Validate inputs before writing the builds row.
        Bug #15 fix: stat and skill fields must be numeric or empty.
        """
        values = self._get_values()
        bad_fields = []
        for col, val in values.items():
            if col in NUMERIC_DB_COLS and val != "":
                try:
                    float(val)
                except ValueError:
                    bad_fields.append(col)
        if bad_fields:
            messagebox.showerror(
                "Invalid Input",
                "The following fields must be numeric (or empty):\n"
                + "\n".join(bad_fields),
            )
            return None
        return values

    def _set_entry_value(self, db_col: str, value) -> None:
        entry = self._entries[db_col]
        entry.delete(0, tk.END)
        if value is not None:
            entry.insert(0, str(value))

    def load_build(self) -> None:
        identity = self._get_build_identity(strict=True)
        if identity is None:
            return
        name, build_type, level = identity

        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM builds"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                (name, build_type, level),
            ).fetchone()

        if row is None:
            messagebox.showerror(
                "Not Found",
                "No build data found for the selected Character Name, Build Type, and Level.",
            )
            return

        for db_col, *_ in CREATE_BUILD_FIELDS:
            self._set_entry_value(db_col, row[db_col])

    def create_build(self) -> None:
        identity = self._get_build_identity()
        if identity is None:
            return
        name, build_type, level = identity
        values = self._validate_values()
        if values is None:
            return

        cols = list(values.keys())
        vals = [values[c] or None for c in cols]
        placeholders = ", ".join("?" * len(cols))
        col_names = ", ".join(cols)

        with get_connection() as conn:
            existing = conn.execute(
                "SELECT rowid FROM builds"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                (name, build_type, level),
            ).fetchone()

            if existing:
                messagebox.showerror(
                    "Build Exists",
                    f"A build already exists for {name} — {build_type} level {level}. "
                    "Use Update Build to modify it.",
                )
                return

            conn.execute(
                f"INSERT INTO builds (character_name, build_type,"
                f" character_level, {col_names})"
                f" VALUES (?, ?, ?, {placeholders})",
                [name, build_type, level] + vals,
            )

        messagebox.showinfo("Created", f"Build created for {name} — {build_type}"
                            f" level {level}.")
        BuildSelector.refresh_all_selectors()

    def update_build(self) -> None:
        identity = self._get_build_identity()
        if identity is None:
            return
        name, build_type, level = identity
        values = self._validate_values()
        if values is None:
            return

        cols = list(values.keys())
        vals = [values[c] or None for c in cols]
        set_clause = ", ".join(f"{c}=?" for c in cols)

        with get_connection() as conn:
            existing = conn.execute(
                "SELECT rowid FROM builds"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                (name, build_type, level),
            ).fetchone()
            if existing is None:
                messagebox.showerror(
                    "Not Found",
                    "No build data found for the selected Character Name, Build Type, and Level.",
                )
                return

            if not messagebox.askyesno(
                "Confirm Update",
                f"Are you sure you want to update {name} — {build_type} level {level}?",
            ):
                return

            conn.execute(
                f"UPDATE builds SET {set_clause}"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                vals + [name, build_type, level],
            )

        messagebox.showinfo("Updated", f"Build updated for {name} — {build_type}"
                            f" level {level}.")
        BuildSelector.refresh_all_selectors()


# ── Tab 4: Add/Update Mythic Feat ────────────────────────────────────────────

class AddMythicFeat(BuildSelector):
    """
    'Add/Update Mythic Feat' tab.

    Bug #13 fix: method first-parameter is ``self``.
    Bug #14 fix: StringVar is ``self.mp_var`` (was ``self.mp__var``).
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.mp_var = tk.StringVar()   # Bug #14 fix: was mp__var
        self._build_ui()
        self.populate_names()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        sel = tk.Frame(self, bg=BG)
        sel.pack(fill="x", padx=10, pady=(10, 5))
        self._create_selector_row(sel, row=0)

        inner = tk.Frame(self, bg=BG)
        inner.pack(fill="both", expand=True, padx=20, pady=10)

        make_label(inner, "Mythic Feat:", bold=True, anchor="e").grid(
            row=0, column=0, sticky="e", **PAD)
        self.mp_combo = ttk.Combobox(inner, textvariable=self.mp_var, width=35)
        self.mp_combo.grid(row=0, column=1, sticky="w", **PAD)

        make_button(inner, "Add Mythic Feat", self.save_feat).grid(
            row=1, column=0, columnspan=2, pady=10)

        # Populate the feat dropdown with values already in the database
        self.level_combo.bind("<<ComboboxSelected>>",
                              self._on_level_selected)

    def _on_level_selected(self, event=None) -> None:
        """Chain the base populate_levels then refresh the feat list."""
        self.populate_levels(event)
        self._populate_feats()

    def _populate_feats(self) -> None:
        """Load existing mythic feat values from the DB into the combobox."""
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT mythic_feat FROM builds"
                " WHERE mythic_feat IS NOT NULL"
                " ORDER BY mythic_feat"
            ).fetchall()
        self.mp_combo["values"] = [r["mythic_feat"] for r in rows]

    # ── Action ──────────────────────────────────────────────────────────────

    def save_feat(self) -> None:
        name = self.name_var.get().strip()
        build_type = self.type_var.get().strip()
        level = self.level_var.get().strip()
        feat = self.mp_var.get().strip()

        if not name or not build_type or not level or not feat:
            messagebox.showwarning("Incomplete", "All fields are required.")
            return

        with get_connection() as conn:
            existing = conn.execute(
                "SELECT rowid FROM builds"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                (name, build_type, level),
            ).fetchone()

            if existing:
                conn.execute(
                    "UPDATE builds SET mythic_feat=?"
                    " WHERE character_name=? AND build_type=? AND character_level=?",
                    (feat, name, build_type, level),
                )
            else:
                conn.execute(
                    "INSERT INTO builds (character_name, build_type,"
                    " character_level, mythic_feat) VALUES (?, ?, ?, ?)",
                    (name, build_type, level, feat),
                )

        messagebox.showinfo("Saved",
                            f"Mythic feat '{feat}' saved for {name}"
                            f" — {build_type} level {level}.")
        BuildSelector.refresh_all_selectors()


# ── Tab 5: Delete a Build ─────────────────────────────────────────────────────

class DeleteBuild(BuildSelector):
    """'Delete a Build' tab."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()
        self.populate_names()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        sel = tk.Frame(self, bg=BG)
        sel.pack(fill="x", padx=10, pady=(10, 5))
        self._create_selector_row(sel, row=0)

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=20)

        make_button(btn_frame, "Delete Level",
                    self.delete_level).grid(row=0, column=0, padx=10)
        make_button(btn_frame, "Delete Entire Build",
                    self.delete_build).grid(row=0, column=1, padx=10)
        make_button(btn_frame, "Delete All Character Builds",
                    self.delete_character).grid(row=0, column=2, padx=10)
        make_button(btn_frame, "Clear",
                    self._clear).grid(row=0, column=3, padx=10)

    # ── Actions ─────────────────────────────────────────────────────────────

    def _clear(self) -> None:
        self.name_var.set("")
        self.type_var.set("")
        self.level_var.set("")

    def delete_level(self) -> None:
        name = self.name_var.get()
        build_type = self.type_var.get()
        level = self.level_var.get()
        if not name or not build_type or not level:
            messagebox.showwarning("Incomplete",
                                   "Select Name, Build Type, and Level.")
            return
        if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete level {level} of '{build_type}' for {name}?"):
            return
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM builds"
                " WHERE character_name=? AND build_type=? AND character_level=?",
                (name, build_type, level),
            )
        messagebox.showinfo("Deleted", "Level deleted.")
        BuildSelector.refresh_all_selectors()
        self._clear()

    def delete_build(self) -> None:
        name = self.name_var.get()
        build_type = self.type_var.get()
        if not name or not build_type:
            messagebox.showwarning("Incomplete", "Select Name and Build Type.")
            return
        if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete ALL levels of '{build_type}' for {name}?"):
            return
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM builds WHERE character_name=? AND build_type=?",
                (name, build_type),
            )
        messagebox.showinfo("Deleted", "Build deleted.")
        BuildSelector.refresh_all_selectors()
        self._clear()

    def delete_character(self) -> None:
        name = self.name_var.get()
        if not name:
            messagebox.showwarning("Incomplete", "Select a Character Name.")
            return
        if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete ALL builds for {name}? This cannot be undone."):
            return
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM builds WHERE character_name=?", (name,))
        messagebox.showinfo("Deleted", "All builds deleted.")
        BuildSelector.refresh_all_selectors()
        self._clear()


# ── Tab 6: Delete Mythic Feat ────────────────────────────────────────────────

class MythicFeatDelete(BuildSelector):
    """
    'Delete Mythic Feat' tab.

    Bug #7  fix: removed ``clear_dropdowns`` entirely; clearing is handled by
                 the base-class ``populate_types`` / ``populate_levels``.
    Bug #8  fix: the feat combobox is NOT bound to ``populate_levels``.
    Bug #9  fix: populate_feats excludes NULL rows.
    Bug #10 fix: delete button now reads "Delete Mythic Feat"; all four fields
                 are validated before deleting.
    Bug #11 fix: populate_levels filters by character_name AND build_type.
    Bug #13 fix: method first-parameter is ``self``.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.feat_var = tk.StringVar()
        self.feat_combo = None
        self._build_ui()
        self.populate_names()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        sel = tk.Frame(self, bg=BG)
        sel.pack(fill="x", padx=10, pady=(10, 5))
        self._create_selector_row(sel, row=0)

        # Bind level combobox to populate the 4th (feat) dropdown
        self.level_combo.bind("<<ComboboxSelected>>", self._on_level_selected)

        # 4th combobox: Mythic Feat
        make_label(sel, "Mythic Feat:", bold=True).grid(
            row=1, column=0, sticky="e", **PAD)
        self.feat_combo = ttk.Combobox(
            sel, textvariable=self.feat_var, width=35, state="readonly")
        self.feat_combo.grid(row=1, column=1, columnspan=3, sticky="w", **PAD)
        # Bug #8 fix: feat combobox is NOT bound to populate_levels

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=20)
        # Bug #10 fix: label is "Delete Mythic Feat" (was "Delete Build")
        make_button(btn_frame, "Delete Mythic Feat",
                    self.delete_feat).grid(row=0, column=0, padx=10)
        make_button(btn_frame, "Clear",
                    self._clear).grid(row=0, column=1, padx=10)

    # ── Override populate_levels ────────────────────────────────────────────

    def populate_types(self, event=None) -> None:
        """Chain base implementation and also reset the feat combobox."""
        super().populate_types(event)
        self.feat_var.set("")
        if self.feat_combo:
            self.feat_combo["values"] = []

    def populate_levels(self, event=None) -> None:
        """
        Show only levels that have a mythic feat (Bug #11 includes name filter).
        Also reset the feat combobox.
        """
        name = self.name_var.get()
        build_type = self.type_var.get()
        self.level_var.set("")
        self.level_combo["values"] = []
        self.feat_var.set("")
        if self.feat_combo:
            self.feat_combo["values"] = []
        if not name or not build_type:
            return
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT character_level FROM builds"
                " WHERE character_name=? AND build_type=?"   # Bug #11
                "   AND mythic_feat IS NOT NULL"
                " ORDER BY CAST(character_level AS INTEGER)",
                (name, build_type),
            ).fetchall()
        self.level_combo["values"] = [r["character_level"] for r in rows]

    def _on_level_selected(self, event=None) -> None:
        """Level chosen → populate the feat dropdown."""
        self.populate_feats()

    def populate_feats(self) -> None:
        """
        Populate the mythic-feat combobox for the current name/type/level.
        Bug #9  fix: AND mythic_feat IS NOT NULL
        Bug #11 fix: filter by character_name too
        """
        name = self.name_var.get()
        build_type = self.type_var.get()
        level = self.level_var.get()
        self.feat_var.set("")
        if self.feat_combo:
            self.feat_combo["values"] = []
        if not name or not build_type or not level:
            return
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT mythic_feat FROM builds"
                " WHERE character_name=? AND build_type=?"   # Bug #11
                "   AND character_level=?"
                "   AND mythic_feat IS NOT NULL",             # Bug #9
                (name, build_type, level),
            ).fetchall()
        if self.feat_combo:
            self.feat_combo["values"] = [r["mythic_feat"] for r in rows]

    # ── Actions ─────────────────────────────────────────────────────────────

    def _clear(self) -> None:
        self.name_var.set("")
        self.type_var.set("")
        self.level_var.set("")
        self.feat_var.set("")
        if self.feat_combo:
            self.feat_combo["values"] = []

    def delete_feat(self) -> None:
        """
        Delete (set to NULL) the selected mythic feat.
        Bug #10 fix: validates all four fields are selected.
        """
        name = self.name_var.get()
        build_type = self.type_var.get()
        level = self.level_var.get()
        feat = self.feat_var.get()

        # Bug #10 fix: validate all fields
        if not name or not build_type or not level or not feat:
            messagebox.showwarning(
                "Incomplete",
                "Select Character Name, Build Type, Level, and Mythic Feat.")
            return

        if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete mythic feat '{feat}' for {name} — {build_type}"
                f" level {level}?"):
            return

        with get_connection() as conn:
            conn.execute(
                "UPDATE builds SET mythic_feat=NULL"
                " WHERE character_name=? AND build_type=?"
                "   AND character_level=? AND mythic_feat=?",
                (name, build_type, level, feat),
            )

        messagebox.showinfo("Deleted", f"Mythic feat '{feat}' removed.")
        BuildSelector.refresh_all_selectors()
        self._clear()


# ── Window geometry ───────────────────────────────────────────────────────────

def load_window_coords(root: tk.Tk) -> None:
    """Restore window position from the previous session, if available."""
    try:
        with open(resource_path(COORDS_PATH)) as fh:
            x, y = fh.read().strip().split(",")
            root.geometry(f"+{int(x)}+{int(y)}")
    except (FileNotFoundError, ValueError, OSError):
        pass  # Use OS default position


def on_close(root: tk.Tk) -> None:
    """
    Save window position and close.
    Bug #12 fix: os.makedirs guards against a missing 'data' directory so the
    window always closes even on the very first run.
    """
    try:
        os.makedirs("data", exist_ok=True)   # Bug #12 fix
        with open(resource_path(COORDS_PATH), "w") as fh:
            fh.write(f"{root.winfo_x()},{root.winfo_y()}")
    except OSError:
        pass  # Never block window close due to I/O error
    finally:
        root.destroy()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    init_db()

    root = tk.Tk()
    root.title("Pathfinder: Wrath of the Righteous — Build Tool")
    root.configure(bg=BG)
    root.geometry("1100x700")
    root.minsize(900, 600)

    apply_styles(root)
    load_window_coords(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)

    # ── Create the six tabs in the specified order ───────────────────────────
    tabs = [
        ("View a Build",          LoadBuilds),
        ("View Mythic Feat",      LoadMythicPath),
        ("Create a Build",        CreateBuild),
        ("Add/Update Mythic Feat", AddMythicFeat),
        ("Delete a Build",        DeleteBuild),
        ("Delete Mythic Feat",    MythicFeatDelete),
    ]
    for title, cls in tabs:
        frame = cls(notebook)
        notebook.add(frame, text=title)

    def _refresh_current_tab(event=None):
        """Refresh current tab selectors when a notebook tab is selected."""
        tab_id = notebook.select()
        if tab_id:
            frame = notebook.nametowidget(tab_id)
            if isinstance(frame, BuildSelector):
                frame.refresh_names()

    notebook.bind("<<NotebookTabChanged>>", _refresh_current_tab)

    root.mainloop()


if __name__ == "__main__":
    main()
