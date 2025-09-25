import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog, simpledialog

class PaintApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Paint App - Event Handling Demo")
        self.window.geometry("800x600")

        # Variabel untuk painting
        self.last_x = None
        self.last_y = None
        self.pen_color = "black"
        self.pen_size = 2
        self.is_drawing = False
        # Riwayat untuk undo/redo & mode
        self.current_stroke = []  # daftar item id pada satu goresan
        self.history = []         # tumpukan goresan untuk undo
        self.redo_stack = []      # tumpukan untuk redo
        self.eraser_mode = False  # mode penghapus
        self.background_color = "white"
        # Tool & state tambahan
        self.current_tool = 'pen'
        self.temp_item = None
        self.polygon_points = []
        self.polygon_preview_line = None

        self.buat_interface()
        self.bind_events()

    def buat_interface(self):
        # Frame untuk toolbar
        toolbar = tk.Frame(self.window, bg="lightgray", height=50)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)

        # Canvas untuk menggambar
        self.canvas = tk.Canvas(
            self.window,
            bg="white",
            cursor="pencil"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # sinkronkan warna background canvas
        self.background_color = "white"

        # Pilih alat (tool)
        tk.Label(toolbar, text="Tool:", bg="lightgray").pack(side=tk.LEFT, padx=(8, 4))
        tools = ['pen', 'eraser', 'line', 'rect', 'oval', 'polygon', 'text', 'cube', 'cylinder', 'pyramid']
        self.tool_var = tk.StringVar(value=self.current_tool)
        tool_menu = tk.OptionMenu(toolbar, self.tool_var, *tools, command=lambda v: self.set_tool(v))
        tool_menu.config(bg="white")
        tool_menu.pack(side=tk.LEFT, padx=4)

        # Tombol pilih warna pena
        btn_color = tk.Button(
            toolbar,
            text="Pilih Warna",
            command=self.pilih_warna,
            bg="lightblue"
        )
        btn_color.pack(side=tk.LEFT, padx=5, pady=5)

        # Tombol ganti background
        btn_bg = tk.Button(
            toolbar,
            text="BG Color",
            command=self.change_background,
            bg="lightyellow"
        )
        btn_bg.pack(side=tk.LEFT, padx=5, pady=5)

        # Label dan slider untuk ukuran pen
        tk.Label(toolbar, text="Ukuran:", bg="lightgray").pack(side=tk.LEFT, padx=5)

        self.size_var = tk.IntVar(value=self.pen_size)
        size_scale = tk.Scale(
            toolbar,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.size_var,
            command=self.ubah_ukuran
        )
        size_scale.pack(side=tk.LEFT, padx=5)

        # Tombol clear
        btn_clear = tk.Button(
            toolbar,
            text="Clear",
            command=self.clear_canvas,
            bg="red",
            fg="white"
        )
        btn_clear.pack(side=tk.LEFT, padx=5, pady=5)

        # Label info
        self.info_label = tk.Label(
            toolbar,
            text=f"Mode: Pen | Warna: {self.pen_color} | Ukuran: {self.pen_size}",
            bg="lightgray"
        )
        self.info_label.pack(side=tk.RIGHT, padx=10)

    def set_tool(self, tool):
        self.current_tool = tool
        self.eraser_mode = (tool == 'eraser')
        # Ubah kursor sesuai tool
        cursor = 'tcross' if self.eraser_mode else ('xterm' if tool == 'text' else 'pencil')
        self.canvas.config(cursor=cursor)
        self.update_info()

    def pilih_warna(self):
        """Event handler untuk memilih warna"""
        color = colorchooser.askcolor(title="Pilih Warna Pen")
        if color[1]:  # Jika user tidak cancel
            self.pen_color = color[1]
            self.update_info()

    def change_background(self):
        """Ganti warna background canvas dan sesuaikan eraser"""
        color = colorchooser.askcolor(title="Pilih Warna Background")
        if color[1]:
            old_bg = self.background_color
            new_bg = color[1]
            self.canvas.configure(bg=new_bg)
            self.background_color = new_bg
            # Recolor goresan penghapus lama (yang berwarna old_bg) ke new_bg
            try:
                for item in self.canvas.find_all():
                    # beberapa item (line, polygon, oval, dll) memiliki properti 'fill'
                    try:
                        fill = self.canvas.itemcget(item, 'fill')
                        if fill == old_bg:
                            self.canvas.itemconfigure(item, fill=new_bg)
                    except tk.TclError:
                        pass
            except tk.TclError:
                pass
            self.update_info()

    def ubah_ukuran(self, value):
        """Event handler untuk mengubah ukuran pen"""
        self.pen_size = int(float(value))
        self.update_info()

    def clear_canvas(self, event=None):
        """Event handler untuk membersihkan canvas"""
        if messagebox.askyesno("Konfirmasi", "Hapus semua gambar?"):
            self.canvas.delete("all")
            # reset riwayat
            self.history.clear()
            self.redo_stack.clear()

    def update_info(self):
        """Method untuk update info di toolbar"""
        mode = self.current_tool.capitalize()
        self.info_label.config(
            text=f"Tool: {mode} | Warna: {self.pen_color} | Ukuran: {self.pen_size}"
        )

    def bind_events(self):
        """Method untuk binding semua events"""
        # Mouse events untuk menggambar
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<Double-Button-1>", self.finish_polygon)

        # Mouse events untuk info posisi
        self.canvas.bind("<Motion>", self.show_position)

        # Keyboard events
        self.window.bind("<Control-s>", self.save_image)
        self.window.bind("<Control-o>", self.open_image)
        self.window.bind("<Control-n>", self.new_canvas)
        # Undo/Redo dan lainnya
        self.window.bind("<Control-z>", self.undo)
        self.window.bind("<Control-y>", self.redo)
        self.window.bind("<Control-Shift-Z>", self.redo)
        self.window.bind("<Control-Shift-z>", self.redo)
        # Clear canvas via shortcut
        self.window.bind("<Control-Shift-C>", self.clear_canvas)
        # Toggle eraser (E) dan ubah ukuran ([ dan ])
        self.window.bind("<e>", self.toggle_eraser)
        self.window.bind("<E>", self.toggle_eraser)
        self.window.bind("<bracketright>", lambda e: self.adjust_size(1))
        self.window.bind("<bracketleft>", lambda e: self.adjust_size(-1))

        # Window events
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_draw(self, event):
        """Event handler saat mulai menggambar (mouse press)"""
        self.last_x = event.x
        self.last_y = event.y
        self.is_drawing = True
        # mulai goresan baru
        self.current_stroke = []

        if self.current_tool == 'text':
            # Masukkan teks dan buat item
            text = simpledialog.askstring("Tambah Teks", "Masukkan teks:", parent=self.window)
            if text:
                item = self.canvas.create_text(event.x, event.y, text=text, fill=self.pen_color, anchor='nw', font=("Arial", max(8, self.pen_size + 6)))
                self.current_stroke = [item]
                self.history.append(self.current_stroke)
                self.redo_stack.clear()
            self.is_drawing = False
            return

        if self.current_tool == 'polygon':
            # Tambah titik ke polygon
            self.polygon_points.append((event.x, event.y))
            # Tampilkan pratinjau segmen terakhir ke posisi mouse (handled in draw)
            # Tambahkan penanda kecil
            r = 2
            dot = self.canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill=self.pen_color, outline='')
            self.current_stroke.append(dot)
            # Tidak finalize di sini
            return

        # Untuk alat drag-based (pen/eraser/line/rect/oval/cube/cylinder/pyramid)
        self.temp_item = None

    def draw(self, event):
        """Event handler saat menggambar (mouse drag)"""
        if not self.is_drawing:
            # Untuk polygon, update pratinjau garis ke kursor
            if self.current_tool == 'polygon' and self.polygon_points:
                if self.polygon_preview_line is not None:
                    try:
                        self.canvas.delete(self.polygon_preview_line)
                    except tk.TclError:
                        pass
                x0, y0 = self.polygon_points[-1]
                self.polygon_preview_line = self.canvas.create_line(x0, y0, event.x, event.y, dash=(3, 3), fill=self.pen_color)
            return

        # Freehand pen/eraser
        if self.current_tool in ('pen', 'eraser'):
            if self.last_x is not None and self.last_y is not None:
                color = self.background_color if self.eraser_mode else self.pen_color
                width = self.pen_size * (2 if self.eraser_mode else 1)
                item_id = self.canvas.create_line(
                    self.last_x, self.last_y,
                    event.x, event.y,
                    width=width,
                    fill=color,
                    capstyle=tk.ROUND,
                    smooth=tk.TRUE
                )
                self.current_stroke.append(item_id)
                self.last_x = event.x
                self.last_y = event.y
            return

        # Shape preview for drag-based tools
        if self.temp_item is not None:
            try:
                self.canvas.delete(self.temp_item)
            except tk.TclError:
                pass
            self.temp_item = None

        x1, y1, x2, y2 = self.last_x, self.last_y, event.x, event.y
        outline = self.pen_color
        width = self.pen_size

        if self.current_tool == 'line':
            self.temp_item = self.canvas.create_line(x1, y1, x2, y2, fill=outline, width=width, dash=(3, 3))
        elif self.current_tool == 'rect':
            self.temp_item = self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline, width=width, dash=(3, 3))
        elif self.current_tool == 'oval':
            self.temp_item = self.canvas.create_oval(x1, y1, x2, y2, outline=outline, width=width, dash=(3, 3))
        elif self.current_tool in ('cube', 'cylinder', 'pyramid'):
            # pratinjau sederhana: gunakan rectangle sebagai placeholder
            self.temp_item = self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline, width=width, dash=(3, 3))

    def stop_draw(self, event):
        """Event handler saat berhenti menggambar (mouse release)"""
        if self.current_tool == 'polygon':
            # polygon diselesaikan via double click
            self.is_drawing = False
            return

        if not self.is_drawing:
            return

        self.is_drawing = False

        # finalize pen/eraser
        if self.current_tool in ('pen', 'eraser'):
            if self.current_stroke:
                self.history.append(self.current_stroke)
                self.current_stroke = []
                self.redo_stack.clear()
            self.last_x = None
            self.last_y = None
            return

        # finalize shapes from drag
        x1, y1, x2, y2 = self.last_x, self.last_y, event.x, event.y
        self.last_x = None
        self.last_y = None

        # hapus preview jika ada
        if self.temp_item is not None:
            try:
                self.canvas.delete(self.temp_item)
            except tk.TclError:
                pass
            self.temp_item = None

        items = []
        outline = self.pen_color
        width = self.pen_size

        if self.current_tool == 'line':
            items.append(self.canvas.create_line(x1, y1, x2, y2, fill=outline, width=width))
        elif self.current_tool == 'rect':
            items.append(self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline, width=width))
        elif self.current_tool == 'oval':
            items.append(self.canvas.create_oval(x1, y1, x2, y2, outline=outline, width=width))
        elif self.current_tool == 'cube':
            items.extend(self._create_cube(x1, y1, x2, y2, outline, width))
        elif self.current_tool == 'cylinder':
            items.extend(self._create_cylinder(x1, y1, x2, y2, outline, width))
        elif self.current_tool == 'pyramid':
            items.extend(self._create_pyramid(x1, y1, x2, y2, outline, width))

        if items:
            self.current_stroke = items
            self.history.append(self.current_stroke)
            self.current_stroke = []
            self.redo_stack.clear()

    def finish_polygon(self, event=None):
        """Selesaikan polygon saat double-click"""
        if self.current_tool != 'polygon':
            return
        if len(self.polygon_points) < 3:
            # hapus titik-titik kecil jika tidak jadi
            for item in self.current_stroke:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
            self.current_stroke = []
            self.polygon_points = []
            if self.polygon_preview_line is not None:
                try:
                    self.canvas.delete(self.polygon_preview_line)
                except tk.TclError:
                    pass
                self.polygon_preview_line = None
            return

        # Hapus preview line
        if self.polygon_preview_line is not None:
            try:
                self.canvas.delete(self.polygon_preview_line)
            except tk.TclError:
                pass
            self.polygon_preview_line = None

        # Buat polygon final
        flat_points = [coord for pt in self.polygon_points for coord in pt]
        poly = self.canvas.create_polygon(*flat_points, outline=self.pen_color, fill='', width=self.pen_size)
        self.current_stroke.append(poly)
        self.history.append(self.current_stroke)
        self.redo_stack.clear()

        # Reset
        self.current_stroke = []
        self.polygon_points = []
        self.is_drawing = False

    def _create_cube(self, x1, y1, x2, y2, outline, width):
        items = []
        # normalize
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])
        dx = (x_max - x_min) * 0.3
        dy = (y_max - y_min) * 0.3
        # front square
        f1, f2, f3, f4 = (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)
        # back square (offset)
        b1 = (x_min + dx, y_min - dy)
        b2 = (x_max + dx, y_min - dy)
        b3 = (x_max + dx, y_max - dy)
        b4 = (x_min + dx, y_max - dy)
        # draw squares
        items.append(self.canvas.create_rectangle(*f1, *f3, outline=outline, width=width))
        items.append(self.canvas.create_rectangle(*b1, *b3, outline=outline, width=width))
        # connect corners
        items.append(self.canvas.create_line(*f1, *b1, fill=outline, width=width))
        items.append(self.canvas.create_line(*f2, *b2, fill=outline, width=width))
        items.append(self.canvas.create_line(*f3, *b3, fill=outline, width=width))
        items.append(self.canvas.create_line(*f4, *b4, fill=outline, width=width))
        return items

    def _create_cylinder(self, x1, y1, x2, y2, outline, width):
        items = []
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])
        # top and bottom ellipses
        items.append(self.canvas.create_oval(x_min, y_min, x_max, y_min + (y_max - y_min) * 0.3, outline=outline, width=width))
        items.append(self.canvas.create_oval(x_min, y_max - (y_max - y_min) * 0.3, x_max, y_max, outline=outline, width=width))
        # body rectangle sides
        items.append(self.canvas.create_line(x_min, y_min + (y_max - y_min) * 0.15, x_min, y_max - (y_max - y_min) * 0.15, fill=outline, width=width))
        items.append(self.canvas.create_line(x_max, y_min + (y_max - y_min) * 0.15, x_max, y_max - (y_max - y_min) * 0.15, fill=outline, width=width))
        return items

    def _create_pyramid(self, x1, y1, x2, y2, outline, width):
        items = []
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])
        # base rectangle
        b1, b2, b3, b4 = (x_min, y_max), (x_max, y_max), (x_max, y_min), (x_min, y_min)
        # apex (center top)
        apex = ((x_min + x_max) / 2, y_min - (y_max - y_min) * 0.3)
        # draw base
        items.append(self.canvas.create_rectangle(*b4, *b2, outline=outline, width=width))
        # connect apex to base corners
        for p in (b1, b2, b3, b4):
            items.append(self.canvas.create_line(*apex, *p, fill=outline, width=width))
        return items

    def toggle_eraser(self, event=None):
        """Toggle mode penghapus (E)"""
        # Toggle antara pen dan eraser
        if self.current_tool == 'eraser':
            self.set_tool('pen')
            self.tool_var.set('pen')
        else:
            self.set_tool('eraser')
            self.tool_var.set('eraser')

    def adjust_size(self, delta):
        """Sesuaikan ukuran pena via keyboard [ dan ]"""
        new_size = max(1, min(20, self.pen_size + delta))
        self.pen_size = new_size
        # jika ada scale, sinkronkan
        if hasattr(self, 'size_var'):
            self.size_var.set(new_size)
        self.update_info()

    def undo(self, event=None):
        """Undo goresan terakhir (Ctrl+Z)"""
        if not self.history:
            return
        stroke = self.history.pop()
        # sembunyikan semua item pada goresan
        for item in stroke:
            try:
                self.canvas.itemconfigure(item, state='hidden')
            except tk.TclError:
                # item mungkin sudah terhapus
                pass
        self.redo_stack.append(stroke)

    def redo(self, event=None):
        """Redo goresan (Ctrl+Y atau Ctrl+Shift+Z)"""
        if not self.redo_stack:
            return
        stroke = self.redo_stack.pop()
        for item in stroke:
            try:
                self.canvas.itemconfigure(item, state='normal')
            except tk.TclError:
                pass
        self.history.append(stroke)

    def show_position(self, event):
        """Event handler untuk menampilkan posisi mouse"""
        if hasattr(self, 'pos_label'):
            self.pos_label.destroy()

        self.pos_label = tk.Label(
            self.window,
            text=f"Posisi: ({event.x}, {event.y})",
            bg="yellow"
        )
        self.pos_label.place(x=event.x + 10, y=event.y + 10)

        # Hapus label setelah 1 detik
        self.window.after(1000, lambda: self.pos_label.destroy() if hasattr(self, 'pos_label') else None)

    def save_image(self, event=None):
        """Event handler untuk save (Ctrl+S)"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".ps",
            filetypes=[["PostScript files", "*.ps"], ["All files", "*.*"]]
        )
        if filename:
            self.canvas.postscript(file=filename)
            messagebox.showinfo("Info", f"Gambar disimpan sebagai {filename}")

    def open_image(self, event=None):
        """Event handler untuk open (Ctrl+O)"""
        messagebox.showinfo("Info", "Fitur buka gambar belum diimplementasi")

    def new_canvas(self, event=None):
        """Event handler untuk canvas baru (Ctrl+N)"""
        if messagebox.askyesno("Canvas Baru", "Buat canvas baru? Gambar saat ini akan hilang."):
            self.canvas.delete("all")
            self.history.clear()
            self.redo_stack.clear()

    def on_closing(self):
        """Event handler saat jendela akan ditutup"""
        if messagebox.askokcancel("Keluar", "Yakin ingin keluar? Gambar yang belum disimpan akan hilang."):
            self.window.destroy()

    def jalankan(self):
        """Method untuk menjalankan aplikasi"""
        self.window.mainloop()

# Untuk menjalankan aplikasi
if __name__ == "__main__":
    app = PaintApp()
    app.jalankan()