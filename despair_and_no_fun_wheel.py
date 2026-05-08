"""
HOW IT WORKS
─────────────────────────
  _build_ui()          builds every button, canvas, and label once at startup
  _loop()              runs ~60 times per second — the heartbeat of the app
  _tick_spin()         moves the wheel each frame (updates angle & velocity)
  _draw_wheel()        redraws the wheel + event banner overlay each frame
  _draw_stickman()     shows PNG image OR falls back to drawn stick figure
  _next_event()        pops the next chaos event from the queue and sets it up
  _run_event()         executes one frame of the active chaos event
  _finish()            called once when the wheel stops — picks the winner

PNG STICKMAN — place images in a stickman/ folder next to this file.

  REQUIRED (app falls back to drawn stickman if any are missing):
    stickman/idle.png
    stickman/excited.png
    stickman/shocked.png
    stickman/victory.png

  OPTIONAL per-event (falls back to the base state above if missing):
    stickman/stutter.png
    stickman/reverse.png
    stickman/slowdown_burst.png
    stickman/fake_stop.png
    stickman/speed_burst.png
    stickman/almost_there.png
    stickman/earthquake.png
    stickman/warp_speed.png
    stickman/indecision.png
    stickman/gravity_fight.png
    stickman/dead_stop.png
    stickman/start.png
    stickman/winner.png
"""

import tkinter as tk
import math
import random
import os

# ══════════════════════════════════════════════════════════════════════════════
#  COLOURS
# ══════════════════════════════════════════════════════════════════════════════

COLORS = [
    "#FF3366", "#FF6B35", "#FFD700", "#00C853",
    "#00BCD4", "#7C4DFF", "#FF4081", "#76FF03",
    "#FF9100", "#40C4FF", "#E040FB", "#CCFF90",
    "#FF5252", "#EEFF41", "#F06292", "#80CBC4",
    "#FFAB40", "#B39DDB", "#80DEEA", "#A5D6A7",
    "#FF8A65", "#90CAF9", "#CE93D8", "#FFF176",
    "#BCAAA4", "#EF9A9A", "#80CBC4", "#C5E1A5",
    "#FFE082", "#B0BEC5", "#F48FB1", "#AED581",
    "#FFD54F", "#4FC3F7", "#BA68C8", "#DCE775",
    "#FF7043", "#26C6DA", "#AB47BC", "#D4E157",
]

# ══════════════════════════════════════════════════════════════════════════════
#  EFFECT INFO
#  display  : banner text when the event fires
#  color    : banner background colour
#  duration : (min_frames, max_frames) — scaled by the spin multiplier
#  stick    : BASE state fallback ("idle"/"excited"/"shocked"/"victory")
#             Used when no event-specific PNG exists (e.g. no earthquake.png)
# ══════════════════════════════════════════════════════════════════════════════

