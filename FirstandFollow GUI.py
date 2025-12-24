import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from FirstandFollow import GrammarAnalyzer  

# ترمینال های تک حرفی
TERMINAL_SYMBOLS = ['(', ')', '+', '*', '-', '/', '^', '=', '|'] 

def tokenize_production(production_str):
    """توکن‌بندی صحیح نمادها با فاصله"""
    for symbol in TERMINAL_SYMBOLS:
        production_str = production_str.replace(symbol, f' {symbol} ')
    production_str = ' '.join(production_str.split())
    return production_str

def parse_grammar(text):
    #تدبیل متن گرامر به دیکشنری
    grammar = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or ":" not in line or line.startswith(":"):
            continue
        try:
            left, right = line.split(":", 1)
            left = left.strip()
            if not right.strip():
                continue
            tokenized_right = tokenize_production(right)
            productions = [p.strip() for p in tokenized_right.split("|")]
            grammar[left] = [p for p in productions if p]
        except ValueError:
            continue
    return grammar

# ----------------------- GUI -----------------------

class GrammarGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grammar FIRST/FOLLOW Analyzer")
        self.geometry("700x750")
        self.configure(bg="#1E1F22")  # پس‌زمینه خیلی تیره
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.set_dark_theme()
        self.create_widgets()

    def set_dark_theme(self):
        NORMAL_FONT = ('Segoe UI', 12)
        TITLE_FONT = ('Segoe UI', 15, 'bold')

        bg = "#1E1F22"           # پس زمینه کلی
        frame_bg = "#2E3915"     # پس زمینه باکس‌ها
        text_bg = "#2B2D31"
        text_fg = "#FFFFFF"
        button_bg = "#010917"
        button_fg = "#FFFFFF"
        button_active = "#4A4D52"

        self.style.configure('.', background=bg, foreground=text_fg)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, foreground=text_fg, font=NORMAL_FONT)
        self.style.configure('Title.TLabel', font=TITLE_FONT, background=bg)
        self.style.configure('TButton',
                             background=button_bg,
                             foreground=button_fg,
                             font=('Segoe UI', 12, 'bold'),
                             padding=10)
        self.style.map('TButton', background=[('active', button_active)])

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- عنوان ---
        title = ttk.Label(main_frame, text="Grammar Input", style='Title.TLabel')
        title.pack(fill=tk.X, pady=(0, 5))

        # --- پیام راهنما ---
        helper = ttk.Label(main_frame,
                           text="⚠️ The grammar start symbol is assumed to be 'E' <by default> ." ,
                           foreground="#CCCCCC",
                           font=("Segoe UI", 10))
        helper.pack(fill=tk.X, pady=(0, 10))

        # --- TextBox گرامر ---
        self.grammar_box = scrolledtext.ScrolledText(main_frame,
                                                     wrap=tk.WORD,
                                                     height=10,
                                                     font=('Consolas', 12),
                                                     bg="#2B2D31",
                                                     fg="#E0E0E0",
                                                     insertbackground="white")
        self.grammar_box.insert(tk.INSERT,
"""E: T E'
E': + T E' | ε
T: F T'
T': * F T' | ε
F: ( E ) | id""")
        self.grammar_box.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # --- دکمه Run ---
        run_btn = ttk.Button(main_frame, text="Compute FIRST & FOLLOW", command=self.run_analysis)
        run_btn.pack(fill=tk.X, pady=(0, 20))

        # --- خروجی‌ها ---
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(1, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)

        self.first_output = self._create_output_box(output_frame, "FIRST Sets")
        self.first_output.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.follow_output = self._create_output_box(output_frame, "FOLLOW Sets")
        self.follow_output.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    def _create_output_box(self, parent, title_text):
        frame = ttk.Frame(parent, padding=10)
        title = ttk.Label(frame, text=title_text, font=("Segoe UI", 12, "bold"), anchor='center')
        title.pack(fill=tk.X, pady=(0, 5))

        text_box = scrolledtext.ScrolledText(frame,
                                             wrap=tk.WORD,
                                             height=15,
                                             font=("Consolas", 13),
                                             bg="#1D1F22",
                                             fg="#E0E0E0",
                                             insertbackground="white")
        text_box.pack(fill=tk.BOTH, expand=True)
        frame.text_box = text_box
        return frame

    def run_analysis(self):
        raw = self.grammar_box.get("1.0", tk.END).strip()
        grammar = parse_grammar(raw)

        self.first_output.text_box.delete("1.0", tk.END)
        self.follow_output.text_box.delete("1.0", tk.END)

        if not grammar:
            messagebox.showwarning("خطا در ورودی", "لطفاً گرامر معتبر را وارد کنید.")
            return

        try:
            start_symbol = list(grammar.keys())[0]
            analyzer = GrammarAnalyzer(grammar, start_symbol=start_symbol)
            analyzer.compute_follow_sets()
            self._show_sets(self.first_output.text_box, analyzer.first)
            self._show_sets(self.follow_output.text_box, analyzer.follow)
        except Exception as e:
            messagebox.showerror("خطای محاسبه", f"در محاسبه First/Follow خطایی رخ داد: \n{e}")

    def _show_sets(self, box, data):
        output_lines = []
        for nt in sorted(data.keys()):
            items = data[nt]
            line = f"{nt}:  {{ {', '.join(sorted(items))} }}"
            output_lines.append(line)
        box.insert(tk.END, "\n".join(output_lines))

# ---------------- اجرای برنامه ----------------
if __name__ == "__main__":
    app = GrammarGUI()
    app.mainloop()
