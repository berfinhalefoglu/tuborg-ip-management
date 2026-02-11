# login_window.py

import tkinter as tk
from tkinter import messagebox

# Tema renkleri
THEME = {
    "bg": "#1e1e1e",           # Arka plan
    "fg": "#ffffff",           # Yazı rengi
    "button_bg": "#ff8c00",    # Buton arka planı
    "entry_bg": "#2d2d2d",     # Entry kutusu arka planı
    "entry_fg": "#ffffff",     # Entry yazı rengi
    "button_hover": "#ffa733"  # Buton üzerine gelince
}

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tuborg IP Yönetim Sistemi - Giriş")
        self.geometry("400x220")
        self.resizable(False, False)
        self.configure(bg=THEME["bg"])
        self.login_successful = False  # Giriş durumu

        # Kullanıcı Adı
        tk.Label(self, text="Kullanıcı Adı:", bg=THEME["bg"], fg=THEME["fg"]).pack(pady=(30, 5))
        self.username_entry = tk.Entry(self, bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["entry_fg"])
        self.username_entry.pack()

        # Şifre
        tk.Label(self, text="Şifre:", bg=THEME["bg"], fg=THEME["fg"]).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", bg=THEME["entry_bg"], fg=THEME["entry_fg"], insertbackground=THEME["entry_fg"])
        self.password_entry.pack()

        # Giriş Yap Butonu
        self.login_btn = tk.Button(self, text="Giriş Yap", bg=THEME["button_bg"], fg="black", command=self.login)
        self.login_btn.pack(pady=18)

        # Hover efekti
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=THEME["button_hover"]))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=THEME["button_bg"]))

        self.username_entry.focus_set()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "E" and password == "123":
            self.login_successful = True
            self.destroy()  # Sadece login penceresini kapat
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış!")
