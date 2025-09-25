import tkinter as tk
from tkinter import messagebox
import datetime
import logging
import os
import json
import re

PRIMARY_GREEN = "#006b3f"
ACCENT_GOLD = "#c7932c"
BG_LIGHT = "#f5f0e6"
TEXT_DARK = "#2f2f2f"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "logo_uin.png")

def _load_logo(path: str, max_width: int = 140):
    if not os.path.isfile(path):
        return None
    try:
        img = tk.PhotoImage(file=path)
        w = img.width()
        if w > max_width:
            factor = (w + max_width - 1) // max_width
            factor = max(1, factor)
            img = img.subsample(factor)
        return img
    except Exception:
        return None

# Data Fakultas dan Prodi (untuk dropdown terhubung)
fakultas_options = [    
    "Pilih Fakultas...",
    "Fakultas Adab dan Ilmu Budaya",
    "Fakultas Dakwah dan Komunikasi", 
    "Fakultas Ilmu Tarbiyah dan Keguruan",
    "Fakultas Syariah dan Hukum",
    "Fakultas Ushuluddin dan Pemikiran Islam",
    "Fakultas Sains dan Teknologi",
    "Fakultas Kedokteran",
    "Fakultas Ilmu Sosial dan Humaniora",
    "Fakultas Ekonomi dan Bisnis Islam"
]

jurusan_per_fakultas = {
    "Fakultas Adab dan Ilmu Budaya": [
        "Bahasa dan Sastra Arab", "Sejarah dan Kebudayaan Islam", 
        "Ilmu Perpustakaan dan Informasi", "Sastra Inggris"
    ],
    "Fakultas Dakwah dan Komunikasi": [
        "Komunikasi dan Penyiaran Islam", "Bimbingan dan Konseling Islam",
        "Pengembangan Masyarakat Islam", "Manajemen Dakwah", "Ilmu Kesejahteraan Sosial"
    ],
    "Fakultas Ilmu Tarbiyah dan Keguruan": [
        "Pendidikan Agama Islam", "Pendidikan Bahasa Arab", "Pendidikan Bahasa Inggris",
        "Pendidikan Matematika", "Pendidikan Biologi", "Pendidikan Fisika", 
        "Pendidikan Kimia", "Pendidikan Guru Madrasah Ibtidaiyah", "Pendidikan Islam Anak Usia Dini",
        "Manajemen Pendidikan Islam"
    ],
    "Fakultas Syariah dan Hukum": [
        "Hukum Keluarga Islam (Ahwal Syakhshiyyah)", "Hukum Tata Negara (Siyasah)",
        "Perbandingan Mazhab", "Hukum Ekonomi Syariah (Muamalah)", "Ilmu Hukum"
    ],
    "Fakultas Ushuluddin dan Pemikiran Islam": [
        "Aqidah dan Filsafat Islam", "Ilmu Al-Qur'an dan Tafsir",
        "Ilmu Hadits", "Perbandingan Agama", "Studi Agama-Agama"
    ],
    "Fakultas Sains dan Teknologi": [
        "Matematika", "Fisika", "Kimia", "Biologi", "Informatika",
        "Teknik Industri", "Arsitektur"
    ],
    "Fakultas Kedokteran": [
        "Pendidikan Dokter", "Biomedis"
    ],
    "Fakultas Ilmu Sosial dan Humaniora": [
        "Psikologi", "Ilmu Komunikasi"
    ],
    "Fakultas Ekonomi dan Bisnis Islam": [
        "Ekonomi Syariah", "Perbankan Syariah", "Akuntansi Syariah",
        "Manajemen Keuangan Syariah"
    ]
}

