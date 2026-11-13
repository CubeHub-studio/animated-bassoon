import json
import math
import random
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

APP_NAME = "NOVA DESK"
DATA_FILE = Path.home() / ".nova_desk.json"
BG = "#090d18"
PANEL = "#111a2b"
PANEL_2 = "#172238"
TEXT = "#edf3ff"
MUTED = "#8291ad"
ACCENT = "#8b7cff"
CYAN = "#55d8e8"
GREEN = "#83e6b0"


def load_data():
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_data(data):
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


class NovaDesk:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME + "  |  Your little corner of the universe")
        self.root.geometry("1040x700")
        self.root.minsize(850, 600)
        self.root.configure(bg=BG)
        self.data = load_data()
        self.seconds = int(self.data.get("focus_seconds", 25 * 60))
        self.remaining = self.seconds
        self.running = False
        self.last_tick = time.monotonic()
        self.mode = "FOCUS"
        self.stars = []
        self._style()
        self._build()
        self._load_note()
        self._animate()
        self._tick()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=PANEL_2, background=PANEL_2,
                        foreground=TEXT, arrowcolor=CYAN, bordercolor=PANEL_2)
        style.configure("TScrollbar", background=PANEL, troughcolor=BG,
                        bordercolor=BG, arrowcolor=MUTED)

    def _build(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=30, pady=(22, 14))
        brand = tk.Frame(top, bg=BG)
        brand.pack(side="left")
        tk.Label(brand, text="✦", fg=CYAN, bg=BG, font=("Segoe UI Symbol", 22)).pack(side="left", padx=(0, 10))
        tk.Label(brand, text="NOVA", fg=TEXT, bg=BG, font=("Segoe UI", 19, "bold")).pack(side="left")
        tk.Label(brand, text="  /  DESK", fg=ACCENT, bg=BG, font=("Segoe UI", 12, "bold")).pack(side="left", pady=(5, 0))
        tk.Label(top, text="A QUIETER PLACE TO GET THINGS DONE", fg=MUTED, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(side="right", pady=10)

        self.scene = tk.Canvas(self.root, height=150, bg="#0d1425", highlightthickness=0)
        self.scene.pack(fill="x", padx=30)
        self.scene.create_rectangle(0, 105, 2000, 150, fill="#101b30", outline="")
        self.scene.create_text(28, 28, anchor="w", text="YOUR SPACE. YOUR PACE.",
                               fill=TEXT, font=("Segoe UI", 15, "bold"))
        self.scene.create_text(29, 55, anchor="w", text="Small steps still move you forward.",
                               fill="#9eacc7", font=("Segoe UI", 10))
        self.scene.create_oval(760, -95, 930, 75, fill="#302c69", outline="")
        self.scene.create_oval(785, -70, 905, 50, fill="#8b7cff", outline="")
        self.scene.create_oval(815, -43, 875, 17, fill="#c4bcff", outline="")

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=18)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground="#202d45")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground="#202d45")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self._section_title(left, "01", "FOCUS TIMER", "A little progress adds up.")
        timer_wrap = tk.Frame(left, bg=PANEL)
        timer_wrap.pack(fill="both", expand=True, padx=22, pady=5)
        self.clock = tk.Canvas(timer_wrap, width=260, height=230, bg=PANEL, highlightthickness=0)
        self.clock.pack(pady=(0, 2))
        self._draw_clock()
        controls = tk.Frame(left, bg=PANEL)
        controls.pack(pady=(0, 15))
        self.start_btn = self._button(controls, "START FOCUS", self.toggle_timer, ACCENT)
        self.start_btn.pack(side="left", padx=5)
        self._button(controls, "RESET", self.reset_timer, PANEL_2).pack(side="left", padx=5)
        modes = tk.Frame(left, bg=PANEL)
        modes.pack(pady=(0, 20))
        for label, mins in (("QUICK  5", 5), ("STANDARD  25", 25), ("DEEP  50", 50)):
            self._button(modes, label, lambda m=mins: self.set_duration(m), PANEL_2, small=True).pack(side="left", padx=4)

        self._section_title(right, "02", "SCRATCHPAD", "Keep the important bits nearby.")
        self.note = tk.Text(right, height=10, bg=PANEL_2, fg=TEXT, insertbackground=CYAN,
                            relief="flat", borderwidth=0, padx=14, pady=14,
                            font=("Segoe UI", 10), wrap="word", undo=True)
        self.note.pack(fill="both", expand=True, padx=20, pady=(8, 10))
        self.note.bind("<KeyRelease>", self._save_note)
        bottom = tk.Frame(right, bg=PANEL)
        bottom.pack(fill="x", padx=20, pady=(0, 18))
        self.status = tk.Label(bottom, text="●  NOTES SAVE AUTOMATICALLY", fg=GREEN, bg=PANEL,
                               font=("Segoe UI", 8, "bold"))
        self.status.pack(side="left")
        self._button(bottom, "CLEAR", self.clear_note, PANEL_2, small=True).pack(side="right")

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=30, pady=(0, 14))
        tk.Label(footer, text="✦  BUILT FOR THE IN-BETWEEN MOMENTS", fg="#64728d", bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        self.footer_time = tk.Label(footer, text="", fg=MUTED, bg=BG, font=("Segoe UI", 9))
        self.footer_time.pack(side="right")
        self._update_footer()

    def _section_title(self, parent, number, title, subtitle):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=22, pady=(20, 5))
        tk.Label(row, text=number, fg=CYAN, bg=PANEL, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        tk.Label(row, text=title, fg=TEXT, bg=PANEL, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(parent, text=subtitle, fg=MUTED, bg=PANEL, font=("Segoe UI", 9)).pack(anchor="w", padx=48)

    def _button(self, parent, label, command, color, small=False):
        return tk.Button(parent, text=label, command=command, bg=color, fg=TEXT,
                         activebackground="#6559c7", activeforeground="white",
                         relief="flat", bd=0, padx=15 if not small else 10,
                         pady=10 if not small else 7, cursor="hand2",
                         font=("Segoe UI", 8, "bold"))

    def _draw_clock(self):
        c = self.clock
        c.delete("timer")
        cx, cy, radius = 130, 112, 86
        c.create_oval(cx-radius, cy-radius, cx+radius, cy+radius,
                      outline="#25334e", width=9, tags="timer")
        total = max(1, self.seconds)
        fraction = max(0, min(1, self.remaining / total))
        c.create_arc(cx-radius, cy-radius, cx+radius, cy+radius, start=90,
                     extent=-360*fraction, style="arc", outline=ACCENT, width=9,
                     tags="timer")
        c.create_text(cx, cy-8, text=self._format_time(self.remaining), fill=TEXT,
                      font=("Segoe UI", 31, "bold"), tags="timer")
        c.create_text(cx, cy+27, text=self.mode, fill=CYAN,
                      font=("Segoe UI", 8, "bold"), tags="timer")

    @staticmethod
    def _format_time(value):
        return f"{value//60:02d}:{value%60:02d}"

    def toggle_timer(self):
        self.running = not self.running
        self.last_tick = time.monotonic()
        self.start_btn.configure(text="PAUSE" if self.running else "RESUME")

    def reset_timer(self):
        self.running = False
        self.remaining = self.seconds
        self.start_btn.configure(text="START FOCUS")
        self._draw_clock()

    def set_duration(self, minutes):
        self.running = False
        self.seconds = minutes * 60
        self.remaining = self.seconds
        self.mode = "QUICK" if minutes == 5 else ("DEEP WORK" if minutes == 50 else "FOCUS")
        self.start_btn.configure(text="START FOCUS")
        self._draw_clock()
        self.data["focus_seconds"] = self.seconds
        save_data(self.data)

    def _tick(self):
        now = time.monotonic()
        if self.running:
            elapsed = now - self.last_tick
            if elapsed >= 1:
                self.remaining = max(0, self.remaining - int(elapsed))
                self.last_tick = now
                self._draw_clock()
                if self.remaining == 0:
                    self.running = False
                    self.start_btn.configure(text="START AGAIN")
                    self.mode = "COMPLETE"
                    self._draw_clock()
                    self.root.bell()
        self.root.after(250, self._tick)

    def _load_note(self):
        self.note.insert("1.0", self.data.get("note", ""))

    def _save_note(self, _event=None):
        self.data["note"] = self.note.get("1.0", "end-1c")
        save_data(self.data)
        self.status.configure(text="●  SAVED", fg=GREEN)

    def clear_note(self):
        self.note.delete("1.0", "end")
        self._save_note()

    def _animate(self):
        if not self.stars:
            w = max(500, self.scene.winfo_width())
            for _ in range(55):
                x = random.randint(0, w)
                y = random.randint(0, 100)
                r = random.choice((1, 1, 2))
                item = self.scene.create_oval(x, y, x+r, y+r, fill="#667da8", outline="")
                self.stars.append((item, random.uniform(0.2, 1.0)))
        for item, speed in self.stars:
            self.scene.move(item, -speed, 0)
            x1, y1, x2, y2 = self.scene.coords(item)
            if x2 < 0:
                self.scene.coords(item, self.scene.winfo_width()+5, y1, self.scene.winfo_width()+6, y2)
        self.root.after(45, self._animate)

    def _update_footer(self):
        self.footer_time.configure(text=time.strftime("%A  •  %I:%M %p"))
        self.root.after(1000, self._update_footer)

    def _close(self):
        self._save_note()
        self.data["focus_seconds"] = self.seconds
        save_data(self.data)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = NovaDesk(root)
    root.mainloop()
