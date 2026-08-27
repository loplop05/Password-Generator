import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import secrets
import string

AMBIGUOUS = "Il1O0|`'\".,{}[]()/\\;:<>"

# ---------------- Theme ----------------

THEMES = {
    "dark": {
        "bg": "#1e1f29",
        "panel": "#282a3a",
        "fg": "#f2f2f7",
        "muted": "#9a9cb0",
        "accent": "#7c5cff",
        "accent_hover": "#6a4ce0",
        "entry_bg": "#33344a",
        "border": "#3d3f56",
        "weak": "#ff5c5c",
        "fair": "#ffb64c",
        "good": "#ffe14c",
        "strong": "#4cff88",
    },
    "light": {
        "bg": "#f4f4f8",
        "panel": "#ffffff",
        "fg": "#1e1f29",
        "muted": "#6b6d80",
        "accent": "#6c4cf0",
        "accent_hover": "#5a3ce0",
        "entry_bg": "#eeeef4",
        "border": "#dcdce6",
        "weak": "#e0453f",
        "fair": "#e08c2b",
        "good": "#c9a70e",
        "strong": "#1eab5e",
    },
}


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("480x720")
        self.root.minsize(440, 680)
        self.mode = "dark"
        self.history = []

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.exclude_ambiguous_var = tk.BooleanVar(value=False)
        self.exclude_custom_var = tk.StringVar(value="")
        self.length_var = tk.IntVar(value=16)
        self.count_var = tk.IntVar(value=1)

        self._build_style()
        self._build_ui()
        self._apply_theme()
        self.root.bind("<Return>", lambda e: self.generate())

    # ---------------- Style / theme ----------------

    def _build_style(self):
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

    def _c(self, key):
        return THEMES[self.mode][key]

    def _apply_theme(self):
        c = THEMES[self.mode]
        self.root.configure(bg=c["bg"])

        self.style.configure("TFrame", background=c["bg"])
        self.style.configure("Panel.TFrame", background=c["panel"])

        self.style.configure(
            "Title.TLabel", background=c["bg"], foreground=c["fg"],
            font=("Segoe UI", 20, "bold"),
        )
        self.style.configure(
            "Sub.TLabel", background=c["bg"], foreground=c["muted"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Section.TLabel", background=c["panel"], foreground=c["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        self.style.configure(
            "Body.TLabel", background=c["panel"], foreground=c["fg"],
            font=("Segoe UI", 11),
        )
        self.style.configure(
            "Strength.TLabel", background=c["panel"], foreground=c["fg"],
            font=("Segoe UI", 10, "bold"),
        )

        self.style.configure(
            "TCheckbutton", background=c["panel"], foreground=c["fg"],
            font=("Segoe UI", 10), focuscolor=c["panel"],
        )
        self.style.map("TCheckbutton", background=[("active", c["panel"])])

        self.style.configure(
            "Accent.TButton", background=c["accent"], foreground="#ffffff",
            font=("Segoe UI", 12, "bold"), borderwidth=0, padding=10,
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", c["accent_hover"]), ("pressed", c["accent_hover"])],
        )

        self.style.configure(
            "Ghost.TButton", background=c["entry_bg"], foreground=c["fg"],
            font=("Segoe UI", 10), borderwidth=0, padding=8,
        )
        self.style.map("Ghost.TButton", background=[("active", c["border"])])

        self.style.configure(
            "Horizontal.TScale", background=c["panel"], troughcolor=c["entry_bg"],
        )

        self.style.configure(
            "TSpinbox", fieldbackground=c["entry_bg"], background=c["entry_bg"],
            foreground=c["fg"], arrowsize=14,
        )

        self.password_var_widget_refresh()
        self._redraw_strength()
        self._refresh_history_colors()

    def password_var_widget_refresh(self):
        c = THEMES[self.mode]
        for widget, kind in getattr(self, "_manual_widgets", []):
            if kind == "panel":
                widget.configure(bg=c["panel"])
            elif kind == "entry":
                widget.configure(
                    bg=c["entry_bg"], fg=c["fg"], insertbackground=c["fg"],
                    relief="flat", highlightthickness=1,
                    highlightbackground=c["border"], highlightcolor=c["accent"],
                )
            elif kind == "canvas":
                widget.configure(bg=c["entry_bg"], highlightthickness=0)
            elif kind == "listbox":
                widget.configure(
                    bg=c["entry_bg"], fg=c["fg"], selectbackground=c["accent"],
                    relief="flat", highlightthickness=0,
                )

    def toggle_theme(self):
        self.mode = "light" if self.mode == "dark" else "dark"
        self.theme_btn.config(text="☀ Light" if self.mode == "dark" else "🌙 Dark")
        self._apply_theme()

    # ---------------- UI ----------------

    def _build_ui(self):
        self._manual_widgets = []

        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=24, pady=(20, 10))

        ttk.Label(header, text="Password Generator", style="Title.TLabel").pack(side="left")
        self.theme_btn = ttk.Button(
            header, text="☀ Light", style="Ghost.TButton", command=self.toggle_theme
        )
        self.theme_btn.pack(side="right")

        ttk.Label(
            self.root, text="Strong, random passwords — generated locally.",
            style="Sub.TLabel",
        ).pack(anchor="w", padx=24)

        # ---- Password output panel ----
        out_panel = tk.Frame(self.root, bd=0)
        out_panel.pack(fill="x", padx=24, pady=(18, 12))
        self._manual_widgets.append((out_panel, "panel"))

        inner = ttk.Frame(out_panel, style="Panel.TFrame")
        inner.pack(fill="x", padx=14, pady=14)

        row = tk.Frame(inner, bd=0)
        row.pack(fill="x")
        self._manual_widgets.append((row, "panel"))

        self.password_entry = tk.Entry(
            row, font=("Consolas", 15), justify="center", show="*", bd=0,
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self._manual_widgets.append((self.password_entry, "entry"))

        self.show_button = ttk.Button(
            row, text="Show", style="Ghost.TButton", width=6, command=self.toggle_password
        )
        self.show_button.pack(side="left")

        # Strength meter
        strength_row = ttk.Frame(inner, style="Panel.TFrame")
        strength_row.pack(fill="x", pady=(14, 0))

        self.strength_canvas = tk.Canvas(strength_row, height=8, bd=0, highlightthickness=0)
        self.strength_canvas.pack(fill="x", side="left", expand=True)
        self._manual_widgets.append((self.strength_canvas, "canvas"))

        self.strength_label = ttk.Label(strength_row, text="", style="Strength.TLabel", width=12)
        self.strength_label.pack(side="left", padx=(10, 0))

        btn_row = ttk.Frame(inner, style="Panel.TFrame")
        btn_row.pack(fill="x", pady=(14, 0))

        self.copy_button = ttk.Button(
            btn_row, text="Copy", style="Ghost.TButton", command=self.copy_password
        )
        self.copy_button.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ttk.Button(
            btn_row, text="Save to file", style="Ghost.TButton", command=self.save_to_file
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # ---- Options panel ----
        opt_panel = tk.Frame(self.root, bd=0)
        opt_panel.pack(fill="x", padx=24, pady=6)
        self._manual_widgets.append((opt_panel, "panel"))

        opt_inner = ttk.Frame(opt_panel, style="Panel.TFrame")
        opt_inner.pack(fill="x", padx=14, pady=14)

        ttk.Label(opt_inner, text="LENGTH", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        self.length_display = ttk.Label(opt_inner, text="16", style="Body.TLabel")
        self.length_display.grid(row=0, column=1, sticky="e", pady=(0, 4))

        length_scale = ttk.Scale(
            opt_inner, from_=4, to=64, orient="horizontal",
            variable=self.length_var, command=self._on_length_change,
        )
        length_scale.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        opt_inner.columnconfigure(0, weight=1)

        ttk.Label(opt_inner, text="CHARACTER TYPES", style="Section.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )

        chk_frame = ttk.Frame(opt_inner, style="Panel.TFrame")
        chk_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        ttk.Checkbutton(chk_frame, text="Uppercase (A-Z)", variable=self.uppercase_var).grid(
            row=0, column=0, sticky="w", pady=2
        )
        ttk.Checkbutton(chk_frame, text="Lowercase (a-z)", variable=self.lowercase_var).grid(
            row=1, column=0, sticky="w", pady=2
        )
        ttk.Checkbutton(chk_frame, text="Numbers (0-9)", variable=self.numbers_var).grid(
            row=0, column=1, sticky="w", padx=(20, 0), pady=2
        )
        ttk.Checkbutton(chk_frame, text="Symbols (!@#$)", variable=self.symbols_var).grid(
            row=1, column=1, sticky="w", padx=(20, 0), pady=2
        )
        ttk.Checkbutton(
            chk_frame, text="Exclude ambiguous (l, 1, I, O, 0...)",
            variable=self.exclude_ambiguous_var,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 2))

        ttk.Label(opt_inner, text="EXCLUDE CUSTOM CHARACTERS", style="Section.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(14, 4)
        )
        exclude_entry = tk.Entry(
            opt_inner, textvariable=self.exclude_custom_var, font=("Consolas", 11), bd=0,
        )
        exclude_entry.grid(row=5, column=0, columnspan=2, sticky="ew", ipady=5)
        self._manual_widgets.append((exclude_entry, "entry"))

        ttk.Label(opt_inner, text="HOW MANY", style="Section.TLabel").grid(
            row=6, column=0, sticky="w", pady=(14, 4)
        )
        count_spin = ttk.Spinbox(
            opt_inner, from_=1, to=20, textvariable=self.count_var, width=6, justify="center",
        )
        count_spin.grid(row=7, column=0, sticky="w")

        # ---- Generate button ----
        ttk.Button(
            self.root, text="Generate Password(s)", style="Accent.TButton",
            command=self.generate,
        ).pack(fill="x", padx=24, pady=(16, 10))

        # ---- History ----
        hist_panel = tk.Frame(self.root, bd=0)
        hist_panel.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self._manual_widgets.append((hist_panel, "panel"))

        hist_inner = ttk.Frame(hist_panel, style="Panel.TFrame")
        hist_inner.pack(fill="both", expand=True, padx=14, pady=14)

        top_row = ttk.Frame(hist_inner, style="Panel.TFrame")
        top_row.pack(fill="x")
        ttk.Label(top_row, text="HISTORY (this session)", style="Section.TLabel").pack(side="left")
        ttk.Button(
            top_row, text="Clear", style="Ghost.TButton", width=6, command=self.clear_history
        ).pack(side="right")

        list_frame = ttk.Frame(hist_inner, style="Panel.TFrame")
        list_frame.pack(fill="both", expand=True, pady=(8, 0))

        self.history_list = tk.Listbox(
            list_frame, font=("Consolas", 11), bd=0, activestyle="none",
        )
        self.history_list.pack(side="left", fill="both", expand=True)
        self._manual_widgets.append((self.history_list, "listbox"))

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_list.config(yscrollcommand=scrollbar.set)
        self.history_list.bind("<Double-Button-1>", self._copy_from_history)

    def _on_length_change(self, _val=None):
        self.length_display.config(text=str(self.length_var.get()))

    # ---------------- Core logic ----------------

    def _build_charset(self):
        pools = []
        if self.uppercase_var.get():
            pools.append(string.ascii_uppercase)
        if self.lowercase_var.get():
            pools.append(string.ascii_lowercase)
        if self.numbers_var.get():
            pools.append(string.digits)
        if self.symbols_var.get():
            pools.append(string.punctuation)

        exclude = set(self.exclude_custom_var.get())
        if self.exclude_ambiguous_var.get():
            exclude |= set(AMBIGUOUS)

        cleaned_pools = []
        for pool in pools:
            filtered = "".join(ch for ch in pool if ch not in exclude)
            if filtered:
                cleaned_pools.append(filtered)
        return cleaned_pools

    def _make_password(self, length, pools):
        all_chars = "".join(pools)
        # Guarantee at least one character from each selected pool
        required = [secrets.choice(pool) for pool in pools]
        remaining = [secrets.choice(all_chars) for _ in range(length - len(required))]
        combined = required + remaining
        for _ in range(6):  # shuffle securely
            secrets.SystemRandom().shuffle(combined)
        return "".join(combined)

    def generate(self):
        try:
            length = int(self.length_var.get())
        except (ValueError, tk.TclError):
            messagebox.showerror("Error", "Enter a valid password length.")
            return

        if length < 4:
            messagebox.showerror("Error", "Password length must be at least 4.")
            return

        pools = self._build_charset()
        if not pools:
            messagebox.showerror(
                "Error",
                "Select at least one character type (after exclusions, "
                "at least one pool must still have characters).",
            )
            return
        if length < len(pools):
            messagebox.showerror(
                "Error",
                f"Length must be at least {len(pools)} to include every selected type.",
            )
            return

        try:
            count = max(1, int(self.count_var.get()))
        except (ValueError, tk.TclError):
            count = 1

        last_password = ""
        for _ in range(count):
            last_password = self._make_password(length, pools)
            self.history.insert(0, last_password)
            self.history_list.insert(0, last_password)

        self.history = self.history[:100]
        while self.history_list.size() > 100:
            self.history_list.delete(self.history_list.size() - 1)

        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, last_password)
        self._redraw_strength(last_password)

    # ---------------- Strength meter ----------------

    def _score_password(self, password):
        if not password:
            return 0, "—", self._c("muted")

        variety = sum(
            [
                any(c.islower() for c in password),
                any(c.isupper() for c in password),
                any(c.isdigit() for c in password),
                any(c in string.punctuation for c in password),
            ]
        )
        length_score = min(len(password) / 20, 1.0)
        score = 0.55 * length_score + 0.45 * (variety / 4)

        if score < 0.35:
            return score, "Weak", self._c("weak")
        if score < 0.6:
            return score, "Fair", self._c("fair")
        if score < 0.85:
            return score, "Good", self._c("good")
        return score, "Strong", self._c("strong")

    def _redraw_strength(self, password=None):
        if password is None:
            password = self.password_entry.get()
        score, label, color = self._score_password(password)

        self.strength_canvas.delete("all")
        w = self.strength_canvas.winfo_width() or 300
        h = 8
        self.strength_canvas.create_rectangle(0, 0, w, h, fill=self._c("entry_bg"), width=0)
        self.strength_canvas.create_rectangle(0, 0, int(w * score), h, fill=color, width=0)
        self.strength_label.config(text=label, foreground=color)
        self.root.after(50, lambda: self._resize_strength(password))

    def _resize_strength(self, password):
        # redraw once real width is known (first call may be before layout settles)
        self.strength_canvas.bind(
            "<Configure>", lambda e: self._redraw_strength(self.password_entry.get())
        )

    def _refresh_history_colors(self):
        pass  # listbox theming handled in password_var_widget_refresh

    # ---------------- Actions ----------------

    def toggle_password(self):
        if self.password_entry.cget("show") == "":
            self.password_entry.config(show="*")
            self.show_button.config(text="Show")
        else:
            self.password_entry.config(show="")
            self.show_button.config(text="Hide")

    def copy_password(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Warning", "Generate a password first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()

        original = self.copy_button.cget("text")
        self.copy_button.config(text="Copied!")
        self.root.after(1200, lambda: self.copy_button.config(text=original))

    def _copy_from_history(self, _event=None):
        selection = self.history_list.curselection()
        if not selection:
            return
        password = self.history_list.get(selection[0])
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self._redraw_strength(password)

    def clear_history(self):
        self.history.clear()
        self.history_list.delete(0, tk.END)

    def save_to_file(self):
        if not self.history:
            messagebox.showwarning("Warning", "No passwords generated yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile="passwords.txt",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.history))
        messagebox.showinfo("Saved", f"Saved {len(self.history)} password(s) to:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()