# Konfigurasi logging aplikasi
logging.basicConfig(
    filename="aplikasi_biodata.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class AplikasiBiodata(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window config
        self.title("Aplikasi Biodata Mahasiswa")
        self.geometry("680x760")
        self.configure(bg=BG_LIGHT)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.keluar_aplikasi)

        # Database user sederhana
        self.users_db = {
            "admin": "123",
            "user1": "password1",
            "mahasiswa": "123456",
        }

        # Prefs & state
        self._prefs_path = os.path.join(os.path.dirname(__file__), "biodata_prefs.json")
        self._password_visible = False
        self.current_user = None
        self.frame_aktif = None
        self.prefs = self._load_prefs()

        # Siapkan tampilan dan menu
        self._buat_tampilan_login()
        self._buat_tampilan_biodata()
        self._buat_menu()

        # Tampilkan login dulu
        self._pindah_ke(self.frame_login)
        logging.info("Aplikasi dimulai")

    # ---------------- Login ----------------
    def _buat_tampilan_login(self):
        self.frame_login = tk.Frame(master=self, padx=20, pady=40, bg=BG_LIGHT)
        self.frame_login.grid_columnconfigure(0, weight=1)
        # Logo
        self.logo_login = _load_logo(LOGO_PATH, max_width=110)
        if self.logo_login:
            tk.Label(self.frame_login, image=self.logo_login, bg=BG_LIGHT).grid(row=0, column=0, pady=(0, 6))
        tk.Label(
            self.frame_login,
            text="HALAMAN LOGIN",
            font=("Arial", 18, "bold"),
            bg=BG_LIGHT,
            fg=PRIMARY_GREEN,
        ).grid(row=1, column=0, pady=(0, 14))

        # Kartu/Panel login dengan border & padding
        self.frame_login_card = tk.Frame(
            self.frame_login,
            relief=tk.GROOVE,
            borderwidth=2,
            padx=16,
            pady=16,
            bg="white",
            highlightthickness=2,
            highlightbackground=ACCENT_GOLD,
        )
        self.frame_login_card.grid(row=2, column=0, sticky="EW")
        self.frame_login_card.grid_columnconfigure(0, weight=0)
        self.frame_login_card.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.frame_login_card,
            text="Username:",
            font=("Arial", 12),
            anchor="w",
            justify=tk.LEFT,
        ).grid(row=0, column=0, sticky="W", pady=5, padx=(0, 6))
        self.entry_username = tk.Entry(self.frame_login_card, font=("Arial", 12))
        self.entry_username.grid(row=0, column=1, pady=5, sticky="EW")

        tk.Label(
            self.frame_login_card,
            text="Password:",
            font=("Arial", 12),
            anchor="w",
            justify=tk.LEFT,
        ).grid(row=1, column=0, sticky="W", pady=5, padx=(0, 6))
        # Frame untuk password + toggle show/hide
        self.frame_password = tk.Frame(self.frame_login_card, bg="white")
        self.frame_password.grid(row=1, column=1, pady=5, sticky="EW")
        self.frame_password.grid_columnconfigure(0, weight=1)
        self.entry_password = tk.Entry(self.frame_password, font=("Arial", 12), show="*")
        self.entry_password.grid(row=0, column=0, sticky="EW")
        self.btn_toggle_pwd = tk.Button(
            self.frame_password,
            text="Show",
            width=6,
            command=self._toggle_password_visibility,
        )
        self.btn_toggle_pwd.grid(row=0, column=1, padx=(6, 0))

        # Remember Me
        self.var_remember = tk.IntVar(value=1 if self.prefs.get("remember", False) else 0)
        self.chk_remember = tk.Checkbutton(self.frame_login_card, text="Remember Me", variable=self.var_remember, bg="white")
        self.chk_remember.grid(row=2, column=0, columnspan=2, sticky="W", pady=(2, 8))

        self.btn_login = tk.Button(
            self.frame_login,
            text="Login",
            font=("Arial", 12, "bold"),
            command=self._coba_login,
            bg=PRIMARY_GREEN,
            fg="white",
            activebackground=ACCENT_GOLD,
            activeforeground="white",
            relief=tk.RAISED,
            cursor="hand2",
        )
        self.btn_login.grid(row=3, column=0, pady=20, sticky="EW")

        # Shortcuts
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda e: self._coba_login())

        tk.Label(
            self.frame_login,
            font=("Arial", 9),
            fg="gray",
            justify=tk.LEFT,
        ).grid(row=5, column=0, columnspan=2, pady=10)

        # Prefill username dari prefs jika diingat
        remembered_username = self.prefs.get("remembered_username") if self.prefs.get("remember", False) else None
        if remembered_username:
            self.entry_username.insert(0, remembered_username)
            self.after(50, lambda: self.entry_password.focus_set())
        self.frame_login.bind("<Configure>", lambda e: self._update_login_label_wrap())

    def _coba_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        logging.info(f"Login attempt for username: {username}")

        if not username or not password:
            logging.warning("Empty credentials on login")
            messagebox.showwarning("Login Gagal", "Username dan Password tidak boleh kosong.")
            self.entry_username.focus_set()
            return

        if len(username) < 3:
            logging.warning("Username too short")
            messagebox.showwarning("Login Gagal", "Username minimal 3 karakter.")
            self.entry_username.focus_set()
            return

        if self.users_db.get(username) == password:
            self.current_user = username
            logging.info(f"Successful login: {username}")
            self._update_title_with_user()
            self._reset_form_biodata()
            self._pindah_ke(self.frame_biodata)
            # Simpan prefs jika Remember Me dicentang
            if self.var_remember.get() == 1:
                self.prefs["remember"] = True
                self.prefs["remembered_username"] = username
            else:
                self.prefs["remember"] = False
                self.prefs.pop("remembered_username", None)
            self._save_prefs()
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            self.after(100, lambda: self.entry_nama.focus_set())
        else:
            logging.warning(f"Failed login attempt: {username}")
            messagebox.showerror("Login Gagal", "Username atau Password salah.")
            self.entry_password.delete(0, tk.END)
            self.entry_username.focus_set()

    # ---------------- Biodata ----------------
    def _buat_tampilan_biodata(self):
        # Variabel kontrol
        self.var_nama = tk.StringVar()
        self.var_nim = tk.StringVar()
        # Dropdown Fakultas & Prodi
        self.var_fakultas = tk.StringVar(value=fakultas_options[0])
        self.var_prodi = tk.StringVar(value="Pilih Prodi...")
        self.var_email = tk.StringVar()
        self.var_tel = tk.StringVar()
        self.var_tgl = tk.StringVar()  # format YYYY-MM-DD
        self.var_jk = tk.StringVar(value="Pria")
        self.var_setuju = tk.IntVar()

        # Frame utama biodata
        self.frame_biodata = tk.Frame(master=self, padx=20, pady=20)
        self.frame_biodata.columnconfigure(1, weight=1)
        self.frame_biodata.configure(bg=BG_LIGHT)

        # Logo UIN di atas judul
        self.logo_image = _load_logo(LOGO_PATH, max_width=110)
        if self.logo_image:
            lbl_logo = tk.Label(self.frame_biodata, image=self.logo_image, bg=BG_LIGHT)
            lbl_logo.grid(row=0, column=0, columnspan=2, pady=(0, 6))

        tk.Label(
            self.frame_biodata,
            text="FORM BIODATA MAHASISWA",
            font=("Arial", 18, "bold"),
            bg=BG_LIGHT,
            fg=PRIMARY_GREEN,
        ).grid(row=1, column=0, columnspan=2, pady=(0, 14))

        # Frame input
        self.frame_input = tk.Frame(
            self.frame_biodata,
            relief=tk.GROOVE,
            borderwidth=2,
            padx=12,
            pady=12,
            bg="white",
            highlightthickness=2,
            highlightbackground=ACCENT_GOLD,
        )
        self.frame_input.grid(row=2, column=0, columnspan=2, sticky="EW")
        self.frame_input.grid_columnconfigure(0, weight=0)
        self.frame_input.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.frame_input, text="Nama Lengkap:", font=("Arial", 12), anchor="w", justify=tk.LEFT
        ).grid(row=0, column=0, sticky="W", pady=2, padx=(0, 8))
        self.entry_nama = tk.Entry(self.frame_input, width=30, font=("Arial", 12), textvariable=self.var_nama)
        self.entry_nama.grid(row=0, column=1, pady=2, sticky="EW")

        tk.Label(self.frame_input, text="NIM:", font=("Arial", 12), anchor="w", justify=tk.LEFT).grid(
            row=1, column=0, sticky="W", pady=2, padx=(0, 8)
        )
        self.entry_nim = tk.Entry(self.frame_input, width=30, font=("Arial", 12), textvariable=self.var_nim)
        self.entry_nim.grid(row=1, column=1, pady=2, sticky="EW")

        # Fakultas (dropdown)
        tk.Label(self.frame_input, text="Fakultas:", font=("Arial", 12), anchor="w", justify=tk.LEFT).grid(
            row=2, column=0, sticky="W", pady=2, padx=(0, 8)
        )
        self.option_fakultas = tk.OptionMenu(self.frame_input, self.var_fakultas, *fakultas_options)
        self.option_fakultas.config(font=("Arial", 11), width=26)
        self.option_fakultas.grid(row=2, column=1, pady=2, sticky="EW")

        # Prodi (dropdown)
        tk.Label(self.frame_input, text="Prodi:", font=("Arial", 12), anchor="w", justify=tk.LEFT).grid(
            row=3, column=0, sticky="W", pady=2, padx=(0, 8)
        )
        self.option_prodi = tk.OptionMenu(self.frame_input, self.var_prodi, "Pilih Prodi...")
        self.option_prodi.config(font=("Arial", 11), width=26)
        self.option_prodi.grid(row=3, column=1, pady=2, sticky="EW")

        # Email
        tk.Label(self.frame_input, text="Email:", font=("Arial", 12), anchor="w", justify=tk.LEFT).grid(
            row=4, column=0, sticky="W", pady=2, padx=(0, 8)
        )
        self.entry_email = tk.Entry(self.frame_input, width=30, font=("Arial", 12), textvariable=self.var_email)
        self.entry_email.grid(row=4, column=1, pady=2, sticky="EW")

        # Telepon
        tk.Label(self.frame_input, text="Telepon:", font=("Arial", 12), anchor="w", justify=tk.LEFT).grid(
            row=5, column=0, sticky="W", pady=2, padx=(0, 8)
        )
        self.entry_tel = tk.Entry(self.frame_input, width=30, font=("Arial", 12), textvariable=self.var_tel)
        self.entry_tel.grid(row=5, column=1, pady=2, sticky="EW")

        # Tanggal Lahir
        tk.Label(
            self.frame_input,
            text="Tanggal Lahir (YYYY-MM-DD):",
            font=("Arial", 12),
            anchor="w",
            justify=tk.LEFT,
        ).grid(row=6, column=0, sticky="W", pady=2, padx=(0, 8))
        self.entry_tgl = tk.Entry(self.frame_input, width=30, font=("Arial", 12), textvariable=self.var_tgl)
        self.entry_tgl.grid(row=6, column=1, pady=2, sticky="EW")

        # Alamat
        tk.Label(self.frame_input, text="Alamat:", font=("Arial", 12), anchor="w", justify=tk.LEFT).grid(
            row=7, column=0, sticky="NW", pady=2, padx=(0, 8)
        )
        self.frame_alamat = tk.Frame(self.frame_input, relief=tk.SUNKEN, borderwidth=1)
        self.frame_alamat.grid(row=7, column=1, pady=2, sticky="EW")
        self.frame_alamat.grid_columnconfigure(0, weight=1)
        self.text_alamat = tk.Text(self.frame_alamat, height=5, width=28, font=("Arial", 12))
        self.text_alamat.grid(row=0, column=0, sticky="NSEW")
        self.scrollbar_alamat = tk.Scrollbar(self.frame_alamat, command=self.text_alamat.yview)
        self.scrollbar_alamat.grid(row=0, column=1, sticky="NS")
        self.text_alamat.config(yscrollcommand=self.scrollbar_alamat.set)

        tk.Label(self.frame_input, text="Jenis Kelamin:", font=("Arial", 12), anchor="w", justify=tk.LEFT).grid(
            row=8, column=0, sticky="W", pady=2, padx=(0, 8)
        )
        self.frame_jk = tk.Frame(self.frame_input)
        self.frame_jk.grid(row=8, column=1, sticky="W")
        tk.Radiobutton(self.frame_jk, text="Pria", variable=self.var_jk, value="Pria").pack(side=tk.LEFT)
        tk.Radiobutton(self.frame_jk, text="Wanita", variable=self.var_jk, value="Wanita").pack(side=tk.LEFT)

        self.check_setuju = tk.Checkbutton(
            self.frame_input,
            text="Saya menyetujui pengumpulan data ini.",
            variable=self.var_setuju,
            font=("Arial", 10),
            command=self.validate_form,
        )
        self.check_setuju.grid(row=9, column=0, columnspan=2, pady=10, sticky="W")

        # Tombol aksi
        self.frame_actions = tk.Frame(self.frame_biodata)
        self.frame_actions.grid(row=9, column=0, columnspan=2, sticky="EW", pady=(10, 0))
        self.btn_reset = tk.Button(
            self.frame_actions,
            text="Reset Form",
            command=self._reset_form_biodata,
            bg=PRIMARY_GREEN,
            fg="white",
            activebackground=ACCENT_GOLD,
            activeforeground="white",
            relief=tk.RAISED,
            cursor="hand2",
        )
        self.btn_reset.pack(side=tk.LEFT)
        # self.btn_logout = tk.Button(self.frame_actions, text="Logout", command=self._logout)
        # self.btn_logout.pack(side=tk.LEFT, padx=8)

        self.btn_submit = tk.Button(
            self.frame_biodata,
            text="Submit Biodata",
            font=("Arial", 12, "bold"),
            command=self.submit_data,
            state=tk.DISABLED,
            bg=PRIMARY_GREEN,
            fg="white",
            activebackground=ACCENT_GOLD,
            activeforeground="white",
            relief=tk.RAISED,
            cursor="hand2",
        )
        self.btn_submit.grid(row=10, column=0, columnspan=2, pady=16, sticky="EW")

        self.label_hasil = tk.Label(
            self.frame_biodata,
            text="",
            font=("Arial", 12, "italic"),
            justify=tk.LEFT,
            bg=BG_LIGHT,
            fg=TEXT_DARK,
        )
        self.label_hasil.grid(row=11, column=0, columnspan=2, sticky="W", padx=10)

        # Events
        self.btn_submit.bind("<Enter>", self.on_enter)
        self.btn_submit.bind("<Leave>", self.on_leave)
        self.entry_nama.bind("<Return>", self.submit_shortcut)
        self.entry_nim.bind("<Return>", self.submit_shortcut)
        # OptionMenu tidak pakai Enter binding
        self.entry_email.bind("<Return>", self.submit_shortcut)
        self.entry_tel.bind("<Return>", self.submit_shortcut)
        self.entry_tgl.bind("<Return>", self.submit_shortcut)
        self.text_alamat.bind("<Return>", self.submit_shortcut)
        self.frame_biodata.bind("<Configure>", lambda e: self._update_form_label_wrap())
        self.frame_input.bind("<Configure>", lambda e: self._update_form_label_wrap())

        # Trace validasi
        self.var_nama.trace_add("write", self.validate_form)
        self.var_nim.trace_add("write", self.validate_form)
        self.var_fakultas.trace_add("write", self.validate_form)
        self.var_prodi.trace_add("write", self.validate_form)
        self.var_fakultas.trace_add("write", self._update_prodi_options)
        # Inisialisasi Prodi awal
        self._update_prodi_options()
        self.var_email.trace_add("write", self.validate_form)
        self.var_tel.trace_add("write", self.validate_form)
        self.var_tgl.trace_add("write", self.validate_form)

    # ---------------- Menu ----------------
    def _buat_menu(self):
        # Top bar Menubutton
        self.menu_topbar = tk.Frame(self, bg=BG_LIGHT)
        self.menu_button = tk.Menubutton(
            self.menu_topbar,
            text="Menu",
            relief=tk.RAISED,
            bg="white",
            activebackground=ACCENT_GOLD,
        )
        self.menu_button.pack(side=tk.LEFT, padx=8, pady=4)

        self.dropdown_menu = tk.Menu(self.menu_button, tearoff=0)
        self.dropdown_menu.add_command(label="Simpan Hasil", command=self.simpan_hasil)
        self.dropdown_menu.add_separator()
        self.dropdown_menu.add_command(label="Logout", command=self._logout)
        self.dropdown_menu.add_separator()
        self.dropdown_menu.add_command(label="Keluar", command=self.keluar_aplikasi)
        self.menu_button.config(menu=self.dropdown_menu)
        self.menu_button.bind("<Enter>", self._post_menu) # Hover untuk menampilkan opsi

    def _update_title_with_user(self):
        if self.current_user:
            self.title(f"Aplikasi Biodata Mahasiswa - User: {self.current_user}")
        else:
            self.title("Aplikasi Biodata Mahasiswa")

    # ---------------- Util & Events ----------------
    def _pindah_ke(self, frame_tujuan):
        if self.frame_aktif is not None:
            self.frame_aktif.pack_forget()
        if hasattr(self, 'menu_topbar'):
            if frame_tujuan == self.frame_login:
                self.menu_topbar.pack_forget()
            else:
                self.menu_topbar.pack(side=tk.TOP, fill=tk.X)
        self.frame_aktif = frame_tujuan
        self.frame_aktif.pack(fill=tk.BOTH, expand=True)

    def _post_menu(self, event=None):
        try:
            x = self.menu_button.winfo_rootx()
            y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
            self.dropdown_menu.post(x, y)
        except Exception:
            pass

    def _update_prodi_options(self, *args):
        try:
            fak = self.var_fakultas.get()
            menu = self.option_prodi["menu"]
            menu.delete(0, "end")
            prodi_list = jurusan_per_fakultas.get(fak, [])
            if not prodi_list:
                self.var_prodi.set("Pilih Prodi...")
                menu.add_command(label="Pilih Prodi...", command=lambda v="Pilih Prodi...": self.var_prodi.set(v))
            else:
                # Set default ke item pertama
                self.var_prodi.set(prodi_list[0])
                for p in prodi_list:
                    menu.add_command(label=p, command=lambda v=p: self.var_prodi.set(v))
        except Exception:
            pass

    def validate_form(self, *args):
        nama = self.var_nama.get().strip()
        nim = self.var_nim.get().strip()
        fakultas = self.var_fakultas.get().strip()
        prodi = self.var_prodi.get().strip()
        email = self.var_email.get().strip()
        tel = self.var_tel.get().strip()
        tgl = self.var_tgl.get().strip()
        setuju = self.var_setuju.get() == 1

        nim_ok = nim.isdigit() and len(nim) >= 8 if nim else False
        nama_ok = not nama.isdigit() if nama else False
        email_ok = bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email)) if email else False
        tel_ok = bool(re.match(r"^(\+62|0)8\d{7,11}$", tel)) if tel else False
        tgl_ok = False
        if tgl:
            try:
                d = datetime.datetime.strptime(tgl, "%Y-%m-%d").date()
                tgl_ok = d <= datetime.date.today()
            except ValueError:
                tgl_ok = False

        fakultas_ok = fakultas not in ("", "Pilih Fakultas...")
        prodi_ok = prodi not in ("", "Pilih Prodi...")
        required_ok = all([nama, nim, fakultas_ok, prodi_ok, email, tel, tgl, setuju])
        form_ok = required_ok and nim_ok and nama_ok and email_ok and tel_ok and tgl_ok

        if form_ok:
            self.btn_submit.config(state=tk.NORMAL, bg=PRIMARY_GREEN, fg="white", cursor="hand2")
        else:
            try:
                system_face = self.tk.eval('tk::palette')
            except Exception:
                system_face = None
            disabled_bg = "#c9c9c9"
            self.btn_submit.config(state=tk.DISABLED, bg=disabled_bg, fg="#6b6b6b", cursor="arrow")

    def submit_data(self):
        try:
            if self.var_setuju.get() == 0:
                messagebox.showwarning("Peringatan", "Anda harus menyetujui pengumpulan data!")
                return

            nama = self.entry_nama.get().strip()
            nim = self.entry_nim.get().strip()
            fakultas = self.var_fakultas.get().strip()
            prodi = self.var_prodi.get().strip()
            email = self.entry_email.get().strip()
            tel = self.entry_tel.get().strip()
            tgl = self.entry_tgl.get().strip()
            alamat = self.text_alamat.get("1.0", tk.END).strip()
            jenis_kelamin = self.var_jk.get()

            if not (nama and nim and email and tel and tgl) or fakultas in ("", "Pilih Fakultas...") or prodi in ("", "Pilih Prodi..."):
                messagebox.showwarning("Input Kosong", "Semua field wajib (Nama, NIM, Fakultas, Prodi, Email, Telepon, Tanggal Lahir) harus diisi!")
                return

            if not nim.isdigit() or len(nim) < 8:
                messagebox.showwarning("Format NIM Salah", "NIM harus berupa angka minimal 8 digit!")
                self.entry_nim.focus_set()
                return

            if nama.isdigit():
                messagebox.showwarning("Format Nama Salah", "Nama tidak boleh hanya berupa angka!")
                self.entry_nama.focus_set()
                return

            # Validasi email
            if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
                messagebox.showwarning("Format Email Salah", "Masukkan email yang valid (contoh: nama@domain.com)")
                self.entry_email.focus_set()
                return

            # Validasi telepon Indonesia
            if not re.match(r"^(\+62|0)8\d{7,11}$", tel):
                messagebox.showwarning("Format Telepon Salah", "Masukkan nomor telepon Indonesia yang valid (08… atau +628…)")
                self.entry_tel.focus_set()
                return

            # Validasi tanggal lahir
            try:
                d = datetime.datetime.strptime(tgl, "%Y-%m-%d").date()
                if d > datetime.date.today():
                    messagebox.showwarning("Tanggal Lahir Tidak Valid", "Tanggal lahir tidak boleh di masa depan.")
                    self.entry_tgl.focus_set()
                    return
            except ValueError:
                messagebox.showwarning("Format Tanggal Salah", "Gunakan format YYYY-MM-DD (contoh: 2000-01-31)")
                self.entry_tgl.focus_set()
                return

            hasil = (
                f"Nama: {nama}\n"
                f"NIM: {nim}\n"
                f"Fakultas: {fakultas}\n"
                f"Prodi: {prodi}\n"
                f"Email: {email}\n"
                f"Telepon: {tel}\n"
                f"Tanggal Lahir: {tgl}\n"
                f"Alamat: {alamat}\n"
                f"Jenis Kelamin: {jenis_kelamin}"
            )
            messagebox.showinfo("Data Tersimpan", hasil)

            hasil_lengkap = (
                f"BIODATA TERSIMPAN:\nDiinput oleh: {self.current_user or '-'}\n\n{hasil}"
            )
            self.label_hasil.config(text=hasil_lengkap)
            logging.info(f"Data submitted by user: {self.current_user} - NIM: {nim}")
        except Exception as e:
            logging.error(f"Error in submit_data by {self.current_user}: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan saat memproses data:\n{str(e)}")

    def simpan_hasil(self):
        try:
            hasil_tersimpan = self.label_hasil.cget("text")
            if not hasil_tersimpan or "BIODATA TERSIMPAN" not in hasil_tersimpan:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan. Mohon submit terlebih dahulu.")
                return

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"biodata_{(self.current_user or 'anon')}_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Data disimpan oleh: {self.current_user or '-'}\n")
                f.write(
                    f"Waktu penyimpanan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write("-" * 50 + "\n")
                f.write(hasil_tersimpan)

            logging.info(f"Saved biodata file: {filename}")
            messagebox.showinfo("Info", f"Data berhasil disimpan ke file '{filename}'.")
        except PermissionError:
            messagebox.showerror("Error", "Tidak memiliki izin untuk menyimpan file di lokasi ini.")
        except Exception as e:
            logging.error(f"Error saving file: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan saat menyimpan file:\n{str(e)}")

    def _reset_form_biodata(self):
        self.var_nama.set("")
        self.var_nim.set("")
        self.var_fakultas.set(fakultas_options[0])
        self.var_prodi.set("Pilih Prodi...")
        self.var_email.set("")
        self.var_tel.set("")
        self.var_tgl.set("")
        self.text_alamat.delete("1.0", tk.END)
        self.var_jk.set("Pria")
        self.var_setuju.set(0)
        self.label_hasil.config(text="")
        self.validate_form()

    def _logout(self):
        if not self.current_user:
            self._pindah_ke(self.frame_login)
            return
        ask_yes_no = getattr(messagebox, 'askyesno', None)
        if ask_yes_no is not None:
            confirm = ask_yes_no("Logout", f"Apakah {self.current_user} yakin ingin logout?")
        else:
            confirm = messagebox.askquestion("Logout", f"Apakah {self.current_user} yakin ingin logout?") == 'yes'

        if confirm:
            logging.info(f"User logout: {self.current_user}")
            self.current_user = None
            self._update_title_with_user()
            self._reset_form_biodata()
            self._pindah_ke(self.frame_login)
            self.entry_username.focus_set()

    def keluar_aplikasi(self):
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?"):
            logging.info(f"Application closed by user: {self.current_user}")
            self.destroy()

    def on_enter(self, event):
        if self.btn_submit["state"] == tk.NORMAL:
            self.btn_submit.config(bg="lightblue")

    def on_leave(self, event):
        self.btn_submit.config(bg="SystemButtonFace")

    def submit_shortcut(self, event=None):
        if self.btn_submit["state"] == tk.NORMAL:
            self.submit_data()
            return "break"

    # ---------------- Helpers ----------------
    def _update_form_label_wrap(self):
        """Sesuaikan wraplength label di kolom kiri form sesuai lebar frame."""
        try:
            col0_width = max(80, int(self.frame_input.winfo_width() * 0.35))
            for w in self.frame_input.winfo_children():
                if isinstance(w, tk.Label):
                    info = w.grid_info()
                    if info and int(info.get("column", 1)) == 0 and int(info.get("columnspan", 1)) == 1:
                        w.configure(wraplength=col0_width, justify=tk.LEFT, anchor="w")
        except Exception:
            pass

    def _update_login_label_wrap(self):
        """Sesuaikan wraplabel login (kolom label kiri) sesuai lebar frame login."""
        try:
            target = getattr(self, "frame_login_card", self.frame_login)
            col0_width = max(80, int(target.winfo_width() * 0.35))
            for w in target.winfo_children():
                if isinstance(w, tk.Label):
                    info = w.grid_info()
                    if info and int(info.get("column", 1)) == 0 and int(info.get("columnspan", 1)) == 1:
                        w.configure(wraplength=col0_width, justify=tk.LEFT, anchor="w")
        except Exception:
            pass
    def _toggle_password_visibility(self):
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.entry_password.config(show="")
            self.btn_toggle_pwd.config(text="Hide")
        else:
            self.entry_password.config(show="*")
            self.btn_toggle_pwd.config(text="Show")

    def _load_prefs(self):
        try:
            if os.path.exists(self._prefs_path):
                with open(self._prefs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        return {}

    def _save_prefs(self):
        try:
            with open(self._prefs_path, "w", encoding="utf-8") as f:
                json.dump(self.prefs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    app = AplikasiBiodata()
    app.mainloop()