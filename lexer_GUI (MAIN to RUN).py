import sys
import subprocess
from tkinter import filedialog, messagebox, ttk
try:
    import customtkinter as ctk
except ImportError:
        
    response = messagebox.askyesno(
        "Dependency Missing", 
        "The 'customtkinter' library is required to run the Program.\n"
        "Do you want to install it now using pip?"
    )
    
    if response:
        try:
            print("Attempting to install 'customtkinter'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
            print("'customtkinter' installed successfully. Please restart the application.")
            
            sys.exit(0)
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Installation Failed", 
                f"Failed to install 'customtkinter'. Please run 'pip install customtkinter' manually.\nError: {e}"
            )
            sys.exit(1)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An unexpected error occurred during installation: {e}"
            )
            sys.exit(1)
    else:
        messagebox.showinfo("Exit", "Cannot run the application without 'customtkinter'. Exiting.")
        sys.exit(0)



from lexer import Lexer 

TOKEN_COLORS = {
    'number': "#15b1c9",    
    'keyword': "#8052a8",    
    'id': "#1ac358",        
    'relop': '#fb923c',      
    'op': "#f04aa0",         
    'delimiter': '#9ca3af',  
    'comment': "#6b7280",    
    'string': "#f6c500",     
    'error': "#e50000"       
}

class LexerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Lexer Analyzer")
        self.geometry("820x720")  

        self.tokens = []
        self.symbol_table = {}

        # ---------- Input Text ----------
        self.code_text = ctk.CTkTextbox(self, height=220)
        self.code_text.configure(font=("Consolas", 14))
        self.code_text.pack(fill="x", padx=10, pady=(10,5))

        # ---------- Buttons ----------
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.upload_btn = ctk.CTkButton(btn_frame, text="Upload File", command=self.upload_file)
        self.upload_btn.pack(side="left", padx=5)

        self.analyze_btn = ctk.CTkButton(btn_frame, text="Analyze Code", command=self.analyze_code)
        self.analyze_btn.pack(side="left", padx=5)

        self.download_btn = ctk.CTkButton(btn_frame, text="Download Output", command=self.download_output)
        self.download_btn.pack(side="left", padx=5)

        # ---------- Tokens Table ----------
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
                        font=("Consolas", 12),
                        rowheight=28,
                        background="#1f2937", foreground="white",
                        fieldbackground="#1f2937")
        style.configure("Treeview.Heading", font=("Consolas", 13, "bold"))

        self.token_table = ttk.Treeview(self, columns=("No", "Token", "Line"), show='headings', height=14)
        self.token_table.heading("No", text="#")
        self.token_table.heading("Token", text="Token")
        self.token_table.heading("Line", text="Line")
        self.token_table.column("No", width=50, anchor="center")
        self.token_table.column("Token", width=420)    
        self.token_table.column("Line", width=80, anchor="center")
        self.token_table.pack(fill="both", padx=10, pady=5, expand=True)

        # ---------- Symbol Table ----------
        self.sym_table = ttk.Treeview(self, columns=("Identifier", "Index"), show='headings', height=6)
        self.sym_table.heading("Identifier", text="Identifier")
        self.sym_table.heading("Index", text="Index")
        self.sym_table.column("Identifier", width=300)
        self.sym_table.column("Index", width=80, anchor="center")
        self.sym_table.pack(fill="x", padx=10, pady=(0,10))

        for ttype, color in TOKEN_COLORS.items():
            if ttype == 'error':
                self.token_table.tag_configure(ttype, background=color, foreground='white', font=("Consolas", 12, "bold"))
            else:
                self.token_table.tag_configure(ttype, foreground=color)

    # ---------- Functions ----------
    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    self.code_text.delete("0.0", "end")
                    self.code_text.insert("0.0", code)
                    self.tokens.clear()
                    self.symbol_table.clear()
                    self.clear_tables()
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def clear_tables(self):
        for row in self.token_table.get_children():
            self.token_table.delete(row)
        for row in self.sym_table.get_children():
            self.sym_table.delete(row)

    def analyze_code(self):
        code = self.code_text.get("0.0", "end-1c")
        if not code.strip():
            messagebox.showwarning("Warning", "Please enter or upload code")
            return

        lexer = Lexer(code)
        self.tokens, self.symbol_table = lexer.tokenize()
        self.clear_tables()

        for idx, (token, line, ttype) in enumerate(self.tokens, 1):
            self.token_table.insert("", "end", values=(idx, token, line), tags=(ttype,))

        for name, idx in self.symbol_table.items():
            self.sym_table.insert("", "end", values=(name, idx))


    def download_output(self):
        if not self.tokens:
            messagebox.showwarning("Warning", "No tokens to save")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    
                    for idx, (token, line, ttype) in enumerate(self.tokens, 1):
                        f.write(f"{token} [line:{line}]\n")
                        
                messagebox.showinfo("Saved", f"Output saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

# ---------- Run Application ----------
if __name__ == "__main__":
    app = LexerGUI()
    app.mainloop()