EFFECT_INFO = {
    "stutter": {
        "display":  "⚡  S T U T T E R I N G !",
        "color":    "#FF9100",
        "duration": (100, 160),
        "stick":    "shocked",
    },
    "reverse": {
        "display":  "⏪  R E V E R S E !",
        "color":    "#7C4DFF",
        "duration": (120, 180),
        "stick":    "shocked",
    },
    "slowdown_burst": {
        "display":  "🐌  S L O W . . .  P S Y C H !",
        "color":    "#FF3366",
        "duration": (140, 200),
        "stick":    "shocked",
    },
    "fake_stop": {
        "display":  "🛑  F A K E   S T O P !",
        "color":    "#FFD700",
        "duration": (160, 230),
        "stick":    "shocked",
    },
    "speed_burst": {
        "display":  "🚀  S P E E D   B U R S T !",
        "color":    "#00C853",
        "duration": (90, 130),
        "stick":    "excited",
    },
    "almost_there": {
        "display":  "😰  A L M O S T . . .",
        "color":    "#00BCD4",
        "duration": (200, 320),
        "stick":    "idle",
    },
    "earthquake": {
        "display":  "🌋  E A R T H Q U A K E !",
        "color":    "#BF360C",
        "duration": (120, 180),
        "stick":    "shocked",
    },
    "warp_speed": {
        "display":  "🌀  W A R P   S P E E D !",
        "color":    "#E040FB",
        "duration": (80, 120),
        "stick":    "excited",
    },
    "indecision": {
        "display":  "🤔  I N D E C I S I O N !",
        "color":    "#F06292",
        "duration": (160, 240),
        "stick":    "shocked",
    },
    "gravity_fight": {
        "display":  "💪  F I G H T I N G   G R A V I T Y !",
        "color":    "#26C6DA",
        "duration": (140, 200),
        "stick":    "shocked",
    },
    "dead_stop": {
        "display":  "💀  D E A D   S T O P .",
        "color":    "#222222",
        "duration": (1, 1),
        "stick":    "shocked",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
#  NARRATIONS
# ══════════════════════════════════════════════════════════════════════════════

NARRATIONS = {
    "start": [
        "HERE WE GO!!",
        "LET'S DO THIS!",
        "MAY THE ODDS\nBE IN YOUR FAVOR!",
        "AND THE WHEEL\nSPINS!",
        "HOLD ON TO\nYOUR HATS!!!",
    ],
    "stutter": [
        "WHAT IS IT\nDOING?!",
        "THE WHEEL IS\nHICCUPING!",
        "IS IT BROKEN?!",
        "IT'S STUTTERING!!",
        "SOMEONE CALL\nA MECHANIC!",
    ],
    "reverse": [
        "WAIT,\nBACKWARDS?!",
        "REVERSE!\nREVERSE!",
        "WHO INSTALLED\nTHIS THING?!",
        "NOPE,\nOTHER WAY!!",
        "GOING BACK\nIN TIME?!",
    ],
    "slowdown_burst": [
        "It's slowing...\nPSYCH!!!",
        "GOTCHA!\nFULL SPEED AHEAD!",
        "FAKE OUT!!!",
        "NOT DONE YET!!",
    ],
    "fake_stop": [
        "It's... wait NO!",
        "Almost... NOPE!\nKEEP GOING!",
        "THE WHEEL\nSAID NO!",
        "NOT TODAY!!",
        "DENIED!!!",
    ],
    "speed_burst": [
        "TURBO MODE!!!",
        "SPEED BOOST!!!",
        "ZOOM ZOOM!!!",
        "SUPERSONIC!!",
        "GO GO GO!!!",
    ],
    "almost_there": [
        "So close...",
        "I can feel it...",
        "Holding my\nbreath...",
        "Any second\nnow...",
        "Come on...",
    ],
    "earthquake": [
        "THE GROUND\nSHAKES!!!",
        "EARTHQUAKE!!!",
        "HOLD ON TIGHT!!",
        "MAGNITUDE 10!!!",
        "IT'S GOING\nCRAZY!!!",
    ],
    "warp_speed": [
        "LIGHT SPEED!!!",
        "WARP FACTOR 9!!!",
        "TOO FAST TO SEE!!",
        "HYPERDRIVE!!!",
        "ENGAGE!!!",
    ],
    "indecision": [
        "IT CAN'T\nDECIDE!!!",
        "MAKE UP YOUR\nMIND!!!",
        "YES? NO? YES?!",
        "SO INDECISIVE!!!",
        "COMMIT!!!!!",
    ],
    "gravity_fight": [
        "FIGHTING\nGRAVITY!!!",
        "NOT YET!!!",
        "IT'S STRUGGLING!!",
        "COME ON,\nKEEP GOING!",
        "PUSH THROUGH!!!",
    ],
    "dead_stop": [
        "...",
        "oh.",
        "just\nstops.",
        "yep.\nthat's it.",
        "no drama.\njust done.",
    ],
    "winner": [
        "WE HAVE A\nWINNER!!!",
        "CONGRATULATIONS!!",
        "DESTINY HAS\nSPOKEN!",
        "THE WHEEL\nHAS DECIDED!",
        "AND THE WINNER\nIS...",
    ],
    "idle": [
        "Ready when\nyou are!",
        "Add names\nand spin!",
        "Just standing\nhere...",
        "Waiting\npatiently...",
        "Let's spin!!",
        "Who will it\nbe today?",
    ],
}

MAX_ITEMS = 40


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION CLASS
# ══════════════════════════════════════════════════════════════════════════════

class SpinWheelApp:

    CANVAS_SIZE = 900
    CX = 450
    CY = 450
    R  = 415

    def __init__(self, root):
        self.root = root
        self.root.title("mr chung's wheel of saddness and despair")
        self.root.configure(bg="#0d0d1a")

        self.items = ["me", "myself", "I", "yours truly", "that guy", "him"]

        self.angle    = 0.0
        self.vel      = 0.0
        self.spinning = False
        self.winner   = None

        self.phase     = "idle"
        self.chaos_q   = []
        self.cur_event = None
        self.c_frame   = 0
        self.c_dur     = 0

        # stick_state holds either an event name (e.g. "earthquake") or a base
        # state name ("idle", "excited", "shocked", "victory").
        # _draw_stickman_png resolves it with a fallback chain.
        self.stick_state       = "idle"
        self.stick_lock_frames = 0    # image won't change until this hits 0
        self.anim_f            = 0
        self.narr_timer        = 0

        self.flash_col = None
        self.flash_f   = 0

        self.banner_text   = ""
        self.banner_color  = "#FFD700"
        self.banner_frames = 0

        self.effect_vars = {
            name: tk.BooleanVar(value=True) for name in EFFECT_INFO
        }
        self.spin_mult  = tk.DoubleVar(value=1.0)
        self.max_events = tk.IntVar(value=2)

        self.png_images = {}
        self._load_stickman_images()

        self._build_ui()
        self._loop()

    # ────────────────────────────────────────────────────────────────────────
    #  PNG LOADING
    #  BUG FIX 1: now loads event-specific PNGs in addition to the 4 base states.
    # ────────────────────────────────────────────────────────────────────────

    def _load_stickman_images(self):
        """
        Load PNGs from the stickman/ folder.

        Step 1 — load 4 required base states.
                  If any are missing, fall back to the drawn stickman entirely.
        Step 2 — try to load one optional PNG per event name (and start/winner).
                  Missing optional files are silently skipped.
        """
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stickman")
        loaded = {}

        # ── Step 1: required base states ────────────────────────────────────
        base_states = ["idle", "excited", "shocked", "victory"]
        for state in base_states:
            path = os.path.join(folder, f"{state}.png")
            if not os.path.exists(path):
                print(f"[stickman] Required image missing: {path}")
                print("[stickman] Falling back to drawn stickman.")
                self.png_images = {}
                return
            try:
                loaded[state] = tk.PhotoImage(file=path)
            except Exception as e:
                print(f"[stickman] Error loading {path}: {e}")
                print("[stickman] Falling back to drawn stickman.")
                self.png_images = {}
                return

        # ── Step 2: optional per-event images ───────────────────────────────
        # One slot per event key, plus "start" and "winner" for special moments.
        optional_slots = list(EFFECT_INFO.keys()) + ["start", "winner"]
        for slot in optional_slots:
            path = os.path.join(folder, f"{slot}.png")
            if os.path.exists(path):
                try:
                    loaded[slot] = tk.PhotoImage(file=path)
                    print(f"[stickman] Loaded optional: {slot}.png")
                except Exception as e:
                    print(f"[stickman] Could not load optional {slot}.png: {e}")

        self.png_images = loaded
        n_opt = len(loaded) - len(base_states)
        print(f"[stickman] Ready — {len(base_states)} base + {n_opt} optional images.")

    # ────────────────────────────────────────────────────────────────────────
    #  _set_stick  — the ONLY place stick_state should be changed.
    #
    #  BUG FIX 2: previously stick_state was always set to the base state name
    #  (e.g. "shocked") so event-specific images could never be found.
    #  Now it stores the event name (e.g. "earthquake") and _draw_stickman_png
    #  resolves it through a fallback chain.
    #
    #  The lock prevents rapid flicker — once changed, the image stays for
    #  at least 180 frames (~3 seconds at 60 fps).
    #  Pass force=True to bypass the lock (winner, dead_stop, idle resets).
    # ────────────────────────────────────────────────────────────────────────

    def _set_stick(self, state, force=False):
        if self.stick_lock_frames > 0 and not force:
            return
        self.stick_state       = state
        self.stick_lock_frames = 180   # 180 × 16 ms ≈ 3 seconds

    # ────────────────────────────────────────────────────────────────────────
    #  UI
    # ────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.geometry("1920x1080")

        top_row = tk.Frame(self.root, bg="#0d0d1a")
        top_row.pack(side="top", fill="x", padx=20, pady=(10, 0))

        tk.Label(
            top_row,
            text = "M R . C H U N G ' S  W H E E L  O F  H A P P I N E S S  A N D  J O Y",
            font = ("Courier", 28, "bold"),
            fg   = "#FFD700",
            bg   = "#0d0d1a",
        ).pack(side="left")

        tk.Button(
            top_row,
            text             = "⚙  Settings",
            font             = ("Courier", 13, "bold"),
            fg               = "#fff",
            bg               = "#1a1a3a",
            activebackground = "#2a2a4a",
            relief           = "flat",
            padx             = 16,
            pady             = 6,
            cursor           = "hand2",
            command          = self.open_settings,
        ).pack(side="right", padx=(0, 4))

        body = tk.Frame(self.root, bg="#0d0d1a")
        body.pack(side="top", fill="both", expand=True, padx=16, pady=10)

        left = tk.Frame(body, bg="#0d0d1a")
        left.pack(side="left", anchor="n")

        self.wcv = tk.Canvas(
            left,
            width              = self.CANVAS_SIZE,
            height             = self.CANVAS_SIZE,
            bg                 = "#0d0d1a",
            highlightthickness = 0,
        )
        self.wcv.pack()

        right = tk.Frame(body, bg="#0d0d1a")
        right.pack(side="left", anchor="n", fill="both", expand=True, padx=(24, 0))

        stick_row = tk.Frame(right, bg="#0d0d1a")
        stick_row.pack(fill="x", pady=(0, 12))

        self.speech = tk.Label(
            stick_row,
            text       = "Ready when\nyou are!",
            font       = ("Courier", 16, "bold"),
            fg         = "#fff",
            bg         = "#1a1a3a",
            justify    = "center",
            padx       = 18,
            pady       = 14,
            relief     = "ridge",
            bd         = 3,
            width      = 22,
            wraplength = 320,
        )
        self.speech.pack(side="left", padx=(0, 20), anchor="center")

        self.scv = tk.Canvas(
            stick_row,
            width               = 340,
            height              = 420,
            bg                  = "#80c3db",
            highlightthickness  = 2,
            highlightbackground = "#2a2a4a",
        )
        self.scv.pack(side="left", anchor="n")

        ctrl = tk.Frame(right, bg="#0d0d1a")
        ctrl.pack(fill="x", pady=(0, 12))

        self.sbtn = tk.Button(
            ctrl,
            text             = "S P I N !",
            font             = ("Courier", 26, "bold"),
            fg               = "#fff",
            bg               = "#FF3366",
            activebackground = "#cc2255",
            relief           = "flat",
            padx             = 30,
            pady             = 14,
            cursor           = "hand2",
            command          = self.start_spin,
        )
        self.sbtn.pack(side="left", padx=(0, 16))

        self.wlbl = tk.Label(
            ctrl,
            text       = "",
            font       = ("Courier", 20, "bold"),
            fg         = "#FFD700",
            bg         = "#0d0d1a",
            wraplength = 500,
            justify    = "left",
        )
        self.wlbl.pack(side="left")

        self.rbtn = tk.Button(
            right,
            text             = "✕  Remove Winner from Wheel",
            font             = ("Courier", 13),
            fg               = "#FF3366",
            bg               = "#1a1a3a",
            activebackground = "#2a2a4a",
            relief           = "flat",
            pady             = 7,
            cursor           = "hand2",
            command          = self.remove_winner,
            state            = "disabled",
        )
        self.rbtn.pack(fill="x", pady=(0, 16))

        panel = tk.Frame(right, bg="#13132a", relief="ridge", bd=1)
        panel.pack(fill="both", expand=True)

        hdr = tk.Frame(panel, bg="#13132a")
        hdr.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(hdr, text="ITEMS", font=("Courier", 14, "bold"),
                 fg="#888", bg="#13132a").pack(side="left")
        self.count_lbl = tk.Label(
            hdr,
            text = f"({len(self.items)}/{MAX_ITEMS})",
            font = ("Courier", 12),
            fg   = "#555",
            bg   = "#13132a",
        )
        self.count_lbl.pack(side="left", padx=8)

        list_frame = tk.Frame(panel, bg="#13132a")
        list_frame.pack(fill="both", expand=True, padx=14)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.lb = tk.Listbox(
            list_frame,
            font             = ("Courier", 13),
            fg               = "#fff",
            bg               = "#0d0d1a",
            selectbackground = "#FF3366",
            height           = 10,
            width            = 50,
            yscrollcommand   = scrollbar.set,
            relief           = "flat",
        )
        self.lb.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.lb.yview)
        for name in self.items:
            self.lb.insert("end", name)

        btn_row = tk.Frame(panel, bg="#13132a")
        btn_row.pack(fill="x", padx=14, pady=10)

        self.ent = tk.Entry(
            btn_row,
            font             = ("Courier", 14),
            fg               = "#fff",
            bg               = "#0d0d1a",
            insertbackground = "#fff",
            relief           = "flat",
            bd               = 6,
            width            = 30,
        )
        self.ent.pack(side="left", padx=(0, 8))
        self.ent.bind("<Return>", lambda _: self.add_item())

        for label, color, cmd in [
            ("+  Add",         "#00E676", self.add_item),
            ("✕  Remove",      "#444",    self.remove_selected),
            ("📋  Paste List", "#1a1a3a", self.open_paste_dialog),
            ("🗑  Remove All", "#1a1a3a", self.remove_all),
        ]:
            tk.Button(
                btn_row,
                text    = label,
                font    = ("Courier", 12, "bold") if label.startswith("+") else ("Courier", 12),
                fg      = "#0d0d1a" if label.startswith("+") else ("#FF3366" if "Remove All" in label else "#fff"),
                bg      = color,
                relief  = "flat",
                padx    = 12,
                pady    = 4,
                cursor  = "hand2",
                command = cmd,
            ).pack(side="left", padx=(0, 6))

    # ────────────────────────────────────────────────────────────────────────
    #  CREDITS WINDOW
    # ────────────────────────────────────────────────────────────────────────
    def open_credits(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("🙌 Special Thanks")
        dlg.configure(bg="#0d0d1a")
        dlg.grab_set()
        
        def section(parent, title):
            tk.Label(parent, text=title, font=("Courier", 13, "bold"),
                     fg="#FFD700", bg="#0d0d1a").pack(anchor="w", pady=(14, 4))
        outer = tk.Frame(dlg, bg="#0d0d1a")
        outer.pack(padx=28, pady=20)

        section(outer, "Mantis Tribe")
        tk.Label(outer,
                 text    = "Special thanks to Lung Cancer, Fallen Galaxy, Mystic, Supernova, Stoner, Oni, Videogamegod21",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        section(outer, "Gim Troupe")
        tk.Label(outer,
                 text    = "Special thanks to Lung Cancer (again), 15chefsXL, Jimeh, Gim, IKGim, Plague, Haider, Lasanga, Seasalt",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        section(outer, "Kingdom of Hallownest")
        tk.Label(outer,
                 text    = "Special thanks to Knight, Ashlyn, Ralsei/Dess, Opal, Emerald, Godseeker, Hornet/Hazlenut, Seer, Void, Mato",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        section(outer, "Youtubers/Devolpers for coding")
        tk.Label(outer,
                 text    = "Special thanks to Kaupenjoe, DougDoug, Crin, DougDougDoug, Toby Fox, LocalThunk, Minikloon",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        section(outer, "Background Music I used when I was coding")
        tk.Label(outer,
                 text    = "Special thanks to Bubble Pop Electric, 1 Hour of Agnes Tachyon, khaos emerald, goofy goober playlist,\nRisk of Rain 2 + Deltarune + Celsete + Silksong + Balatro + Cult of the Lamb + lobotomy kasien OST",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        section(outer, "My Friends")
        tk.Label(outer,
                 text    = "everyone one in those goated group chats",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        section(outer, "My Teachers")
        tk.Label(outer,
                 text    = "Mr. Chung",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        section(outer, "Other")
        tk.Label(outer,
                 text    = "Special thanks to Fuse, for writing my favorite series\nYuu Tanaka for my second favorite\nGoober my glorious bot I made\n" \
                            "Fujimoto and Gege, I hate you\nMy Parents\nMsPaint\nDrawnParrot for being a hella chill guy\nand last, Cayden.",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
    # ────────────────────────────────────────────────────────────────────────
    #  SETTINGS POPUP
    # ────────────────────────────────────────────────────────────────────────

    def open_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("⚙  Settings")
        dlg.configure(bg="#0d0d1a")
        dlg.grab_set()

        def section(parent, title):
            tk.Label(parent, text=title, font=("Courier", 13, "bold"),
                     fg="#FFD700", bg="#0d0d1a").pack(anchor="w", pady=(14, 4))

        outer = tk.Frame(dlg, bg="#0d0d1a")
        outer.pack(padx=28, pady=20)

        section(outer, "CHAOS EFFECTS  (uncheck to disable)")
        grid = tk.Frame(outer, bg="#0d0d1a")
        grid.pack(anchor="w")
        for i, (ev_name, info) in enumerate(EFFECT_INFO.items()):
            col = i % 2
            row = i // 2
            display = info["display"].replace("  ", " ").strip()
            tk.Checkbutton(
                grid,
                text             = display,
                variable         = self.effect_vars[ev_name],
                font             = ("Courier", 11),
                fg               = "#ddd",
                bg               = "#0d0d1a",
                selectcolor      = "#1a1a3a",
                activebackground = "#0d0d1a",
                activeforeground = "#fff",
            ).grid(row=row, column=col, sticky="w", padx=(0, 30), pady=2)

        section(outer, "SPIN DURATION")
        tk.Label(outer,
                 text    = "Controls how long each chaos event lasts.\n"
                           "1.0 = normal   |   0.5 = short   |   2.5 = very long",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        dur_row = tk.Frame(outer, bg="#0d0d1a")
        dur_row.pack(anchor="w", pady=(4, 0))
        tk.Label(dur_row, text="0.5×", font=("Courier", 10),
                 fg="#555", bg="#0d0d1a").pack(side="left")
        tk.Scale(
            dur_row,
            variable           = self.spin_mult,
            from_              = 0.5,
            to                 = 2.5,
            resolution         = 0.1,
            orient             = "horizontal",
            length             = 340,
            bg                 = "#1a1a3a",
            fg                 = "#fff",
            troughcolor        = "#0d0d1a",
            highlightthickness = 0,
            font               = ("Courier", 10),
        ).pack(side="left", padx=6)
        tk.Label(dur_row, text="2.5×", font=("Courier", 10),
                 fg="#555", bg="#0d0d1a").pack(side="left")

        section(outer, "MAX CHAOS EVENTS PER SPIN")
        tk.Label(outer,
                 text    = "How many chaos events can happen in a single spin.\n"
                           "0 = always straight stop   |   1 = calm   |   2 = full chaos",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        ev_row = tk.Frame(outer, bg="#0d0d1a")
        ev_row.pack(anchor="w", pady=(4, 0))
        for val, lbl in [(0, "0  (none)"), (1, "1  (one)"), (2, "2  (chaos)")]:
            tk.Radiobutton(
                ev_row,
                text             = lbl,
                variable         = self.max_events,
                value            = val,
                font             = ("Courier", 12),
                fg               = "#ddd",
                bg               = "#0d0d1a",
                selectcolor      = "#1a1a3a",
                activebackground = "#0d0d1a",
            ).pack(side="left", padx=(0, 20))
        section(outer, "CREDITS")
        tk.Label(outer,
                 text            = "Deepak Goteti  |  Period 1  |  Class of 2026\n"
                                   "little bit of Claude because some of this was mad annoying to debug",
                 font    = ("Courier", 10),
                 fg      = "#888",
                 bg      = "#0d0d1a",
                 justify = "left").pack(anchor="w")
        tk.Button(
            outer,
            text = "Special Thanks (Very Long)",
            font    = ("Courier", 9, "bold"),
            fg      = "#0d0d1a",
            bg      = "grey",
            relief  = "flat",
            padx    = 5,
            pady    = 2,
            cursor  = "hand2",
            command = self.open_credits).pack(anchor="w")
        
        grid = tk.Frame(outer, bg="#0d0d1a")
        grid.pack(anchor="w")
        tk.Button(
            outer,
            text    = "✓  Done",
            font    = ("Courier", 13, "bold"),
            fg      = "#0d0d1a",
            bg      = "#00E676",
            relief  = "flat",
            padx    = 20,
            pady    = 8,
            cursor  = "hand2",
            command = dlg.destroy,
        ).pack(pady=(20, 0))

    # ────────────────────────────────────────────────────────────────────────
    #  DRAWING
    # ────────────────────────────────────────────────────────────────────────

    def _draw_wheel(self):
        cv = self.wcv
        cx, cy, r = self.CX, self.CY, self.R
        n = len(self.items)

        cv.delete("all")
        cv.configure(bg=self.flash_col or "#0d0d1a")

        if n == 0:
            cv.create_oval(cx-r, cy-r, cx+r, cy+r,
                           fill="#1a1a2e", outline="#333", width=4)
            cv.create_text(cx, cy, text="Add items to spin!",
                           font=("Courier", 20), fill="#555")
        else:
            slice_deg = 360.0 / n
            for i, item in enumerate(self.items):
                start = self.angle + i * slice_deg - 90
                color = COLORS[i % len(COLORS)]
                cv.create_arc(
                    cx-r, cy-r, cx+r, cy+r,
                    start=start, extent=slice_deg,
                    fill=color, outline="#0d0d1a", width=2, style="pieslice",
                )
                mid_deg = start + slice_deg / 2.0
                mid_rad = math.radians(mid_deg)
                tr = r * 0.65
                tx = cx + tr * math.cos(mid_rad)
                ty = cy - tr * math.sin(mid_rad)
                if   n <= 8:  fs = 14
                elif n <= 16: fs = 11
                elif n <= 24: fs = 9
                else:         fs = 7
                max_chars = max(4, int(18 - n * 0.25))
                label = item[:max_chars] + "…" if len(item) > max_chars else item
                if slice_deg >= 6:
                    cv.create_text(tx, ty, text=label,
                                   font=("Courier", fs, "bold"),
                                   fill="black", angle=mid_deg)

        cv.create_oval(cx-r, cy-r, cx+r, cy+r,
                       outline="#FFD700", width=4, fill="")
        cv.create_oval(cx-28, cy-28, cx+28, cy+28,
                       fill="#0d0d1a", outline="#FFD700", width=4)
        cv.create_oval(cx-11, cy-11, cx+11, cy+11, fill="#FFD700", outline="")
        cv.create_polygon(cx-18, 4, cx+18, 4, cx, 44,
                          fill="#FFD700", outline="#fff", width=2)

        if self.banner_frames > 0:
            self.banner_frames -= 1
            if self.banner_frames > 0:
                bx1, by1 = cx - r,     cy + r - 90
                bx2, by2 = cx + r + 1, cy + r + 1
                cv.create_rectangle(bx1, by1, bx2, by2,
                                    fill=self.banner_color, outline="")
                cv.create_text(cx, (by1 + by2) / 2,
                               text=self.banner_text,
                               font=("Courier", 26, "bold"),
                               fill="black")

    def _draw_stickman(self):
        """Show PNG if available, otherwise draw the stick figure."""
        if self.png_images:
            self._draw_stickman_png()

    def _draw_stickman_png(self):
        """
        BUG FIX 3: three-level fallback chain so event-specific images work.

        Lookup order:
          1. Exact match for stick_state (e.g. "earthquake" → earthquake.png)
          2. If stick_state is an event name, try its declared base state
             (e.g. "earthquake" → "shocked" → shocked.png)
          3. Fall back to "idle" as a last resort
        """
        c = self.scv
        c.delete("all")

        # 1. Try event-specific image
        img = self.png_images.get(self.stick_state)

        # 2. If not found and it's an event name, try the base state image
        if img is None and self.stick_state in EFFECT_INFO:
            base_state = EFFECT_INFO[self.stick_state]["stick"]
            img = self.png_images.get(base_state)

        # 3. Final fallback to idle
        if img is None:
            img = self.png_images.get("idle")

        if img:
            c.create_image(170, 210, image=img, anchor="center")

    
    # ────────────────────────────────────────────────────────────────────────
    #  SPIN ENGINE
    # ────────────────────────────────────────────────────────────────────────

    def start_spin(self):
        if self.spinning or len(self.items) < 2:
            return

        self.spinning = True
        self.winner   = None
        self.wlbl.config(text="")
        self.rbtn.config(state="disabled")
        self.sbtn.config(state="disabled")
        self._set_stick("start", force=True)
        self._say(random.choice(NARRATIONS["start"]))

        self.vel = random.uniform(22, 32)

        enabled = [name for name, var in self.effect_vars.items() if var.get()]
        max_ev  = self.max_events.get()
        roll    = random.random()

        if max_ev == 0 or not enabled:
            n_events = 0
        elif max_ev == 1:
            n_events = 0 if roll < 0.15 else 1
        else:
            if   roll < 0.10: n_events = 0
            elif roll < 0.80: n_events = 1
            else:             n_events = 2

        self.chaos_q = random.choices(enabled, k=n_events) if enabled else []
        self.chaos_q.append("_stop")

        self.phase   = "initial"
        self.c_frame = 0
        self.c_dur   = random.randint(160, 240)

    def _tick_spin(self):
        if not self.spinning:
            return

        if self.phase == "initial":
            self.angle   += self.vel
            self.c_frame += 1
            if self.c_frame >= self.c_dur:
                self._next_event()

        elif self.phase == "chaos":
            self._run_event()

        elif self.phase == "stopping":
            self.angle += self.vel
            self.vel   *= 0.975
            if abs(self.vel) < 0.25:
                self.vel   = 0
                self.phase = "done"
                self._finish()

    def _next_event(self):
        if not self.chaos_q:
            self.phase = "stopping"
            return

        ev = self.chaos_q.pop(0)

        if ev == "_stop":
            if abs(self.vel) < 4:
                self.vel = random.uniform(6, 14)
            self.phase = "stopping"
            return

        self.cur_event = ev
        self.c_frame   = 0
        self.phase     = "chaos"

        info       = EFFECT_INFO[ev]
        lo, hi     = info["duration"]
        self.c_dur = int(random.randint(lo, hi) * self.spin_mult.get())

        if self.c_dur >= 80:
            self._say(random.choice(NARRATIONS.get(ev, ["..."])))
            self._show_banner(info["display"], info["color"])

        # Store the EVENT NAME so _draw_stickman_png can look up earthquake.png etc.
        # The fallback chain in _draw_stickman_png handles missing event images.
        self._set_stick(ev)

    def _run_event(self):
        ev = self.cur_event
        f  = self.c_frame
        d  = self.c_dur
        self.c_frame += 1

        if ev == "stutter":
            if f % 5 == 0:
                self.vel = random.choice([-4, 0.3, 1.0, 8.0, 22.0, 30.0, 3.0, -2.0])
            self.angle += self.vel

        elif ev == "reverse":
            if   f < d * 0.35: self.vel -= 2.8
            elif f > d * 0.60: self.vel += 2.2
            self.vel   = max(-60, min(60, self.vel))
            self.angle += self.vel

        elif ev == "slowdown_burst":
            if f < d * 0.55:
                self.vel = max(0.2, self.vel * 0.89)
            else:
                self.vel = min(55, self.vel * 1.45)
                if f == int(d * 0.55) + 1:
                    self._say(random.choice(NARRATIONS["slowdown_burst"]))
                    self._flash("#FF3366", 10)
            self.angle += self.vel

        elif ev == "fake_stop":
            half = int(d * 0.5)
            if f < half:
                self.vel = max(0.05, self.vel * 0.91)
            elif f == half:
                self._say(random.choice(NARRATIONS["fake_stop"]))
                self._flash("#FFD700", 14)
                self.vel = random.uniform(20, 35)
            self.angle += self.vel

        elif ev == "speed_burst":
            if f == 0:
                self.vel = random.uniform(50, 70)
                self._flash("#00E676", 10)
            self.vel   = max(12, self.vel * 0.985)
            self.angle += self.vel

        elif ev == "almost_there":
            self.vel = max(0.4, self.vel * 0.962)
            self.angle += self.vel

        elif ev == "earthquake":
            if f % 3 == 0:
                jolt     = random.uniform(8, 22) * random.choice([-1, 1])
                self.vel = max(-30, min(50, self.vel + jolt))
            if f % 8 == 0:
                self._flash(random.choice(["#FF3366", "#FFD700", "#FF6B35", "#E040FB"]), 5)
            self.angle += self.vel

        elif ev == "warp_speed":
            if f == 0:
                self.vel = random.uniform(80, 110)
                self._flash("#E040FB", 12)
            self.vel   = max(8, self.vel * 0.965)
            self.angle += self.vel

        elif ev == "indecision":
            target     = 6 + 22 * (0.5 + 0.5 * math.sin(f * 0.21))
            self.vel   = self.vel + (target - self.vel) * 0.18
            self.angle += self.vel

        elif ev == "gravity_fight":
            gravity    = 0.4
            self.vel   = max(0.5, self.vel - gravity)
            if f % 15 == 0:
                self.vel += random.uniform(8, 18)
                self._flash("#26C6DA", 6)
            self.vel   = min(50, self.vel)
            self.angle += self.vel

        elif ev == "dead_stop":
            self.vel = 0
            self._say(random.choice(NARRATIONS["dead_stop"]))
            self._show_banner("💀  D E A D   S T O P .", "#222222")
            self._set_stick("dead_stop", force=True)
            self.phase = "done"
            self._finish()
            return

        if self.c_frame >= self.c_dur:
            self._next_event()

    def _finish(self):
        self.spinning = False
        self.sbtn.config(state="normal")
        self._set_stick("winner", force=True)
        self._flash("#FFD700", 30)

        n         = len(self.items)
        slice_deg = 360.0 / n
        local     = (180.0 - self.angle % 360.0) % 360.0
        idx       = int(local / slice_deg) % n

        self.winner = self.items[idx]
        self.wlbl.config(text=f"🏆  {self.winner}")
        self._say(random.choice(NARRATIONS["winner"]) + f"\n{self.winner}!")
        self.rbtn.config(state="normal")

    # ────────────────────────────────────────────────────────────────────────
    #  HELPERS
    # ────────────────────────────────────────────────────────────────────────

    def _say(self, text):
        self.speech.config(text=text)

    def _flash(self, color, frames):
        self.flash_col = color
        self.flash_f   = frames

    def _show_banner(self, text, color):
        self.banner_text   = text
        self.banner_color  = color
        self.banner_frames = 150

    def _loop(self):
        self.anim_f += 1

        # Tick the PNG lock down
        if self.stick_lock_frames > 0:
            self.stick_lock_frames -= 1

        if not self.spinning:
            self.narr_timer += 1
            if self.narr_timer >= 160:
                self.narr_timer = 0
                self._set_stick("idle", force=True)
                self._say(random.choice(NARRATIONS["idle"]))

        if self.flash_f > 0:
            self.flash_f -= 1
            if self.flash_f == 0:
                self.flash_col = None

        self._tick_spin()
        self._draw_wheel()
        self._draw_stickman()

        self.root.after(20, self._loop)

    # ────────────────────────────────────────────────────────────────────────
    #  ITEM MANAGEMENT
    # ────────────────────────────────────────────────────────────────────────

    def _refresh_count(self):
        self.count_lbl.config(text=f"({len(self.items)}/{MAX_ITEMS})")

    def add_item(self):
        if len(self.items) >= MAX_ITEMS:
            self._say(f"MAX {MAX_ITEMS}\nITEMS!")
            return
        name = self.ent.get().strip()
        if not name or name in self.items:
            return
        self.items.append(name)
        self.lb.insert("end", name)
        self.ent.delete(0, "end")
        self._refresh_count()

    def remove_selected(self):
        sel = self.lb.curselection()
        if not sel:
            return
        idx = sel[0]
        self.items.pop(idx)
        self.lb.delete(idx)
        self._refresh_count()

    def remove_winner(self):
        if self.winner and self.winner in self.items:
            idx = self.items.index(self.winner)
            self.items.pop(idx)
            self.lb.delete(idx)
            self._refresh_count()
        self.winner = None
        self.wlbl.config(text="")
        self.rbtn.config(state="disabled")

    def remove_all(self):
        self.items.clear()
        self.lb.delete(0, "end")
        self.winner = None
        self.wlbl.config(text="")
        self.rbtn.config(state="disabled")
        self._refresh_count()

    def open_paste_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Paste Name List")
        dlg.configure(bg="#0d0d1a")
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg,
                 text="Paste names below — one per line or comma-separated.",
                 font=("Courier", 12), fg="#aaa", bg="#0d0d1a",
                 justify="left").pack(padx=20, pady=(16, 6), anchor="w")

        txt = tk.Text(dlg, font=("Courier", 12), fg="#fff", bg="#0d0d1a",
                      insertbackground="#fff", width=44, height=16,
                      relief="flat", bd=6)
        txt.pack(padx=20, pady=(0, 10))
        txt.focus_set()

        status = tk.Label(dlg, text="", font=("Courier", 11),
                          fg="#00E676", bg="#0d0d1a")
        status.pack()

        def do_add():
            raw   = txt.get("1.0", "end")
            names = [c.strip() for c in raw.replace(",", "\n").splitlines() if c.strip()]
            added = skipped = 0
            for name in names:
                if len(self.items) >= MAX_ITEMS:
                    skipped += len(names) - names.index(name)
                    break
                if name not in self.items:
                    self.items.append(name)
                    self.lb.insert("end", name)
                    added += 1
                else:
                    skipped += 1
            self._refresh_count()
            msg = f"✓ Added {added}"
            if skipped:
                msg += f"  |  {skipped} skipped"
            status.config(text=msg)
            txt.delete("1.0", "end")

        btn_row = tk.Frame(dlg, bg="#0d0d1a")
        btn_row.pack(pady=(4, 16))

        tk.Button(btn_row, text="Add All to Wheel",
                  font=("Courier", 13, "bold"), fg="#0d0d1a", bg="#00E676",
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=do_add).pack(side="left", padx=(0, 10))

        tk.Button(btn_row, text="Close",
                  font=("Courier", 12), fg="#fff", bg="#333",
                  relief="flat", padx=12, pady=6, cursor="hand2",
                  command=dlg.destroy).pack(side="left")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app  = SpinWheelApp(root)
    root.mainloop()
