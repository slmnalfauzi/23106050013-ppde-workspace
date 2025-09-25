import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import pandas as pd
from tkinter import filedialog
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import threading
import time

class DataVisualizer:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualizer - Professional Data Visualization Tool")
        self.root.geometry("1200x800")
        self.root.configure(bg="white")

        # Initialize variables
        self.current_data = None
        self.annotations = []
        self.realtime_data = []
        self.max_points = 50

        # Mode selector variable
        self.mode = tk.StringVar(value="fungsi")

        # Setup all components
        self.setup_ui()
        self.setup_mode_selector()  # Add mode selector at the top of control panel
        self.setup_controls()
        self.setup_data_controls()
        self.setup_plot()
        self.setup_export_controls()
        self.setup_interactive_features()
        self.setup_theme_controls()
        self.setup_status_bar()

        # Setup menu and shortcuts
        self.create_menu_bar()
        self.setup_keyboard_shortcuts()

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Show initial controls based on mode
        self.show_mode_controls()
        self.update_status("Ready - Load data or use function generator")

    def setup_mode_selector(self):
        # Add radio button for mode selection at the top of control panel
        mode_frame = tk.Frame(self.control_frame, bg="lightblue")
        mode_frame.pack(pady=(0, 10), fill=tk.X)
        tk.Label(mode_frame, text="Mode Visualisasi:", font=("Arial", 11, "bold"), bg="lightblue").pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Fungsi Matematika", variable=self.mode, value="fungsi", command=self.show_mode_controls, bg="lightblue").pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Data/Real-time", variable=self.mode, value="data", command=self.show_mode_controls, bg="lightblue").pack(anchor="w")

    def show_mode_controls(self):
        # Show/hide controls according to mode
        if self.mode.get() == "fungsi":
            self.controls_frame_data.pack_forget()
            self.controls_frame_fungsi.pack(fill=tk.X, pady=(0, 10))
            self.update_plot()
        else:
            self.controls_frame_fungsi.pack_forget()
            self.controls_frame_data.pack(fill=tk.X, pady=(0, 10))
            if hasattr(self, 'realtime_active') and self.realtime_active.get():
                self.update_realtime_plot()
            else:
                self.plot_data_advanced()
        
    def setup_data_controls(self):
        # Frame khusus untuk kontrol data/real-time
        self.controls_frame_data = tk.Frame(self.control_frame, bg="lightblue")

        separator = tk.Frame(self.controls_frame_data, height=2, bg="darkblue")
        separator.pack(fill=tk.X, pady=20)

        data_label = tk.Label(
            self.controls_frame_data, 
            text="VISUALISASI DATA", 
            font=("Arial", 14, "bold"),
            bg="lightblue"
        )
        data_label.pack(pady=10)

        load_btn = tk.Button(
            self.controls_frame_data,
            text="Load Data CSV",
            font=("Arial", 11, "bold"),
            command=self.load_data,
            bg="orange",
            fg="white",
            width=20
        )
        load_btn.pack(pady=5)

        sample_btn = tk.Button(
            self.controls_frame_data,
            text="Generate Sample Data",
            font=("Arial", 11),
            command=self.generate_sample_data,
            bg="green",
            fg="white",
            width=20
        )
        sample_btn.pack(pady=5)

        self.data_info_label = tk.Label(
            self.controls_frame_data,
            text="Belum ada data dimuat",
            font=("Arial", 9),
            bg="lightblue",
            wraplength=200
        )
        self.data_info_label.pack(pady=10)

        self.current_data = None

        plot_type_label = tk.Label(
            self.controls_frame_data, 
            text="Jenis Plot:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        plot_type_label.pack(pady=(15, 5))

        self.plot_type = tk.StringVar(value="line")
        plot_type_combo = ttk.Combobox(
            self.controls_frame_data,
            textvariable=self.plot_type,
            values=["line", "scatter", "bar", "histogram", "box"],
            state="readonly",
            width=18
        )
        plot_type_combo.pack(pady=5)
        plot_type_combo.bind("<<ComboboxSelected>>", self.on_plot_type_change)

        self.use_subplot = tk.BooleanVar(value=False)
        subplot_check = tk.Checkbutton(
            self.controls_frame_data,
            text="Gunakan Multiple Subplot",
            variable=self.use_subplot,
            command=self.toggle_subplot,
            font=("Arial", 10),
            bg="lightblue"
        )
        subplot_check.pack(pady=10)

        realtime_label = tk.Label(
            self.controls_frame_data, 
            text="Real-time Simulation:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        realtime_label.pack(pady=(20, 5))

        self.realtime_active = tk.BooleanVar(value=False)
        self.realtime_btn = tk.Button(
            self.controls_frame_data,
            text="Start Real-time",
            font=("Arial", 11),
            command=self.toggle_realtime,
            bg="red",
            fg="white",
            width=20
        )
        self.realtime_btn.pack(pady=5)

        speed_label = tk.Label(
            self.controls_frame_data, 
            text="Update Speed (ms):", 
            font=("Arial", 10),
            bg="lightblue"
        )
        speed_label.pack(pady=(10, 2))

        self.update_speed = tk.IntVar(value=500)
        speed_scale = tk.Scale(
            self.controls_frame_data,
            from_=100,
            to=2000,
            resolution=100,
            orient=tk.HORIZONTAL,
            variable=self.update_speed,
            length=180,
            bg="lightblue"
        )
        speed_scale.pack(pady=5)

        self.realtime_data = []
        self.max_points = 50

    def toggle_realtime(self):
        if not self.realtime_active.get():
            # Start real-time
            self.realtime_active.set(True)
            self.realtime_btn.config(text="Stop Real-time", bg="green")
            self.start_realtime_thread()
        else:
            # Stop real-time
            self.realtime_active.set(False)
            self.realtime_btn.config(text="Start Real-time", bg="red")

    def start_realtime_thread(self):
        def update_loop():
            while self.realtime_active.get():
                # Generate new data point
                timestamp = len(self.realtime_data)
                value1 = 50 + 20 * np.sin(timestamp * 0.1) + np.random.normal(0, 5)
                value2 = 30 + 15 * np.cos(timestamp * 0.15) + np.random.normal(0, 3)
                value3 = 40 + 10 * np.sin(timestamp * 0.08) + np.random.normal(0, 4)

                self.realtime_data.append({
                    'timestamp': timestamp,
                    'sensor1': value1,
                    'sensor2': value2,
                    'sensor3': value3
                })

                # Keep only last max_points
                if len(self.realtime_data) > self.max_points:
                    self.realtime_data.pop(0)

                # Update plot in main thread
                self.root.after(0, self.update_realtime_plot)

                # Sleep based on update speed
                time.sleep(self.update_speed.get() / 1000.0)

        # Start thread
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def update_realtime_plot(self):
        if not self.realtime_data:
            return

        # Convert to arrays for plotting
        timestamps = [d['timestamp'] for d in self.realtime_data]
        sensor1 = [d['sensor1'] for d in self.realtime_data]
        sensor2 = [d['sensor2'] for d in self.realtime_data]
        sensor3 = [d['sensor3'] for d in self.realtime_data]

        # Clear and plot
        if hasattr(self, 'ax'):
            self.ax.clear()
            self.ax.plot(timestamps, sensor1, 'b-', label='Sensor 1', linewidth=2)
            self.ax.plot(timestamps, sensor2, 'r-', label='Sensor 2', linewidth=2)
            self.ax.plot(timestamps, sensor3, 'g-', label='Sensor 3', linewidth=2)

            self.ax.set_title('Real-time Sensor Data')
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Value')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)

            # Set axis limits for smooth scrolling effect
            if len(timestamps) > 10:
                self.ax.set_xlim(timestamps[-self.max_points], timestamps[-1])

            self.canvas.draw()

    def toggle_subplot(self):
        if self.current_data is not None:
            self.setup_subplot() if self.use_subplot.get() else self.setup_single_plot()
        else:
            messagebox.showwarning("Peringatan", "Muat data terlebih dahulu!")
            self.use_subplot.set(False)

    def setup_single_plot(self):
        # Reset ke single plot
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.plot_data_advanced()

    def setup_subplot(self):
        if self.current_data is None:
            return

        # Clear figure
        self.fig.clear()

        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns
        n_cols = len(numeric_columns)

        if n_cols < 2:
            messagebox.showinfo("Info", "Minimal 2 kolom numerik diperlukan untuk subplot")
            self.use_subplot.set(False)
            self.setup_single_plot()
            return

        # Tentukan layout subplot
        if n_cols == 2:
            rows, cols = 1, 2
        elif n_cols == 3:
            rows, cols = 2, 2
        elif n_cols == 4:
            rows, cols = 2, 2
        else:
            rows, cols = 2, 3

        # Limit maksimal 6 subplot
        n_plots = min(n_cols, 6)

        # Buat subplot
        for i in range(n_plots):
            ax = self.fig.add_subplot(rows, cols, i+1)
            col = numeric_columns[i]

            # Plot berbagai jenis untuk setiap subplot
            if i % 4 == 0:  # Line plot
                ax.plot(self.current_data[col], color='blue', linewidth=1.5)
                ax.set_title(f'Line: {col}')
            elif i % 4 == 1:  # Histogram
                ax.hist(self.current_data[col].dropna(), bins=20, alpha=0.7, color='green')
                ax.set_title(f'Histogram: {col}')
            elif i % 4 == 2:  # Box plot
                ax.boxplot(self.current_data[col].dropna())
                ax.set_title(f'Box: {col}')
            else:  # Scatter dengan kolom pertama
                if len(numeric_columns) > 1:
                    ax.scatter(self.current_data[numeric_columns[0]], 
                            self.current_data[col], alpha=0.6)
                    ax.set_title(f'Scatter: {col}')

            ax.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

    def on_plot_type_change(self, event=None):
        if self.current_data is not None:
            self.plot_data_advanced()
        else:
            messagebox.showwarning("Peringatan", "Muat data terlebih dahulu!")

    # Remove duplicate/old plot_data_advanced, keep only the improved version at the end of the class

    def load_data(self):
        self.update_status("Loading data...")

        file_path = filedialog.askopenfilename(
            title="Pilih file CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Read CSV
                self.current_data = pd.read_csv(file_path)

                # Update info label
                rows, cols = self.current_data.shape
                self.data_info_label.config(
                    text=f"Data dimuat:\n{rows} baris, {cols} kolom\nFile: {file_path.split('/')[-1]}"
                )

                # Plot data
                self.plot_data()
                self.update_status(f"Data loaded: {rows} rows")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file:\n{str(e)}")
                self.update_status("Failed to load data")

    def generate_sample_data(self):
        # Generate data sample yang menarik
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')

        # Simulasi data penjualan dengan tren dan noise
        trend = np.linspace(100, 200, len(dates))
        seasonal = 30 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
        noise = np.random.normal(0, 15, len(dates))
        sales = trend + seasonal + noise

        # Simulasi data temperature
        temp_base = 25 + 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
        temp_noise = np.random.normal(0, 5, len(dates))
        temperature = temp_base + temp_noise

        # Buat DataFrame
        self.current_data = pd.DataFrame({
            'Date': dates,
            'Sales': sales,
            'Temperature': temperature,
            'Category_A': sales * 0.6 + np.random.normal(0, 10, len(dates)),
            'Category_B': sales * 0.4 + np.random.normal(0, 8, len(dates))
        })

        # Update info label
        rows, cols = self.current_data.shape
        self.data_info_label.config(
            text=f"Sample data dibuat:\n{rows} baris, {cols} kolom\nData penjualan tahunan"
        )

        # Plot data
        self.plot_data()

    def plot_data(self):
        self.plot_data_advanced()

    def setup_controls(self):
        # Frame khusus untuk kontrol fungsi matematika
        self.controls_frame_fungsi = tk.Frame(self.control_frame, bg="lightblue")

        self.frequency = tk.DoubleVar(value=1.0)
        self.amplitude = tk.DoubleVar(value=1.0)
        self.phase = tk.DoubleVar(value=0.0)

        freq_label = tk.Label(
            self.controls_frame_fungsi,
            text="Frekuensi:",
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        freq_label.pack(pady=(10, 2))

        self.freq_scale = tk.Scale(
            self.controls_frame_fungsi,
            from_=0.1,
            to=5.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.frequency,
            command=self.on_parameter_change,
            length=200,
            bg="lightblue"
        )
        self.freq_scale.pack(pady=5)

        self.freq_value_label = tk.Label(
            self.controls_frame_fungsi,
            text=f"Nilai: {self.frequency.get()}",
            font=("Arial", 10),
            bg="lightblue"
        )
        self.freq_value_label.pack()

        self.amp_label = tk.Label(
            self.controls_frame_fungsi, 
            text="Amplitudo:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        self.amp_label.pack(pady=(20, 5))

        self.amp_scale = tk.Scale(
            self.controls_frame_fungsi,
            from_=0.1,
            to=3.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.amplitude,
            command=self.on_parameter_change,
            length=200,
            bg="lightblue"
        )
        self.amp_scale.pack(pady=5)

        self.amp_value_label = tk.Label(
            self.controls_frame_fungsi,
            text=f"Nilai: {self.amplitude.get()}",
            font=("Arial", 10),
            bg="lightblue"
        )
        self.amp_value_label.pack()

        self.phase_label = tk.Label(
            self.controls_frame_fungsi, 
            text="Phase:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        self.phase_label.pack(pady=(20, 5))

        self.phase_scale = tk.Scale(
            self.controls_frame_fungsi,
            from_=0.0,
            to=6.28,  # 2π
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.phase,
            command=self.on_parameter_change,
            length=200,
            bg="lightblue"
        )
        self.phase_scale.pack(pady=5)

        self.phase_value_label = tk.Label(
            self.controls_frame_fungsi,
            text=f"Nilai: {self.phase.get()}",
            font=("Arial", 10),
            bg="lightblue"
        )
        self.phase_value_label.pack()

        func_label = tk.Label(
            self.controls_frame_fungsi, 
            text="Jenis Fungsi:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        func_label.pack(pady=(30, 5))

        self.function_type = tk.StringVar(value="sin")
        function_combo = ttk.Combobox(
            self.controls_frame_fungsi,
            textvariable=self.function_type,
            values=["sin", "cos", "tan", "exp", "log"],
            state="readonly",
            width=18
        )
        function_combo.pack(pady=5)
        function_combo.bind("<<ComboboxSelected>>", self.on_function_change)

        color_label = tk.Label(
            self.controls_frame_fungsi, 
            text="Warna Garis:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        color_label.pack(pady=(20, 5))

        self.line_color = tk.StringVar(value="blue")
        color_combo = ttk.Combobox(
            self.controls_frame_fungsi,
            textvariable=self.line_color,
            values=["blue", "red", "green", "orange", "purple", "brown", "pink"],
            state="readonly",
            width=18
        )
        color_combo.pack(pady=5)
        color_combo.bind("<<ComboboxSelected>>", self.on_style_change)

        style_label = tk.Label(
            self.controls_frame_fungsi, 
            text="Style Garis:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        style_label.pack(pady=(15, 5))

        self.line_style = tk.StringVar(value="-")
        style_combo = ttk.Combobox(
            self.controls_frame_fungsi,
            textvariable=self.line_style,
            values=["-", "--", "-.", ":", "o-", "s-", "^-"],
            state="readonly",
            width=18
        )
        style_combo.pack(pady=5)
        style_combo.bind("<<ComboboxSelected>>", self.on_style_change)

        width_label = tk.Label(
            self.controls_frame_fungsi, 
            text="Ketebalan Garis:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        width_label.pack(pady=(15, 5))

        self.line_width = tk.DoubleVar(value=2.0)
        width_scale = tk.Scale(
            self.controls_frame_fungsi,
            from_=0.5,
            to=5.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            variable=self.line_width,
            command=self.on_style_change,
            length=200,
            bg="lightblue"
        )
        width_scale.pack(pady=5)

    def on_style_change(self, value=None):
        self.update_plot()

    def on_function_change(self, event=None):
        self.update_plot()

    def on_parameter_change(self, value=None):
        # Update label nilai
        self.freq_value_label.config(text=f"Nilai: {self.frequency.get():.1f}")
        self.amp_value_label.config(text=f"Nilai: {self.amplitude.get():.1f}")
        self.phase_value_label.config(text=f"Nilai: {self.phase.get():.2f}")

        # Update plot
        self.update_plot()

    def setup_ui(self):
        # Frame utama
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame untuk kontrol (kiri)
        self.control_frame = tk.Frame(main_frame, bg="lightblue", width=250)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.control_frame.pack_propagate(False)  # Maintain fixed width

        # Frame untuk plot (kanan)
        self.plot_frame = tk.Frame(main_frame, bg="white")
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Judul di control frame
        title_label = tk.Label(
            self.control_frame, 
            text="KONTROL VISUALISASI", 
            font=("Arial", 14, "bold"),
            bg="lightblue"
        )
        title_label.pack(pady=20)
    
    def setup_plot(self):
        # Membuat Figure matplotlib
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # Embed plot ke dalam Tkinter (pastikan canvas ada sebelum update_plot)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Toolbar navigasi
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()

        # Plot awal setelah canvas dan toolbar siap
        self.update_plot()

    def update_plot(self):
        # Hanya update plot jika mode fungsi
        if self.mode.get() != "fungsi":
            return
        self.ax.clear()
        x = np.linspace(0, 10, 100)
        freq = self.frequency.get()
        amp = self.amplitude.get()
        phase = self.phase.get()
        func_type = self.function_type.get()
        color = self.line_color.get()
        style = self.line_style.get()
        width = self.line_width.get()
        try:
            if func_type == "sin":
                y = amp * np.sin(freq * x + phase)
                title = f"y = {amp} × sin({freq}x + {round(phase, 2)})"
            elif func_type == "cos":
                y = amp * np.cos(freq * x + phase)
                title = f"y = {amp} × cos({freq}x + {round(phase, 2)})"
            elif func_type == "tan":
                y = amp * np.tan(freq * x + phase)
                y = np.clip(y, -10, 10)
                title = f"y = {amp} × tan({freq}x + {round(phase, 2)})"
            elif func_type == "exp":
                y = amp * np.exp(freq * (x -5) + phase)
                y = np.clip(y, 0, 100)
                title = f"y = {amp} × exp({freq}(x-5) + {round(phase, 2)})"
            elif func_type == "log":
                y = amp * np.log(freq * (x + 1) + phase)
                title = f"y = {amp} × log({freq}(x+1) + {round(phase, 2)})"
        except:
            y = amp * np.sin(freq * x + phase)
            title = f"y = {amp} × sin({freq}x + {round(phase, 2)})"
        self.ax.plot(x, y, linestyle=style, color=color, linewidth=width)
        self.ax.set_title(title, fontsize=16)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()

    def setup_export_controls(self):
        # Separator
        export_separator = tk.Frame(self.control_frame, height=2, bg="darkblue")
        export_separator.pack(fill=tk.X, pady=20)

        # Export section label
        export_label = tk.Label(
            self.control_frame, 
            text="EXPORT & SAVE", 
            font=("Arial", 14, "bold"),
            bg="lightblue"
        )
        export_label.pack(pady=10)

        # Save plot button
        save_btn = tk.Button(
            self.control_frame,
            text="Save Plot",
            font=("Arial", 11, "bold"),
            command=self.save_plot,
            bg="purple",
            fg="white",
            width=20
        )
        save_btn.pack(pady=5)

        # Export format
        format_label = tk.Label(
            self.control_frame, 
            text="Format:", 
            font=("Arial", 10),
            bg="lightblue"
        )
        format_label.pack(pady=(10, 2))

        self.export_format = tk.StringVar(value="png")
        format_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.export_format,
            values=["png", "jpg", "pdf", "svg", "eps"],
            state="readonly",
            width=18
        )
        format_combo.pack(pady=5)

        # DPI setting
        dpi_label = tk.Label(
            self.control_frame, 
            text="Resolusi (DPI):", 
            font=("Arial", 10),
            bg="lightblue"
        )
        dpi_label.pack(pady=(10, 2))

        self.dpi_setting = tk.IntVar(value=300)
        dpi_scale = tk.Scale(
            self.control_frame,
            from_=100,
            to=600,
            resolution=50,
            orient=tk.HORIZONTAL,
            variable=self.dpi_setting,
            length=180,
            bg="lightblue"
        )
        dpi_scale.pack(pady=5)

    def save_plot(self):
        format_ext = self.export_format.get()
        dpi = self.dpi_setting.get()

        # File dialog untuk save
        file_path = filedialog.asksaveasfilename(
            title="Simpan Plot",
            defaultextension=f".{format_ext}",
            filetypes=[
                (f"{format_ext.upper()} files", f"*.{format_ext}"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                # Simpan dengan DPI yang dipilih
                self.fig.savefig(
                    file_path, 
                    dpi=dpi, 
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                messagebox.showinfo(
                    "Berhasil", 
                    f"Plot berhasil disimpan ke:\n{file_path}\nResolusi: {dpi} DPI"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan plot:\n{str(e)}")

        # Export data button
        export_data_btn = tk.Button(
            self.control_frame,
            text="Export Data CSV",
            font=("Arial", 11),
            command=self.export_data_csv,
            bg="brown",
            fg="white",
            width=20
        )
        export_data_btn.pack(pady=5)

    def export_data_csv(self):
        if self.current_data is None:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diekspor!")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Data ke CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.current_data.to_csv(file_path, index=False)
                messagebox.showinfo(
                    "Berhasil", 
                    f"Data berhasil diekspor ke:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Gagal mengekspor data:\n{str(e)}")

    def setup_interactive_features(self):
        # Enable interactive mode
        self.annotations = []
        self.interactive_mode = tk.BooleanVar(value=False)

        # Interactive checkbox
        interactive_check = tk.Checkbutton(
            self.control_frame,
            text="Mode Interaktif (Click to Annotate)",
            variable=self.interactive_mode,
            command=self.toggle_interactive,
            font=("Arial", 10),
            bg="lightblue",
            wraplength=200
        )
        interactive_check.pack(pady=10)

        # Clear annotations button
        clear_btn = tk.Button(
            self.control_frame,
            text="Clear Annotations",
            font=("Arial", 10),
            command=self.clear_annotations,
            bg="gray",
            fg="white",
            width=20
        )
        clear_btn.pack(pady=5)

    def toggle_interactive(self):
        if self.interactive_mode.get():
            # Connect click event
            self.click_cid = self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        else:
            # Disconnect click event
            if hasattr(self, 'click_cid'):
                self.canvas.mpl_disconnect(self.click_cid)

    def on_plot_click(self, event):
        if not self.interactive_mode.get() or event.inaxes != self.ax:
            return

        # Get click coordinates
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        # Create annotation
        annotation_text = f'({x:.2f}, {y:.2f})'
        annotation = self.ax.annotate(
            annotation_text,
            xy=(x, y),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
        )

        # Store annotation for later removal
        self.annotations.append(annotation)

        # Redraw canvas
        self.canvas.draw()

    def clear_annotations(self):
        # Remove all annotations
        for annotation in self.annotations:
            annotation.remove()
        self.annotations = []
        self.canvas.draw()

    def setup_theme_controls(self):
        # Theme section
        theme_label = tk.Label(
            self.control_frame, 
            text="TEMA & STYLE", 
            font=("Arial", 14, "bold"),
            bg="lightblue"
        )
        theme_label.pack(pady=(20, 10))

        # Plot style
        style_label = tk.Label(
            self.control_frame, 
            text="Plot Style:", 
            font=("Arial", 10),
            bg="lightblue"
        )
        style_label.pack(pady=(5, 2))

        self.plot_style = tk.StringVar(value="default")
        style_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.plot_style,
            values=["default", "ggplot", "seaborn", "classic", "dark_background"],
            state="readonly",
            width=18
        )
        style_combo.pack(pady=5)
        style_combo.bind("<<ComboboxSelected>>", self.on_style_change)

        # Color scheme
        color_scheme_label = tk.Label(
            self.control_frame, 
            text="Color Scheme:", 
            font=("Arial", 10),
            bg="lightblue"
        )
        color_scheme_label.pack(pady=(10, 2))

        self.color_scheme = tk.StringVar(value="default")
        color_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.color_scheme,
            values=["default", "viridis", "plasma", "inferno", "cool", "warm"],
            state="readonly",
            width=18
        )
        color_combo.pack(pady=5)
        color_combo.bind("<<ComboboxSelected>>", self.on_color_scheme_change)

        # Grid style
        self.show_grid = tk.BooleanVar(value=True)
        grid_check = tk.Checkbutton(
            self.control_frame,
            text="Show Grid",
            variable=self.show_grid,
            command=self.update_grid,
            font=("Arial", 10),
            bg="lightblue"
        )
        grid_check.pack(pady=5)

    def on_style_change(self, event=None):
        style = self.plot_style.get()
        try:
            plt.style.use(style)
            # Replot to apply new style
            if hasattr(self, 'current_data') and self.current_data is not None:
                self.plot_data_advanced()
            else:
                self.update_plot()
        except:
            messagebox.showerror("Error", f"Style '{style}' tidak tersedia")
            self.plot_style.set("default")
            plt.style.use("default")

    def on_color_scheme_change(self, event=None):
        # This will be applied in next plot update
        if hasattr(self, 'current_data') and self.current_data is not None:
            self.plot_data_advanced()
        else:
            self.update_plot()

    def update_grid(self):
        if hasattr(self, 'ax'):
            self.ax.grid(self.show_grid.get(), alpha=0.3)
            self.canvas.draw()

    # Update plot methods to use color scheme
    def get_colors(self, n_colors):
        scheme = self.color_scheme.get()
        if scheme == "default":
            return ['blue', 'red', 'green', 'orange', 'purple', 'brown'][:n_colors]
        else:
            try:
                cmap = plt.cm.get_cmap(scheme)
                return [cmap(i / max(1, n_colors - 1)) for i in range(n_colors)]
            except:
                return ['blue', 'red', 'green', 'orange', 'purple', 'brown'][:n_colors]
            
    def setup_status_bar(self):
        # Status bar at bottom
        self.status_bar = tk.Frame(self.root, bg="gray", height=30)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        # Status label
        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            bg="gray",
            fg="white",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Performance info
        self.perf_label = tk.Label(
            self.status_bar,
            text="",
            bg="gray",
            fg="white",
            font=("Arial", 10)
        )
        self.perf_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def update_performance_info(self, start_time):
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to ms
        self.perf_label.config(text=f"Render time: {duration:.1f}ms")

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Data CSV", command=self.load_data, accelerator="Ctrl+O")
        file_menu.add_command(label="Generate Sample", command=self.generate_sample_data, accelerator="Ctrl+G")
        file_menu.add_separator()
        file_menu.add_command(label="Save Plot", command=self.save_plot, accelerator="Ctrl+S")
        file_menu.add_command(label="Export Data", command=self.export_data_csv, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Grid", variable=self.show_grid, command=self.update_grid)
        view_menu.add_checkbutton(label="Interactive Mode", variable=self.interactive_mode, command=self.toggle_interactive)
        view_menu.add_checkbutton(label="Multiple Subplot", variable=self.use_subplot, command=self.toggle_subplot)
        view_menu.add_separator()
        view_menu.add_command(label="Clear Annotations", command=self.clear_annotations)
        view_menu.add_command(label="Reset View", command=self.reset_view)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_checkbutton(label="Real-time Mode", variable=self.realtime_active, command=self.toggle_realtime)
        tools_menu.add_separator()
        tools_menu.add_command(label="Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Data Info", command=self.show_data_info)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_keyboard_shortcuts(self):
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_data())
        self.root.bind('<Control-g>', lambda e: self.generate_sample_data())
        self.root.bind('<Control-s>', lambda e: self.save_plot())
        self.root.bind('<Control-e>', lambda e: self.export_data_csv())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F5>', lambda e: self.refresh_plot())
        self.root.bind('<Escape>', lambda e: self.clear_annotations())

    def reset_view(self):
        if hasattr(self, 'ax'):
            self.ax.relim()
            self.ax.autoscale()
            self.canvas.draw()

    def refresh_plot(self):
        if hasattr(self, 'current_data') and self.current_data is not None:
            self.plot_data_advanced()
        else:
            self.update_plot()

    def show_statistics(self):
        if self.current_data is None:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk ditampilkan statistiknya!")
            return

        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) == 0:
            messagebox.showinfo("Info", "Tidak ada kolom numerik dalam data!")
            return

        # Create statistics window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistik Data")
        stats_window.geometry("600x400")
        stats_window.configure(bg="white")

        # Text widget with scrollbar
        text_frame = tk.Frame(stats_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        stats_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = tk.Scrollbar(text_frame)

        stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        stats_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=stats_text.yview)

        # Generate statistics
        stats_info = "STATISTIK DATA\n" + "="*50 + "\n\n"
        stats_info += f"Jumlah baris: {len(self.current_data)}\n"
        stats_info += f"Jumlah kolom: {len(self.current_data.columns)}\n\n"

        for col in numeric_columns:
            stats_info += f"KOLOM: {col}\n" + "-"*30 + "\n"
            data_col = self.current_data[col].dropna()
            stats_info += f"Count: {len(data_col)}\n"
            stats_info += f"Mean: {data_col.mean():.4f}\n"
            stats_info += f"Std: {data_col.std():.4f}\n"
            stats_info += f"Min: {data_col.min():.4f}\n"
            stats_info += f"25%: {data_col.quantile(0.25):.4f}\n"
            stats_info += f"50%: {data_col.median():.4f}\n"
            stats_info += f"75%: {data_col.quantile(0.75):.4f}\n"
            stats_info += f"Max: {data_col.max():.4f}\n\n"

        stats_text.insert(tk.END, stats_info)
        stats_text.config(state=tk.DISABLED)

    def show_data_info(self):
        if self.current_data is None:
            messagebox.showwarning("Peringatan", "Tidak ada data yang dimuat!")
            return

        rows, cols = self.current_data.shape
        numeric_cols = len(self.current_data.select_dtypes(include=[np.number]).columns)
        text_cols = len(self.current_data.select_dtypes(include=['object']).columns)

        info = f"""INFORMASI DATA:

    Dimensi: {rows} baris × {cols} kolom
    Kolom numerik: {numeric_cols}
    Kolom teks: {text_cols}

    KOLOM YANG TERSEDIA:
    {', '.join(self.current_data.columns.tolist())}

    SAMPLE DATA (5 baris pertama):
    {self.current_data.head().to_string()}"""

        messagebox.showinfo("Informasi Data", info)

    def show_shortcuts(self):
        shortcuts = """KEYBOARD SHORTCUTS:

    Ctrl+O - Load Data CSV
    Ctrl+G - Generate Sample Data
    Ctrl+S - Save Plot
    Ctrl+E - Export Data CSV
    Ctrl+Q - Exit Application
    F5 - Refresh Plot
    Esc - Clear Annotations

    MOUSE INTERACTION:
    - Click pada plot (saat Interactive Mode aktif) untuk menambah annotation
    - Gunakan toolbar untuk zoom, pan, dan navigasi plot"""

        messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    def show_about(self):
        about_text = """DATA VISUALIZER v1.0

    Aplikasi visualisasi data interaktif yang dibuat dengan:
    - Python 3.x
    - Tkinter (GUI Framework)
    - Matplotlib (Plotting Library)
    - NumPy & Pandas (Data Processing)

    Fitur Utama:
    ✓ Visualisasi fungsi matematika real-time
    ✓ Import dan visualisasi data CSV
    ✓ Multiple plot types (line, scatter, bar, histogram, box)
    ✓ Real-time data simulation
    ✓ Interactive annotations
    ✓ Export plot dalam berbagai format
    ✓ Multiple themes dan color schemes

    Developed for educational purposes."""

        messagebox.showinfo("About Data Visualizer", about_text)

    def on_closing(self):
        if self.realtime_active.get():
            self.realtime_active.set(False)

        if messagebox.askokcancel("Exit", "Apakah Anda yakin ingin keluar?"):
            self.root.destroy()

    def safe_execute(self, func, error_message="An error occurred"):
        """Wrapper untuk menjalankan fungsi dengan error handling yang baik"""
        try:
            return func()
        except Exception as e:
            error_details = f"{error_message}\n\nTechnical details:\n{str(e)}"
            messagebox.showerror("Error", error_details)
            self.update_status(f"Error: {error_message}")
            return None

    def validate_data_requirements(self, min_numeric_cols=1):
        """Validasi apakah data memenuhi requirements minimum"""
        if self.current_data is None:
            messagebox.showwarning("Data Required", "Please load or generate data first!")
            return False

        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) < min_numeric_cols:
            messagebox.showwarning(
                "Insufficient Data", 
                f"At least {min_numeric_cols} numeric column(s) required!"
            )
            return False

        return True

    # Update method plot_data_advanced dengan error handling:
    def plot_data_advanced(self):
        if not self.validate_data_requirements():
            return

        def _plot():
            start_time = time.time()
            self.update_status("Plotting data...")

            # Clear plot
            self.ax.clear()

            numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns
            date_columns = self.current_data.select_dtypes(include=['datetime64']).columns

            plot_type = self.plot_type.get()
            colors = self.get_colors(len(numeric_columns))

            if plot_type == "line":
                if len(date_columns) > 0 and len(numeric_columns) > 0:
                    date_col = date_columns[0]
                    for i, col in enumerate(numeric_columns[:3]):
                        self.ax.plot(
                            self.current_data[date_col], 
                            self.current_data[col], 
                            color=colors[i % len(colors)],
                            label=col,
                            linewidth=2
                        )
                    self.ax.set_xlabel('Tanggal')
                    self.ax.legend()
                elif len(numeric_columns) >= 1:
                    col = numeric_columns[0]
                    self.ax.plot(self.current_data[col], color=colors[0], linewidth=2)
                    self.ax.set_xlabel('Index')
                    self.ax.set_ylabel(col)

            elif plot_type == "scatter":
                if len(numeric_columns) >= 2:
                    x_col, y_col = numeric_columns[0], numeric_columns[1]
                    self.ax.scatter(
                        self.current_data[x_col], 
                        self.current_data[y_col],
                        alpha=0.6,
                        s=50,
                        c=colors[0]
                    )
                    self.ax.set_xlabel(x_col)
                    self.ax.set_ylabel(y_col)

            elif plot_type == "bar":
                if len(numeric_columns) >= 1:
                    col = numeric_columns[0]
                    data_sample = self.current_data[col].head(20)
                    self.ax.bar(range(len(data_sample)), data_sample, color=colors[0])
                    self.ax.set_xlabel('Index')
                    self.ax.set_ylabel(col)

            elif plot_type == "histogram":
                if len(numeric_columns) >= 1:
                    col = numeric_columns[0]
                    self.ax.hist(
                        self.current_data[col].dropna(), 
                        bins=30, 
                        alpha=0.7, 
                        color=colors[0],
                        edgecolor='black'
                    )
                    self.ax.set_xlabel(col)
                    self.ax.set_ylabel('Frekuensi')

            elif plot_type == "box":
                if len(numeric_columns) >= 1:
                    data_to_plot = [self.current_data[col].dropna() for col in numeric_columns[:5]]
                    labels = numeric_columns[:5].tolist()
                    bp = self.ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
                    for patch, color in zip(bp['boxes'], colors):
                        patch.set_facecolor(color)
                    self.ax.set_ylabel('Nilai')
                    plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)

            self.ax.set_title(f'{plot_type.title()} Plot')
            if self.show_grid.get():
                self.ax.grid(True, alpha=0.3)

            self.fig.tight_layout()
            self.canvas.draw()

            self.update_performance_info(start_time)
            self.update_status("Plot ready")

        self.safe_execute(_plot, "Failed to plot data")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualizer(root)
    root.mainloop()