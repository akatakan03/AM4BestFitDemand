import tkinter as tk
from tkinter import ttk, messagebox

def find_best_config(capacity, dy, dj, df):
    total_demand = dy + dj + df
    if total_demand == 0:
        return capacity, 0, 0

    ty, tj, tf = dy / total_demand, dj / total_demand, df / total_demand
    best = None
    for f in range(0, capacity // 3 + 1):
        remaining_after_f = capacity - 3 * f
        for j in range(0, remaining_after_f // 2 + 1):
            y = remaining_after_f - 2 * j
            seats = y + j + f
            if seats == 0:
                continue
            ry, rj, rf = y / seats, j / seats, f / seats
            err = (ry - ty) ** 2 + (rj - tj) ** 2 + (rf - tf) ** 2
            penalty = 0.0
            if dy == 0 and y > 0: penalty += 0.05
            if dj == 0 and j > 0: penalty += 0.05
            if df == 0 and f > 0: penalty += 0.05
            tie_break = 1e-6 * (j + 2 * f)
            score = err + penalty + tie_break
            if best is None or score < best[0]:
                best = (score, y, j, f)
    _, y, j, f = best
    return y, j, f

def find_best_config_two_classes(capacity, dy, dj, df, disabled):
    total_demand = dy + dj + df
    if total_demand == 0:
        if disabled == "Y":
            for f in range(0, capacity // 3 + 1):
                rem = capacity - 3 * f
                if rem % 2 == 0:
                    return 0, rem // 2, f
            raise ValueError("No solution found.")
        elif disabled == "J":
            f = capacity // 3
            return capacity - 3 * f, 0, f
        elif disabled == "F":
            j = capacity // 2
            return capacity - 2 * j, j, 0

    def score(y, j, f):
        seats = y + j + f
        if seats == 0:
            return float("inf")
        ry, rj, rf = y / seats, j / seats, f / seats
        ty = dy / total_demand if total_demand else 0.0
        tj = dj / total_demand if total_demand else 0.0
        tf = df / total_demand if total_demand else 0.0
        err = (ry - ty) ** 2 + (rj - tj) ** 2 + (rf - tf) ** 2
        penalty = 0.0
        if dy == 0 and y > 0: penalty += 0.05
        if dj == 0 and j > 0: penalty += 0.05
        if df == 0 and f > 0: penalty += 0.05
        tie_break = 1e-6 * (j + 2 * f)
        return err + penalty + tie_break

    best = None
    if disabled == "Y":
        for f in range(0, capacity // 3 + 1):
            rem = capacity - 3 * f
            if rem % 2 != 0:
                continue
            y = 0
            j = rem // 2
            s = score(y, j, f)
            if best is None or s < best[0]:
                best = (s, y, j, f)
    elif disabled == "J":
        for f in range(0, capacity // 3 + 1):
            y = capacity - 3 * f
            if y < 0:
                continue
            s = score(y, 0, f)
            if best is None or s < best[0]:
                best = (s, y, 0, f)
    elif disabled == "F":
        for j in range(0, capacity // 2 + 1):
            y = capacity - 2 * j
            if y < 0:
                continue
            s = score(y, j, 0)
            if best is None or s < best[0]:
                best = (s, y, j, 0)
    else:
        raise ValueError("Invalid 'disabled' parameter.")
    if best is None:
        raise ValueError("No suitable solution found with the given constraint.")
    _, y, j, f = best
    return y, j, f

# --------- GUI ---------
class SeatConfiguratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Three-Class Seat Configurator (Y=1, J=2, F=3)")
        self.geometry("600x460")
        self.resizable(False, False)

        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        row = 0
        ttk.Label(main, text="Y-unit capacity of the plane (e.g. 184):").grid(row=row, column=0, sticky="w")
        self.cap_var = tk.StringVar(value="184")
        ttk.Entry(main, textvariable=self.cap_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Route Y (Economy) demand:").grid(row=row, column=0, sticky="w")
        self.dy_var = tk.StringVar(value="824")
        ttk.Entry(main, textvariable=self.dy_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Route J (Business) demand:").grid(row=row, column=0, sticky="w")
        self.dj_var = tk.StringVar(value="413")
        ttk.Entry(main, textvariable=self.dj_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Route F (First) demand:").grid(row=row, column=0, sticky="w")
        self.df_var = tk.StringVar(value="216")
        ttk.Entry(main, textvariable=self.df_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        # --- Radiobuttons (with toggle-to-deselect) ---
        rb_frame = ttk.LabelFrame(main, text="Disable a class (optional)", padding=8)
        rb_frame.grid(row=row, column=0, columnspan=2, pady=8, sticky="we")
        for c in range(3):
            rb_frame.columnconfigure(c, weight=1)

        self.disable_var = tk.StringVar(value="")  # "", "Y", "J", "F"

        self.rb_y = ttk.Radiobutton(rb_frame, text="Close Y", value="Y", variable=self.disable_var)
        self.rb_j = ttk.Radiobutton(rb_frame, text="Close J", value="J", variable=self.disable_var)
        self.rb_f = ttk.Radiobutton(rb_frame, text="Close F", value="F", variable=self.disable_var)

        # === kritik kısım: aynı seçeneğe tekrar tıklanınca seçimi kaldır ===
        self.rb_y.bind("<Button-1>", lambda e, v="Y": self._on_radio_click(e, v))
        self.rb_j.bind("<Button-1>", lambda e, v="J": self._on_radio_click(e, v))
        self.rb_f.bind("<Button-1>", lambda e, v="F": self._on_radio_click(e, v))

        self.rb_y.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.rb_j.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.rb_f.grid(row=0, column=2, sticky="w", padx=4, pady=2)
        row += 1

        # (İstersen kolaylık için) Clear butonu
        ttk.Button(main, text="Clear selection", command=lambda: self.disable_var.set("")).grid(
            row=row, column=0, columnspan=2, pady=4, sticky="we"
        )
        row += 1

        ttk.Button(main, text="Calculate", command=self.calculate).grid(row=row, column=0, columnspan=2, pady=10, sticky="we")
        row += 1

        self.result_text = tk.Text(main, height=12, width=70, state="disabled")
        self.result_text.grid(row=row, column=0, columnspan=2, pady=6, sticky="we")

        for i in range(2):
            main.columnconfigure(i, weight=1)

    def _on_radio_click(self, event, value):
        """Aynı radiobutton'a tıklanınca seçimi kaldır ("" yap) ve Tk'nin default set etmesini engelle."""
        current = self.disable_var.get()
        if current == value:
            self.disable_var.set("")   # seçimi temizle
            return "break"             # default davranışı iptal et (yoksa tekrar aynı değeri yazardı)
        # farklı bir seçenekse, Tk varsayılan şekilde o değeri set edecek (None döndür)

    def calculate(self):
        try:
            cap = int(self.cap_var.get().strip())
            dy = int(self.dy_var.get().strip())
            dj = int(self.dj_var.get().strip())
            df = int(self.df_var.get().strip())
            if cap < 0 or dy < 0 or dj < 0 or df < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Please enter non-negative integers in all fields.")
            return

        disabled = self.disable_var.get()  # "", "Y", "J", "F"
        try:
            if disabled == "":
                y, j, f = find_best_config(cap, dy, dj, df)
                mode_note = "Mode: Three-class (no class disabled)"
            else:
                y, j, f = find_best_config_two_classes(cap, dy, dj, df, disabled)
                mode_note = f"Mode: Two-class (disabled: {disabled})"
        except Exception as e:
            messagebox.showerror("Error", f"No solution found: {e}")
            return

        used_units = y + 2*j + 3*f
        seats = max(1, y + j + f)
        ry, rj, rf = y / seats, j / seats, f / seats
        total_d = max(1, dy + dj + df)
        ty, tj, tf = dy / total_d, dj / total_d, df / total_d

        out = []
        out.append(mode_note)
        out.append("--- RECOMMENDED CONFIGURATION ---")
        out.append(f"Y (Economy): {y}")
        out.append(f"J (Business): {j}")
        out.append(f"F (First): {f}")
        out.append(f"Capacity utilization: {used_units}/{cap} Y-unit (%{round(100*used_units/cap)})")
        out.append("")
        out.append("Rate comparison (seat vs demand):")
        out.append(f"Y: {ry:.3f} vs {ty:.3f}")
        out.append(f"J: {rj:.3f} vs {tj:.3f}")
        out.append(f"F: {rf:.3f} vs {tf:.3f}")

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "\n".join(out))
        self.result_text.config(state="disabled")

def main():
    app = SeatConfiguratorApp()
    app.mainloop()

if __name__ == "__main__":
    main()
