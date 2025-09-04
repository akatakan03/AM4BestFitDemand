# Airline Manager 4 - Üç sınıflı koltuk konfigüratörü (GUI + opsiyonel sınıf kapatma)
# Y = 1 birim, J = 2 birim, F = 3 birim
# Amaç: Verilen Y-birim kapasitesini %100 doldururken (y + 2j + 3f = CAP),
#       (y, j, f) oranını talep oranına (dY, dJ, dF) mümkün olduğunca yaklaştırmak.

import tkinter as tk
from tkinter import ttk, messagebox

def find_best_config(capacity, dY, dJ, dF):
    # Üç sınıflı çözüm (orijinal)
    total_demand = dY + dJ + dF
    if total_demand == 0:
        return capacity, 0, 0

    ty, tj, tf = dY / total_demand, dJ / total_demand, dF / total_demand

    best = None  # (score, y, j, f)
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
            if dY == 0 and y > 0: penalty += 0.05
            if dJ == 0 and j > 0: penalty += 0.05
            if dF == 0 and f > 0: penalty += 0.05
            tie_break = 1e-6 * (j + 2 * f)
            score = err + penalty + tie_break
            if best is None or score < best[0]:
                best = (score, y, j, f)
    _, y, j, f = best
    return y, j, f

def find_best_config_two_classes(capacity, dY, dJ, dF, disabled):
    """
    İki sınıflı çözüm: 'disabled' sınıfı kapatılır.
    disabled in {"Y","J","F"}
    """
    total_demand = dY + dJ + dF
    # Talep sıfırsa, ulaşılabilir iki sınıflı en basit dolum:
    if total_demand == 0:
        if disabled == "Y":
            # 2j + 3f = cap
            # Her zaman çözülebilir (cap büyük/kullanışlı değerlerde); basit bir çözüm ara
            best = None
            for f in range(0, capacity // 3 + 1):
                rem = capacity - 3 * f
                if rem % 2 == 0:
                    j = rem // 2
                    y = 0
                    best = (0, y, j, f)
                    break
            if best is None:
                raise ValueError("No solution found.")
            _, y, j, f = best
            return y, j, f
        elif disabled == "J":
            # y + 3f = cap
            f = capacity // 3
            y = capacity - 3 * f
            return y, 0, f
        elif disabled == "F":
            # y + 2j = cap
            j = capacity // 2
            y = capacity - 2 * j
            return y, j, 0

    # Skor fonksiyonu (iki sınıf için de aynı mantık)
    def score(y, j, f):
        seats = y + j + f
        if seats == 0:
            return float("inf")
        ry, rj, rf = y / seats, j / seats, f / seats
        ty = dY / total_demand if total_demand else 0.0
        tj = dJ / total_demand if total_demand else 0.0
        tf = dF / total_demand if total_demand else 0.0
        err = (ry - ty) ** 2 + (rj - tj) ** 2 + (rf - tf) ** 2
        penalty = 0.0
        if dY == 0 and y > 0: penalty += 0.05
        if dJ == 0 and j > 0: penalty += 0.05
        if dF == 0 and f > 0: penalty += 0.05
        tie_break = 1e-6 * (j + 2 * f)
        return err + penalty + tie_break

    best = None  # (score, y, j, f)

    if disabled == "Y":
        # y=0, 2j + 3f = capacity
        for f in range(0, capacity // 3 + 1):
            rem = capacity - 3 * f
            if rem < 0:
                continue
            if rem % 2 != 0:
                continue
            j = rem // 2
            y = 0
            s = score(y, j, f)
            if best is None or s < best[0]:
                best = (s, y, j, f)

    elif disabled == "J":
        # j=0, y + 3f = capacity
        for f in range(0, capacity // 3 + 1):
            y = capacity - 3 * f
            if y < 0:
                continue
            s = score(y, 0, f)
            if best is None or s < best[0]:
                best = (s, y, 0, f)

    elif disabled == "F":
        # f=0, y + 2j = capacity
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
        self.geometry("600x430")
        self.resizable(False, False)

        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        row = 0
        ttk.Label(main, text="Y-unit capacity of the plane (e.g. 184):").grid(row=row, column=0, sticky="w")
        self.cap_var = tk.StringVar(value="184")
        ttk.Entry(main, textvariable=self.cap_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Route Y (Economy) request:").grid(row=row, column=0, sticky="w")
        self.dy_var = tk.StringVar(value="824")
        ttk.Entry(main, textvariable=self.dy_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Route J (Business) request:").grid(row=row, column=0, sticky="w")
        self.dj_var = tk.StringVar(value="413")
        ttk.Entry(main, textvariable=self.dj_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(main, text="Route F (First) request:").grid(row=row, column=0, sticky="w")
        self.df_var = tk.StringVar(value="216")
        ttk.Entry(main, textvariable=self.df_var, width=12).grid(row=row, column=1, sticky="w")
        row += 1

        # --- Radiobutton bölümü: en fazla 1 seçili, 0 da olabilir ---
        rb_frame = ttk.LabelFrame(main, text="Class closure (optional)", padding=8)
        rb_frame.grid(row=row, column=0, columnspan=2, pady=8, sticky="we")
        rb_frame.columnconfigure(0, weight=1)
        rb_frame.columnconfigure(1, weight=1)
        rb_frame.columnconfigure(2, weight=1)

        # StringVar varsayılan "" → hiçbir radiobutton seçili değil (0 seçili mümkün)
        self.disable_var = tk.StringVar(value="")  # "", "Y", "J", "F"

        self.rb_y = ttk.Radiobutton(rb_frame, text="Close Y", value="Y", variable=self.disable_var)
        self.rb_j = ttk.Radiobutton(rb_frame, text="Close J", value="J", variable=self.disable_var)
        self.rb_f = ttk.Radiobutton(rb_frame, text="Close F", value="F", variable=self.disable_var)
        self.rb_y.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.rb_j.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.rb_f.grid(row=0, column=2, sticky="w", padx=4, pady=2)
        row += 1

        ttk.Button(main, text="Calculate", command=self.calculate).grid(row=row, column=0, columnspan=2, pady=10, sticky="we")
        row += 1

        self.result_text = tk.Text(main, height=12, width=70, state="disabled")
        self.result_text.grid(row=row, column=0, columnspan=2, pady=6, sticky="we")

        for i in range(2):
            main.columnconfigure(i, weight=1)

    def calculate(self):
        try:
            cap = int(self.cap_var.get().strip())
            dY = int(self.dy_var.get().strip())
            dJ = int(self.dj_var.get().strip())
            dF = int(self.df_var.get().strip())
            if cap < 0 or dY < 0 or dJ < 0 or dF < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Please enter non-negative integers in all fields.")
            return

        disabled = self.disable_var.get()  # "", "Y", "J", "F"
        try:
            if disabled == "":
                y, j, f = find_best_config(cap, dY, dJ, dF)
                mode_note = "Mode: Three-class (no class is closed)"
            else:
                y, j, f = find_best_config_two_classes(cap, dY, dJ, dF, disabled)
                mode_note = f"Mode: Two-class (closed class: {disabled})"
        except Exception as e:
            messagebox.showerror("Error", f"No solution found: {e}")
            return

        used_units = y + 2*j + 3*f
        seats = max(1, y + j + f)
        ry, rj, rf = y / seats, j / seats, f / seats
        total_d = max(1, dY + dJ + dF)
        ty, tj, tf = dY / total_d, dJ / total_d, dF / total_d

        out = []
        out.append(mode_note)
        out.append("--- RECOMMENDED CONFIGURATION ---")
        out.append(f"Y (Economy): {y}")
        out.append(f"J (Business): {j}")
        out.append(f"F (First): {f}")
        out.append(f"Capacity utilization: {used_units}/{cap} Y-unit (%{round(100*used_units/cap)})")
        out.append("")
        out.append("Rate comparison (seat rate vs demand rate):")
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
