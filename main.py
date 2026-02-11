# main.py

from login_window import LoginWindow
from gui import IPAMApp

def main():
    login_window = LoginWindow()
    login_window.mainloop()

    # Giriş başarılı ise ana uygulamayı başlat
    if getattr(login_window, "login_successful", False):
        app = IPAMApp()
        app.mainloop()
    else:
        print("🔐 Giriş başarısız veya kullanıcı tarafından iptal edildi.")

if __name__ == "__main__":
    main()
