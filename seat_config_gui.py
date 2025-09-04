import tkinter as tk
from tkinter import ttk, messagebox
import math

# ---------------- Core seat solvers ----------------
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

# ---------------- Helpers ----------------
def parse_hms_to_hours(text: str) -> float:
    parts = text.strip().split(":")
    if not parts or any(p.strip() == "" for p in parts):
        raise ValueError("Invalid time string")
    try:
        if len(parts) == 1:
            h = int(parts[0]); m = 0; s = 0
        elif len(parts) == 2:
            h, m = map(int, parts); s = 0
        elif len(parts) == 3:
            h, m, s = map(int, parts)
        else:
            raise ValueError("Too many parts")
        if h < 0 or m < 0 or s < 0:
            raise ValueError("Negative not allowed")
        if m >= 60 or s >= 60:
            raise ValueError("Minutes/seconds must be < 60")
        return h + m/60 + s/3600
    except Exception as e:
        raise ValueError("Use HH, HH:MM or HH:MM:SS") from e

# ---------------- GUI ----------------
class SeatConfiguratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Three-Class Seat Configurator (Y=1, J=2, F=3)")
        self.geometry("640x560")
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

        # Optional scheduling inputs
        opt = ttk.LabelFrame(main, text="Optional scheduling inputs", padding=8)
        opt.grid(row=row, column=0, columnspan=2, pady=8, sticky="we")
        opt.columnconfigure(1, weight=1)

        ttk.Label(opt, text="Flight time (HH:MM:SS):").grid(row=0, column=0, sticky="w")

        time_frame = ttk.Frame(opt)
        time_frame.grid(row=0, column=1, sticky="w")
        self.hour_var = tk.IntVar(value=0)
        self.min_var = tk.IntVar(value=0)
        self.sec_var = tk.IntVar(value=0)
        tk.Spinbox(time_frame, from_=0, to=23, textvariable=self.hour_var, width=3).grid(row=0, column=0)
        tk.Label(time_frame, text=":").grid(row=0, column=1)
        tk.Spinbox(time_frame, from_=0, to=59, textvariable=self.min_var, width=3).grid(row=0, column=2)
        tk.Label(time_frame, text=":").grid(row=0, column=3)
        tk.Spinbox(time_frame, from_=0, to=59, textvariable=self.sec_var, width=3).grid(row=0, column=4)

        ttk.Label(opt, text="Reputation (%) [1–99]:").grid(row=1, column=0, sticky="w")
        self.rep_var = tk.StringVar(value="")
        ttk.Entry(opt, textvariable=self.rep_var, width=12).grid(row=1, column=1, sticky="w")
        row += 1

        # Disable-class (toggle-to-deselect)
        rb_frame = ttk.LabelFrame(main, text="Disable a class (optional)", padding=8)
        rb_frame.grid(row=row, column=0, columnspan=2, pady=8, sticky="we")
        for c in range(3):
            rb_frame.columnconfigure(c, weight=1)

        self.disable_var = tk.StringVar(value="")  # "", "Y", "J", "F"
        self.rb_y = ttk.Radiobutton(rb_frame, text="Close Y", value="Y", variable=self.disable_var)
        self.rb_j = ttk.Radiobutton(rb_frame, text="Close J", value="J", variable=self.disable_var)
        self.rb_f = ttk.Radiobutton(rb_frame, text="Close F", value="F", variable=self.disable_var)
        self.rb_y.bind("<Button-1>", lambda e, v="Y": self._on_radio_click(e, v))
        self.rb_j.bind("<Button-1>", lambda e, v="J": self._on_radio_click(e, v))
        self.rb_f.bind("<Button-1>", lambda e, v="F": self._on_radio_click(e, v))
        self.rb_y.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.rb_j.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.rb_f.grid(row=0, column=2, sticky="w", padx=4, pady=2)
        row += 1

        ttk.Button(main, text="Clear selection", command=lambda: self.disable_var.set("")).grid(
            row=row, column=0, columnspan=2, pady=4, sticky="we"
        )
        row += 1

        ttk.Button(main, text="Calculate", command=self.calculate).grid(row=row, column=0, columnspan=2, pady=10, sticky="we")
        row += 1

        self.result_text = tk.Text(main, height=16, width=80, state="disabled")
        self.result_text.grid(row=row, column=0, columnspan=2, pady=6, sticky="we")

        for i in range(2):
            main.columnconfigure(i, weight=1)

    def _on_radio_click(self, event, value):
        current = self.disable_var.get()
        if current == value:
            self.disable_var.set("")
            return "break"

    def _compute_required_flights(self, y, j, f, dy, dj, df, rep_percent):
        rep = (rep_percent / 100.0) if rep_percent is not None else 1.0
        sell_y = int(math.floor(y * rep))
        sell_j = int(math.floor(j * rep))
        sell_f = int(math.floor(f * rep))

        reasons = []
        need_list = []

        if dy > 0:
            if sell_y == 0: reasons.append("Economy demand cannot be served with current reputation/seat mix.")
            else: need_list.append(math.ceil(dy / sell_y))
        if dj > 0:
            if sell_j == 0: reasons.append("Business demand cannot be served with current reputation/seat mix.")
            else: need_list.append(math.ceil(dj / sell_j))
        if df > 0:
            if sell_f == 0: reasons.append("First demand cannot be served with current reputation/seat mix.")
            else: need_list.append(math.ceil(df / sell_f))

        if reasons:
            return None, " / ".join(reasons)
        needed = max(need_list) if need_list else 0
        return needed, ""

    def calculate(self):
        # Required fields
        try:
            cap = int(self.cap_var.get().strip())
            dy = int(self.dy_var.get().strip())
            dj = int(self.dj_var.get().strip())
            df = int(self.df_var.get().strip())
            if cap < 0 or dy < 0 or dj < 0 or df < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Please enter non-negative integers in capacity and demand fields.")
            return

        # Optional fields
        rep_percent = None
        flight_time = None
        try:
            rep_txt = self.rep_var.get()
            if rep_txt.strip() != "":
                rep_percent = int(rep_txt)
                if not (1 <= rep_percent <= 99):
                    raise ValueError
        except Exception:
            messagebox.showerror("Error", "Reputation must be an integer between 1 and 99 (or leave empty).")
            return

        try:
            h = self.hour_var.get()
            m = self.min_var.get()
            s = self.sec_var.get()
            flight_time = h + m / 60 + s / 3600
            if flight_time <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Flight time must be a valid positive number.")
            return

        # Solve seats
        disabled = self.disable_var.get()
        try:
            if disabled == "":
                y, j, f = find_best_config(cap, dy, dj, df)
                mode_note = "Mode: Three-class (no class disabled)"
            else:
                y, j, f = find_best_config_two_classes(cap, dy, dj, df, disabled)
                mode_note = f"Mode: Two-class (disabled: {disabled})"
        except Exception as e:
            messagebox.showerror("Error", f"No seat solution found: {e}")
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

        # Optional scheduling calc (+ minimum aircraft count)
        if rep_percent is not None:
            needed, reason = self._compute_required_flights(y, j, f, dy, dj, df, rep_percent)
            out.append("")
            out.append(f"Reputation used: {rep_percent}%")
            if needed is None:
                out.append(f"Flights needed (per day): IMPOSSIBLE – {reason}")
            else:
                out.append(f"Flights needed (per day) to cover demand: {needed}")
                if flight_time is not None:
                    max_flights_per_plane = int(math.floor(24.0 / flight_time))
                    max_flights = math.ceil(needed / max_flights_per_plane)
                    out.append(f"Max flights per aircraft per day: {max_flights}")

                    if max_flights <= 0:
                        out.append("❌ With this flight time, an aircraft cannot complete even one flight per day.")
                        out.append("   → Use shorter routes, faster aircraft, or ignore flight-time constraint.")
                    else:
                        required_aircraft = math.ceil(needed / max_flights)
                        out.append(f"🛩️ Minimum aircraft to serve full daily demand: {required_aircraft}")

                        if max_flights >= needed:
                            out.append("✅ One aircraft can cover the demand with this schedule.")
                        else:
                            deficit = needed - max_flights
                            out.append(f"⚠️ One aircraft cannot cover the demand. Short by {deficit} flights/day.")
                            out.append("   → Add aircraft, increase frequency, or adjust seat mix.")

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "\n".join(out))
        self.result_text.config(state="disabled")

def main():
    app = SeatConfiguratorApp()
    app.mainloop()

if __name__ == "__main__":
    main()
