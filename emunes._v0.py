import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

THEMES = {
    "Dark": {
        "bg": "#21232c",
        "fg": "#e3e6ee",
        "panel": "#292a36",
        "button": "#3a3d4d",
        "text": "#181926",
        "cat": "#b28cff"
    },
    "Aero": {
        "bg": "#cbe6ff",
        "fg": "#183152",
        "panel": "#eaf6ff",
        "button": "#b3d0f7",
        "text": "#f5faff",
        "cat": "#5596ea"
    },
    "Light Blue": {
        "bg": "#e9f6ff",
        "fg": "#146ba7",
        "panel": "#d7eaff",
        "button": "#bee0fb",
        "text": "#ffffff",
        "cat": "#7bbdff"
    }
}

class Dummy6502CPU:
    def __init__(self, prg_rom):
        self.prg_rom = prg_rom
        self.pc = 0  # Program Counter
        self.cycles = 0

    def step(self):
        if self.pc < len(self.prg_rom):
            opcode = self.prg_rom[self.pc]
            self.pc += 1
            self.cycles += 2  # pretend every op is 2 cycles
            return opcode
        return 0x00  # NOP if out of ROM

class CatNESApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.themename = "Dark"
        self.theme = THEMES[self.themename]
        self.title("CatNES – NES Emulator")
        self.geometry("570x480")
        self.resizable(False, False)
        self.configure(bg=self.theme["bg"])

        self.header = tk.Label(self, text="CatNES Emulator", font=("Segoe UI", 18, "bold"))
        self.header.pack(pady=8)
        self.theme_btn = tk.Button(self, text="Toggle Theme", font=("Segoe UI", 10), command=self.toggle_theme)
        self.theme_btn.pack(pady=2)

        self.open_btn = tk.Button(self, text="Open NES ROM", command=self.load_rom, font=("Segoe UI", 12))
        self.open_btn.pack(pady=4)

        self.info_text = tk.Label(self, text="No ROM loaded.", font=("Segoe UI", 11), anchor="w", justify="left")
        self.info_text.pack(pady=3)

        self.opcode_area = scrolledtext.ScrolledText(self, width=56, height=7, font=("Consolas", 11), state="normal")
        self.opcode_area.pack(pady=4)

        # --- PPU Screen Canvas ---
        ppu_frame = tk.Frame(self, bg=self.theme["panel"], bd=2, relief="groove")
        ppu_frame.pack(pady=8)
        self.ppu_canvas = tk.Canvas(ppu_frame, width=256, height=240, bg=self.theme["text"], bd=0, highlightthickness=0)
        self.ppu_canvas.pack()
        self.ppu_test_pattern()

        self.run_btn = tk.Button(self, text="Step CPU", command=self.step_cpu, state="disabled")
        self.run_btn.pack(pady=2)

        self.cat_footer = tk.Label(self, text="=＾● ⋏ ●＾=   CatNES – Windows 11 style", font=("Segoe UI", 10))
        self.cat_footer.pack(side="bottom", pady=3)

        self.cpu = None
        self.update_theme()

    def toggle_theme(self):
        names = list(THEMES.keys())
        idx = (names.index(self.themename) + 1) % len(names)
        self.themename = names[idx]
        self.theme = THEMES[self.themename]
        self.update_theme()
        self.ppu_test_pattern()

    def update_theme(self):
        t = self.theme
        self.configure(bg=t["bg"])
        self.header.config(bg=t["bg"], fg=t["fg"])
        self.theme_btn.config(bg=t["button"], fg=t["fg"])
        self.open_btn.config(bg=t["button"], fg=t["fg"])
        self.info_text.config(bg=t["bg"], fg=t["fg"])
        self.opcode_area.config(bg=t["text"], fg=t["fg"], insertbackground=t["fg"])
        self.cat_footer.config(bg=t["bg"], fg=t["cat"])
        self.run_btn.config(bg=t["button"], fg=t["fg"])
        # Canvas/frame colors
        self.ppu_canvas.config(bg=t["text"])
        self.ppu_canvas.master.config(bg=t["panel"])

    def load_rom(self):
        file_path = filedialog.askopenfilename(filetypes=[("NES ROMs", "*.nes")])
        if not file_path:
            return
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            if data[:4] != b"NES\x1a":
                raise ValueError("Not a valid NES ROM")
            prg_rom_size = data[4] * 16384
            prg_rom = data[16:16+prg_rom_size]
            self.cpu = Dummy6502CPU(prg_rom)
            self.info_text.config(text=f"Loaded: {file_path.split('/')[-1]}\nPRG: {prg_rom_size//1024} KB")
            self.opcode_area.delete(1.0, tk.END)
            self.opcode_area.insert(tk.END, "First 16 PRG bytes:\n" + " ".join(f"${b:02X}" for b in prg_rom[:16]))
            self.run_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("CatNES Error", str(e))

    def step_cpu(self):
        if self.cpu:
            opcode = self.cpu.step()
            self.cat_footer.config(text=f"Stepped CPU! PC={self.cpu.pc} OPCODE=${opcode:02X} | Cycles={self.cpu.cycles}")
        else:
            self.cat_footer.config(text="No ROM loaded.")

    def ppu_test_pattern(self):
        """Draws a checkerboard test pattern for PPU output (easy to swap later)."""
        self.ppu_canvas.delete("all")
        block = 16
        for y in range(0, 240, block):
            for x in range(0, 256, block):
                fill = self.theme["cat"] if ((x//block) ^ (y//block)) & 1 else self.theme["panel"]
                self.ppu_canvas.create_rectangle(x, y, x+block, y+block, fill=fill, outline=fill)

if __name__ == "__main__":
    app = CatNESApp()
    app.mainloop()
