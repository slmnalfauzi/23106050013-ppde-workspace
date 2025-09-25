import tkinter as tk
import math
import time

class StopwatchApp:
    def buat_penanda_waktu(self):
        """Gambar titik-titik penanda detik/menit di lingkaran jam"""
        center_x, center_y = 150, 150
        radius_outer = 100
        radius_inner = 90
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            x_outer = center_x + radius_outer * math.cos(angle)
            y_outer = center_y + radius_outer * math.sin(angle)
            x_inner = center_x + radius_inner * math.cos(angle)
            y_inner = center_y + radius_inner * math.sin(angle)
            width = 2 if i % 5 == 0 else 1
            color = "white" if i % 5 == 0 else "#888"
            self.canvas.create_line(x_inner, y_inner, x_outer, y_outer, fill=color, width=width)
    def play_sound(self, event="beep"):
        try:
            import winsound
            if event == "start":
                winsound.Beep(1000, 120)
            elif event == "stop":
                winsound.Beep(600, 120)
            elif event == "reset":
                winsound.Beep(400, 120)
            elif event == "lap":
                winsound.Beep(1200, 80)
            elif event == "alarm":
                for _ in range(3):
                    winsound.Beep(1500, 200)
            else:
                winsound.MessageBeep()
        except Exception:
            self.flash_border()

    def flash_border(self):
        """Animasi flash border window sebagai notifikasi visual"""
        orig = self.window.cget("bg")
        def flash(count=0):
            if count < 4:
                color = "#ff0" if count % 2 == 0 else orig
                self.window.configure(bg=color)
                self.window.after(80, lambda: flash(count+1))
            else:
                self.window.configure(bg=orig)
        flash()
    def __init__(self, master=None):
        if master is None:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel(master)
        self.window.title("Stopwatch dengan Animasi")
        self.window.geometry("600x500")
        self.window.configure(bg="black")

        # Variabel untuk stopwatch
        self.start_time = 0
        self.elapsed_time = 0
        self.is_running = False
        self.timer_job = None

        # Variabel untuk animasi
        self.animation_job = None
        self.rotation_angle = 0

        # Variabel untuk countdown
        self.countdown_mode = False
        self.countdown_target = 0
        self.countdown_alarm_triggered = False

        self.theme = "dark"  # default

        self.buat_interface()
        self.start_animation()
        # Keyboard shortcuts
        self.window.bind('<space>', lambda e: self.toggle_stopwatch())
        self.window.bind('<r>', lambda e: self.reset_stopwatch())
        self.window.bind('<R>', lambda e: self.reset_stopwatch())
        self.window.bind('<l>', lambda e: self.record_lap())
        self.window.bind('<L>', lambda e: self.record_lap())
        # Auto-save/restore
        self.restore_state()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    def get_state_file(self):
        import os
        return os.path.join(os.path.expanduser("~"), ".stopwatch_state.json")

    def save_state(self):
        import json
        state = {
            "elapsed_time": self.elapsed_time,
            "lap_times": self.lap_times,
            "lap_count": self.lap_count,
            "theme": self.theme
        }
        try:
            with open(self.get_state_file(), "w", encoding="utf-8") as f:
                json.dump(state, f)
        except Exception:
            pass

    def restore_state(self):
        import json
        import os
        try:
            with open(self.get_state_file(), "r", encoding="utf-8") as f:
                state = json.load(f)
            self.elapsed_time = state.get("elapsed_time", 0)
            self.lap_times = state.get("lap_times", [])
            self.lap_count = state.get("lap_count", 0)
            self.theme = state.get("theme", "dark")
            # Tampilkan waktu
            self.time_label.config(text=self.format_time(self.elapsed_time))
            ms = int((self.elapsed_time % 1) * 1000)
            self.ms_label.config(text=f"{ms:03d}")
            # Tampilkan lap
            self.lap_listbox.delete(0, tk.END)
            for lap in self.lap_times:
                total_formatted = self.format_time(lap[1])
                lap_formatted = self.format_time(lap[2])
                lap_text = f"Lap {lap[0]:2d}: {lap_formatted} (Total: {total_formatted})"
                self.lap_listbox.insert(tk.END, lap_text)
            self.apply_theme()
        except Exception:
            pass

    def on_close(self):
        self.save_state()
        self.window.destroy()

    def buat_interface(self):
        # Frame untuk display waktu
        time_frame = tk.Frame(self.window, bg="black")
        time_frame.pack(pady=20)

        # Label untuk menampilkan waktu
        self.time_label = tk.Label(
            time_frame,
            text="00:00:00",
            font=("Digital-7", 48, "bold"),
            fg="lime",
            bg="black"
        )
        self.time_label.pack()

        # Label untuk milidetik
        self.ms_label = tk.Label(
            time_frame,
            text="000",
            font=("Digital-7", 24),
            fg="yellow",
            bg="black"
        )
        self.ms_label.pack()

        # Canvas untuk animasi
        self.canvas = tk.Canvas(
            self.window,
            width=300,
            height=300,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(pady=20)

        # Gambar lingkaran luar (static)
        self.canvas.create_oval(
            50, 50, 250, 250,
            outline="white",
            width=3,
            tags="outer_circle"
        )

        # Gambar titik-titik penanda waktu
        self.buat_penanda_waktu()

        # Jarum detik (akan beranimasi)
        self.jarum_detik = self.canvas.create_line(
            150, 150, 150, 70,
            fill="red",
            width=3,
            tags="second_hand"
        )

        # Titik tengah
        self.canvas.create_oval(
            145, 145, 155, 155,
            fill="white",
            outline="white"
        )

        # Frame untuk countdown
        countdown_frame = tk.Frame(self.window, bg="black")
        countdown_frame.pack(pady=5)
        tk.Label(countdown_frame, text="Countdown (detik):", font=("Arial", 10), bg="black", fg="white").pack(side=tk.LEFT)
        self.countdown_entry = tk.Entry(countdown_frame, width=8, font=("Arial", 10))
        self.countdown_entry.pack(side=tk.LEFT, padx=5)
        self.set_countdown_btn = tk.Button(countdown_frame, text="SET", font=("Arial", 10), command=self.set_countdown)
        self.set_countdown_btn.pack(side=tk.LEFT)

        # Frame untuk tombol kontrol
        control_frame = tk.Frame(self.window, bg="black")
        control_frame.pack(pady=20)

        # Tombol Start/Stop
        self.start_stop_btn = tk.Button(
            control_frame,
            text="START",
            font=("Arial", 14, "bold"),
            bg="green",
            fg="white",
            width=10,
            command=self.toggle_stopwatch
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Reset
        self.reset_btn = tk.Button(
            control_frame,
            text="RESET",
            font=("Arial", 14, "bold"),
            bg="red",
            fg="white",
            width=10,
            command=self.reset_stopwatch
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Lap
        self.lap_btn = tk.Button(
            control_frame,
            text="LAP",
            font=("Arial", 14, "bold"),
            bg="blue",
            fg="white",
            width=10,
            command=self.record_lap,
            state=tk.DISABLED
        )
        self.lap_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Export
        self.export_btn = tk.Button(
            control_frame,
            text="EXPORT",
            font=("Arial", 12),
            bg="#444",
            fg="white",
            width=8,
            command=self.export_laps
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Import
        self.import_btn = tk.Button(
            control_frame,
            text="IMPORT",
            font=("Arial", 12),
            bg="#444",
            fg="white",
            width=8,
            command=self.import_laps
        )
        self.import_btn.pack(side=tk.LEFT, padx=5)


        # Tombol Statistik
        self.stats_btn = tk.Button(
            control_frame,
            text="STATS",
            font=("Arial", 12),
            bg="#888",
            fg="white",
            width=8,
            command=self.show_stats
        )
        self.stats_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Grafik Lap
        self.lap_chart_btn = tk.Button(
            control_frame,
            text="LAP CHART",
            font=("Arial", 12),
            bg="#888",
            fg="white",
            width=10,
            command=self.show_lap_chart
        )
        self.lap_chart_btn.pack(side=tk.LEFT, padx=5)
    def show_lap_chart(self):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            import tkinter.messagebox as msg
            msg.showerror("Matplotlib Not Found", "matplotlib belum terinstal. Silakan install matplotlib terlebih dahulu.")
            return
        if not self.lap_times:
            import tkinter.messagebox as msg
            msg.showinfo("Lap Chart", "Belum ada lap yang dicatat.")
            return
        lap_durations = [lap[2] for lap in self.lap_times]
        lap_numbers = list(range(1, len(lap_durations)+1))
        plt.figure("Lap Chart")
        plt.plot(lap_numbers, lap_durations, marker='o', color='blue')
        plt.title("Grafik Waktu Lap")
        plt.xlabel("Lap ke-")
        plt.ylabel("Durasi Lap (detik)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


    def export_ics(self):
        from tkinter import filedialog, messagebox
        import datetime
        if not self.lap_times:
            messagebox.showinfo("Export ICS", "Tidak ada lap yang dicatat.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar Files", "*.ics"), ("All Files", "*.*")],
            title="Simpan ke Kalender (.ics)"
        )
        if not file_path:
            return
        now = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        ics = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//StopwatchApp//ID//EN"
        ]
        for lap in self.lap_times:
            lap_num, total, lap_time = lap
            ics.append("BEGIN:VEVENT")
            ics.append(f"UID:stopwatch-lap-{lap_num}-{now}")
            ics.append(f"DTSTAMP:{now}")
            ics.append(f"SUMMARY:Lap {lap_num} - {self.format_time(lap_time)}")
            ics.append(f"DESCRIPTION:Total: {self.format_time(total)}")
            ics.append(f"DTSTART:{now}")
            ics.append(f"DTEND:{now}")
            ics.append("END:VEVENT")
        ics.append("END:VCALENDAR")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\r\n".join(ics))
            messagebox.showinfo("Export ICS", f"Lap times berhasil diekspor ke {file_path}\nSilakan impor ke aplikasi kalender Anda.")
        except Exception as e:
            messagebox.showerror("Export ICS", f"Gagal ekspor ICS: {e}")
    def open_new_stopwatch(self):
        StopwatchApp(master=self.window)
    def open_settings(self):
        import tkinter.simpledialog as sd
        import tkinter.colorchooser as cc
        # Font waktu
        font_now = self.time_label.cget("font")
        font_new = sd.askstring("Font", "Masukkan nama font untuk waktu:", initialvalue=font_now)
        if font_new:
            self.time_label.config(font=(font_new, 48, "bold"))
            self.ms_label.config(font=(font_new, 24))
        # Warna jarum detik
        color = cc.askcolor(title="Pilih warna jarum detik", initialcolor=self.canvas.itemcget(self.jarum_detik, "fill"))
        if color and color[1]:
            self.canvas.itemconfig(self.jarum_detik, fill=color[1])
        # Warna latar belakang animasi
        bg_color = cc.askcolor(title="Pilih warna latar belakang animasi", initialcolor=self.canvas.cget("bg"))
        if bg_color and bg_color[1]:
            self.canvas.config(bg=bg_color[1])
    def show_stats(self):
        import tkinter.messagebox as msg
        if not self.lap_times:
            msg.showinfo("Lap Statistics", "Belum ada lap yang dicatat.")
            return
        lap_durations = [lap[2] for lap in self.lap_times]
        fastest = min(lap_durations)
        slowest = max(lap_durations)
        avg = sum(lap_durations) / len(lap_durations)
        msg.showinfo(
            "Lap Statistics",
            f"Lap tercepat : {self.format_time(fastest)}\nLap terlambat : {self.format_time(slowest)}\nRata-rata     : {self.format_time(avg)}\nJumlah lap    : {len(lap_durations)}"
        )
    def toggle_theme(self):
        """Toggle dark/light theme"""
        if self.theme == "dark":
            self.theme = "light"
        else:
            self.theme = "dark"
        self.apply_theme()

    def apply_theme(self):
        """Apply theme to all widgets"""
        if self.theme == "dark":
            bg = "black"
            fg = "white"
            accent = "lime"
            ms_fg = "yellow"
            lap_fg = "lime"
            btn_bg = {"start": "green", "reset": "red", "lap": "blue", "export": "#444", "import": "#444", "theme": "#888"}
        else:
            bg = "#f0f0f0"
            fg = "#222"
            accent = "#007700"
            ms_fg = "#b8860b"
            lap_fg = "#007700"
            btn_bg = {"start": "#4caf50", "reset": "#e53935", "lap": "#1976d2", "export": "#bbb", "import": "#bbb", "theme": "#888"}

        self.window.configure(bg=bg)
        for w in self.window.winfo_children():
            if isinstance(w, tk.Frame) or isinstance(w, tk.LabelFrame):
                w.configure(bg=bg)
        self.time_label.configure(bg=bg, fg=accent)
        self.ms_label.configure(bg=bg, fg=ms_fg)
        self.canvas.configure(bg=bg)
        self.start_stop_btn.configure(bg=btn_bg["start"] if not self.is_running else btn_bg["reset"], fg="white")
        self.reset_btn.configure(bg=btn_bg["reset"], fg="white")
        self.lap_btn.configure(bg=btn_bg["lap"], fg="white")
        self.export_btn.configure(bg=btn_bg["export"], fg="white")
        self.import_btn.configure(bg=btn_bg["import"], fg="white")
        self.theme_btn.configure(bg=btn_bg["theme"], fg="white")
        self.lap_listbox.configure(bg=bg, fg=lap_fg, selectbackground="#ccc" if self.theme=="light" else "gray")
        # Update lap frame label color
        for w in self.window.winfo_children():
            if isinstance(w, tk.LabelFrame):
                w.configure(fg=fg, bg=bg)

    # Panggil apply_theme() setelah interface dibuat
    def buat_interface(self):
        # Frame untuk display waktu
        time_frame = tk.Frame(self.window, bg="black")
        time_frame.pack(pady=20)

        # Label untuk menampilkan waktu
        self.time_label = tk.Label(
            time_frame,
            text="00:00:00",
            font=("Digital-7", 48, "bold"),
            fg="lime",
            bg="black"
        )
        self.time_label.pack()

        # Label untuk milidetik
        self.ms_label = tk.Label(
            time_frame,
            text="000",
            font=("Digital-7", 24),
            fg="yellow",
            bg="black"
        )
        self.ms_label.pack()

        # Canvas untuk animasi
        self.canvas = tk.Canvas(
            self.window,
            width=300,
            height=300,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(pady=20)

        # Gambar lingkaran luar (static)
        self.canvas.create_oval(
            50, 50, 250, 250,
            outline="white",
            width=3,
            tags="outer_circle"
        )

        # Gambar titik-titik penanda waktu
        self.buat_penanda_waktu()

        # Jarum detik (akan beranimasi)
        self.jarum_detik = self.canvas.create_line(
            150, 150, 150, 70,
            fill="red",
            width=3,
            tags="second_hand"
        )

        # Titik tengah
        self.canvas.create_oval(
            145, 145, 155, 155,
            fill="white",
            outline="white"
        )

        # Frame untuk countdown
        countdown_frame = tk.Frame(self.window, bg="black")
        countdown_frame.pack(pady=5)
        tk.Label(countdown_frame, text="Countdown (detik):", font=("Arial", 10), bg="black", fg="white").pack(side=tk.LEFT)
        self.countdown_entry = tk.Entry(countdown_frame, width=8, font=("Arial", 10))
        self.countdown_entry.pack(side=tk.LEFT, padx=5)
        self.set_countdown_btn = tk.Button(countdown_frame, text="SET", font=("Arial", 10), command=self.set_countdown)
        self.set_countdown_btn.pack(side=tk.LEFT)

        # Frame untuk tombol kontrol
        control_frame = tk.Frame(self.window, bg="black")
        control_frame.pack(pady=20)

        # Tombol Start/Stop
        self.start_stop_btn = tk.Button(
            control_frame,
            text="START",
            font=("Arial", 14, "bold"),
            bg="green",
            fg="white",
            width=10,
            command=self.toggle_stopwatch
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Reset
        self.reset_btn = tk.Button(
            control_frame,
            text="RESET",
            font=("Arial", 14, "bold"),
            bg="red",
            fg="white",
            width=10,
            command=self.reset_stopwatch
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Lap
        self.lap_btn = tk.Button(
            control_frame,
            text="LAP",
            font=("Arial", 14, "bold"),
            bg="blue",
            fg="white",
            width=10,
            command=self.record_lap,
            state=tk.DISABLED
        )
        self.lap_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Export
        self.export_btn = tk.Button(
            control_frame,
            text="EXPORT",
            font=("Arial", 12),
            bg="#444",
            fg="white",
            width=8,
            command=self.export_laps
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Import
        self.import_btn = tk.Button(
            control_frame,
            text="IMPORT",
            font=("Arial", 12),
            bg="#444",
            fg="white",
            width=8,
            command=self.import_laps
        )
        self.import_btn.pack(side=tk.LEFT, padx=5)

        # Tombol Theme
        self.theme_btn = tk.Button(
            control_frame,
            text="THEME",
            font=("Arial", 12),
            bg="#888",
            fg="white",
            width=8,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side=tk.LEFT, padx=5)

        # Frame untuk lap times
        lap_frame = tk.LabelFrame(
            self.window,
            text="Lap Times",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="black"
        )
        lap_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Listbox untuk menampilkan lap times
        self.lap_listbox = tk.Listbox(
            lap_frame,
            font=("Courier", 11),
            bg="black",
            fg="lime",
            selectbackground="gray"
        )
        self.lap_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Variabel untuk lap times
        self.lap_times = []
        self.lap_count = 0

        self.apply_theme()

        # Frame untuk lap times
        lap_frame = tk.LabelFrame(
            self.window,
            text="Lap Times",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="black"
        )
        lap_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Listbox untuk menampilkan lap times
        self.lap_listbox = tk.Listbox(
            lap_frame,
            font=("Courier", 11),
            bg="black",
            fg="lime",
            selectbackground="gray"
        )
        self.lap_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Variabel untuk lap times
        self.lap_times = []
        self.lap_count = 0

    def set_countdown(self):
        val = self.countdown_entry.get()
        try:
            seconds = int(val)
            if seconds > 0:
                self.countdown_mode = True
                self.countdown_target = seconds
                self.elapsed_time = 0
                self.reset_stopwatch()
                self.time_label.config(text=self.format_time(seconds))
                self.ms_label.config(text="000")
                self.countdown_alarm_triggered = False
                self.start_stop_btn.config(text="START", bg="green")
                self.lap_btn.config(state=tk.DISABLED)
        except Exception:
            self.countdown_mode = False
            self.countdown_target = 0
            self.countdown_alarm_triggered = False

    def export_laps(self):
        """Export lap times ke file CSV"""
        import csv
        from tkinter import filedialog, messagebox
        if not self.lap_times:
            messagebox.showinfo("Export Lap Times", "Tidak ada lap yang dicatat.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Simpan Lap Times"
        )
        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Lap", "Total Time (s)", "Lap Time (s)"])
                    for lap in self.lap_times:
                        writer.writerow([lap[0], f"{lap[1]:.3f}", f"{lap[2]:.3f}"])
                messagebox.showinfo("Export Lap Times", f"Lap times berhasil disimpan ke {file_path}")
            except Exception as e:
                messagebox.showerror("Export Lap Times", f"Gagal menyimpan file: {e}")

    def import_laps(self):
        """Import lap times dari file CSV"""
        import csv
        from tkinter import filedialog, messagebox
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Buka Lap Times"
        )
        if file_path:
            try:
                with open(file_path, mode="r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    self.lap_times.clear()
                    self.lap_listbox.delete(0, tk.END)
                    self.lap_count = 0
                    for row in reader:
                        if len(row) >= 3:
                            try:
                                lap_num = int(row[0])
                                total = float(row[1])
                                lap = float(row[2])
                                self.lap_times.append((lap_num, total, lap))
                                total_formatted = self.format_time(total)
                                lap_formatted = self.format_time(lap)
                                lap_text = f"Lap {lap_num:2d}: {lap_formatted} (Total: {total_formatted})"
                                self.lap_listbox.insert(tk.END, lap_text)
                                self.lap_count = lap_num
                            except Exception:
                                continue
                messagebox.showinfo("Import Lap Times", f"Lap times berhasil dimuat dari {file_path}")
            except Exception as e:
                messagebox.showerror("Import Lap Times", f"Gagal memuat file: {e}")

    def toggle_stopwatch(self):
        """Toggle start/stop stopwatch"""
        if not self.is_running:
            self.start_stopwatch()
        else:
            self.stop_stopwatch()

    def start_stopwatch(self):
        """Mulai stopwatch"""
        self.is_running = True
        self.start_time = time.time() - self.elapsed_time

        # Update tampilan tombol
        self.start_stop_btn.config(text="STOP", bg="red")
        self.lap_btn.config(state=tk.NORMAL)

        self.play_sound("start")

        # Mulai timer
        self.update_time()

    def stop_stopwatch(self):
        """Stop stopwatch"""
        self.is_running = False

        # Update tampilan tombol
        self.start_stop_btn.config(text="START", bg="green")
        self.lap_btn.config(state=tk.DISABLED)

        self.play_sound("stop")

        # Hentikan timer
        if self.timer_job:
            self.window.after_cancel(self.timer_job)

    def reset_stopwatch(self):
        """Reset stopwatch"""
        self.stop_stopwatch()
        self.elapsed_time = 0

        # Reset tampilan
        self.time_label.config(text="00:00:00")
        self.ms_label.config(text="000")

        # Reset lap times
        self.lap_times.clear()
        self.lap_count = 0
        self.lap_listbox.delete(0, tk.END)

        # Reset jarum detik
        self.update_second_hand(0)
        self.play_sound("reset")

    def record_lap(self):
        """Catat lap time"""
        if self.is_running:
            self.lap_count += 1
            current_time = self.elapsed_time

            # Hitung lap time (selisih dengan lap sebelumnya)
            if self.lap_times:
                lap_time = current_time - self.lap_times[-1][1]
            else:
                lap_time = current_time

            # Simpan lap time
            self.lap_times.append((self.lap_count, current_time, lap_time))

            # Format dan tampilkan
            total_formatted = self.format_time(current_time)
            lap_formatted = self.format_time(lap_time)

            lap_text = f"Lap {self.lap_count:2d}: {lap_formatted} (Total: {total_formatted})"
            self.lap_listbox.insert(tk.END, lap_text)

            # Scroll ke bawah
            self.lap_listbox.see(tk.END)
            self.play_sound("lap")

    def update_time(self):
        """Update tampilan waktu"""
        if self.is_running:
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time

            if self.countdown_mode:
                sisa = max(0, self.countdown_target - self.elapsed_time)
                time_str = self.format_time(sisa)
                ms = int((sisa % 1) * 1000)
                self.time_label.config(text=time_str)
                self.ms_label.config(text=f"{ms:03d}")
                seconds = sisa % 60
                self.update_second_hand(seconds)
                if sisa <= 0 and not self.countdown_alarm_triggered:
                    self.countdown_alarm_triggered = True
                    self.is_running = False
                    self.play_sound("alarm")
                    self.flash_border()
                    self.start_stop_btn.config(text="START", bg="green")
                    self.lap_btn.config(state=tk.DISABLED)
                    return
            else:
                time_str = self.format_time(self.elapsed_time)
                self.time_label.config(text=time_str)
                ms = int((self.elapsed_time % 1) * 1000)
                self.ms_label.config(text=f"{ms:03d}")
                seconds = self.elapsed_time % 60
                self.update_second_hand(seconds)

            self.timer_job = self.window.after(10, self.update_time)

    def format_time(self, seconds):
        """Format waktu ke string HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def update_second_hand(self, seconds):
        """Update posisi jarum detik"""
        # Hitung sudut (0 detik = atas, 15 detik = kanan, dst)
        angle = math.radians(seconds * 6 - 90)  # -90 untuk mulai dari atas

        center_x, center_y = 150, 150
        length = 70

        end_x = center_x + length * math.cos(angle)
        end_y = center_y + length * math.sin(angle)

        # Update koordinat jarum
        self.canvas.coords(
            self.jarum_detik,
            center_x, center_y,
            end_x, end_y
        )

    def start_animation(self):
        """Mulai animasi latar belakang"""
        self.animate_background()

    def animate_background(self):
        """Animasi latar belakang (opsional)"""
        # Rotasi sudut untuk efek visual
        self.rotation_angle = (self.rotation_angle + 1) % 360

        # Update warna border berdasarkan status
        if self.is_running:
            color = f"#{int(127 + 127 * math.sin(math.radians(self.rotation_angle * 4))):02x}0000"
        else:
            color = "white"

        self.canvas.itemconfig("outer_circle", outline=color)

        # Schedule next animation frame
        self.animation_job = self.window.after(50, self.animate_background)

    def jalankan(self):
        """Method untuk menjalankan aplikasi"""
        self.window.mainloop()

# Untuk menjalankan aplikasi
if __name__ == "__main__":
    app = StopwatchApp()
    app.jalankan()