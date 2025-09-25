        # Real-time data simulation
        realtime_label = tk.Label(
            self.control_frame, 
            text="Real-time Simulation:", 
            font=("Arial", 12, "bold"),
            bg="lightblue"
        )
        realtime_label.pack(pady=(20, 5))

        self.realtime_active = tk.BooleanVar(value=False)
        self.realtime_btn = tk.Button(
            self.control_frame,
            text="Start Real-time",
            font=("Arial", 11),
            command=self.toggle_realtime,
            bg="red",
            fg="white",
            width=20
        )
        self.realtime_btn.pack(pady=5)

        # Kecepatan update
        speed_label = tk.Label(
            self.control_frame, 
            text="Update Speed (ms):", 
            font=("Arial", 10),
            bg="lightblue"
        )
        speed_label.pack(pady=(10, 2))

        self.update_speed = tk.IntVar(value=500)
        speed_scale = tk.Scale(
            self.control_frame,
            from_=100,
            to=2000,
            resolution=100,
            orient=tk.HORIZONTAL,
            variable=self.update_speed,
            length=180,
            bg="lightblue"
        )
        speed_scale.pack(pady=5)

        # Initialize real-time data
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