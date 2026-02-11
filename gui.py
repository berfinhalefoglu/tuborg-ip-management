# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from db import get_all_records, add_record, delete_record, update_record, create_db
from ip_utils import find_unused_ips, get_subnet_info, get_all_hosts, get_used_ips_in_subnet, get_unused_ips, is_valid_subnet

# 🎨 Renk Teması
THEME = {
    "bg": "#FAF1C2",
    "fg": "#000000",
    "entry_bg": "#ffffff",
    "button_bg": "#D4AF37",
    "button_fg": "#000000",
    "tree_bg_1": "#FFF8DC",
    "tree_bg_2": "#FAF1C2",
    "tree_header_bg": "#D4AF37",
    "tree_header_fg": "#000000",
    "highlight": "#D4AF37"
}

class IPAMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tuborg OT L2 Nat Table IP Yönetim Sistemi")
        self.geometry("1300x750")
        self.configure(bg=THEME["bg"])
        create_db()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        self.entries = {}
        self.form_labels = [
            "Main Line", "Line Details", "Inside VLAN ID", "Inside IP Subnet",
            "Inside Subnet Mask", "Inside IP Gateway", "Outside VLAN ID", "Outside IP Subnet",
            "Outside Subnet Bit", "Outside Subnet Mask", "Outside IP Gateway"
        ]

        form_frame = tk.Frame(self, bg=THEME["bg"])
        form_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        for i, label in enumerate(self.form_labels):
            tk.Label(form_frame, text=label, bg=THEME["bg"]).grid(row=0, column=i)
            entry = tk.Entry(form_frame, width=15, bg=THEME["entry_bg"])
            entry.grid(row=1, column=i)
            self.entries[label] = entry

        tk.Button(
            form_frame, text="Kayıt Ekle", bg=THEME["button_bg"], fg=THEME["button_fg"],
            command=self.add_record_gui
        ).grid(row=1, column=len(self.form_labels), padx=10)

        self.tree = ttk.Treeview(self, columns=self.form_labels, show="headings")
        self.tree.tag_configure("evenrow", background=THEME["tree_bg_1"])
        self.tree.tag_configure("oddrow", background=THEME["tree_bg_2"])

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=THEME["bg"], foreground=THEME["fg"], fieldbackground=THEME["bg"], rowheight=25)
        style.configure("Treeview.Heading", background=THEME["tree_header_bg"], foreground=THEME["tree_header_fg"], font=("Arial", 10, "bold"))

        for label in self.form_labels:
            self.tree.heading(label, text=label)
            self.tree.column(label, width=110, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        btn_frame = tk.Frame(self, bg=THEME["bg"])
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(btn_frame, text="Seçili Kaydı Sil", bg=THEME["button_bg"],
                  fg=THEME["button_fg"], command=self.delete_selected_record).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Seçili Kaydı Düzenle", bg=THEME["button_bg"],
                  fg=THEME["button_fg"], command=self.edit_selected_record).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Tabloyu Yazdır", bg=THEME["button_bg"],
                  fg=THEME["button_fg"], command=self.yazdir_btn_handler).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Boş IP Göster ve Ekle", bg=THEME["button_bg"],
                  fg=THEME["button_fg"], command=self.show_and_add_unused_ip).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="CIDR'den Boş IP Göster", bg=THEME["button_bg"],
                  fg=THEME["button_fg"], command=self.show_unused_ips_by_subnet).pack(side=tk.LEFT, padx=5)

    def add_record_gui(self):
        try:
            values = [self.entries[label].get() for label in self.form_labels]
            inside_vlan_id = int(values[2]) if values[2] else None
            outside_vlan_id = int(values[6]) if values[6] else None
            outside_subnet_bit = int(values[8]) if values[8] else None

            add_record(
                values[0], values[1], inside_vlan_id, values[3], values[4], values[5],
                outside_vlan_id, values[7], outside_subnet_bit, values[9], values[10]
            )
            self.refresh_table()
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt eklenirken bir hata oluştu:\n{e}")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, rec in enumerate(get_all_records()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", iid=rec['id'], tags=(tag,), values=[
                rec['main_line'], rec['line_details'], rec['inside_vlan_id'], rec['inside_ip_subnet'],
                rec['inside_subnet_mask'], rec['inside_ip_gateway'], rec['outside_vlan_id'],
                rec['outside_ip_subnet'], rec['outside_subnet_bit'], rec['outside_subnet_mask'],
                rec['outside_ip_gateway']
            ])

    def delete_selected_record(self):
        selected = self.tree.selection()
        if selected:
            record_id = int(selected[0])
            if messagebox.askyesno("Onay", "Kaydı silmek istediğine emin misin?"):
                delete_record(record_id)
                self.refresh_table()
        else:
            messagebox.showwarning("Uyarı", "Silmek için bir kayıt seçin.")

    def edit_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Düzenlemek için bir kayıt seçin.")
            return

        record_id = int(selected[0])
        current_values = self.tree.item(selected, "values")
        edit_win = tk.Toplevel(self)
        edit_win.title("Kaydı Düzenle")
        edit_win.configure(bg=THEME["bg"])

        entry_vars = []
        for i, (label, value) in enumerate(zip(self.form_labels, current_values)):
            tk.Label(edit_win, text=label, bg=THEME["bg"]).grid(row=i, column=0, sticky="e")
            var = tk.StringVar(value=value)
            tk.Entry(edit_win, textvariable=var, width=20, bg=THEME["entry_bg"]).grid(row=i, column=1)
            entry_vars.append(var)

        def save_changes():
            try:
                inside_vlan_id = int(entry_vars[2].get()) if entry_vars[2].get() else None
                outside_vlan_id = int(entry_vars[6].get()) if entry_vars[6].get() else None
                outside_subnet_bit = int(entry_vars[8].get()) if entry_vars[8].get() else None
                kwargs = {
                    "main_line": entry_vars[0].get(),
                    "line_details": entry_vars[1].get(),
                    "inside_vlan_id": inside_vlan_id,
                    "inside_ip_subnet": entry_vars[3].get(),
                    "inside_subnet_mask": entry_vars[4].get(),
                    "inside_ip_gateway": entry_vars[5].get(),
                    "outside_vlan_id": outside_vlan_id,
                    "outside_ip_subnet": entry_vars[7].get(),
                    "outside_subnet_bit": outside_subnet_bit,
                    "outside_subnet_mask": entry_vars[9].get(),
                    "outside_ip_gateway": entry_vars[10].get()
                }
                update_record(record_id, **kwargs)
                self.refresh_table()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt güncellenemedi:\n{e}")

        tk.Button(edit_win, text="Kaydet", command=save_changes,
                  bg=THEME["button_bg"], fg=THEME["button_fg"]).grid(row=len(self.form_labels), columnspan=2, pady=10)

    def yazdir_btn_handler(self):
        messagebox.showinfo("Yazdır", "Yazdırma işlemi burada uygulanabilir.")

    def show_and_add_unused_ip(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen önce bir kayıt seçin.")
            return

        record = self.tree.item(selected, "values")
        outside_subnet = record[7]

        if not outside_subnet:
            messagebox.showwarning("Uyarı", "Outside IP Subnet boş.")
            return

        used_ips = get_used_ips_in_subnet(outside_subnet)
        unused_ips = find_unused_ips(outside_subnet, used_ips)

        self.open_ip_selector(unused_ips, lambda ip: self.entries["Outside IP Gateway"].insert(0, ip))

    def show_unused_ips_by_subnet(self):
        def on_cidr_entered(cidr):
            if not is_valid_subnet(cidr):
                messagebox.showerror("Hatalı CIDR", "Geçersiz subnet girdiniz.")
                return

            records = get_all_records()
            used_ips = [r['inside_ip_gateway'] for r in records if r['inside_ip_gateway']]
            unused = get_unused_ips(cidr, used_ips)
            self.open_ip_selector(unused, lambda ip: self.entries["Inside IP Gateway"].insert(0, ip))

        self.open_subnet_input_popup(on_cidr_entered)

    def open_subnet_input_popup(self, on_cidr_entered):
        popup = tk.Toplevel(self)
        popup.title("Subnet/CIDR Gir")
        popup.geometry("300x120")
        popup.configure(bg=THEME["bg"])

        tk.Label(popup, text="Subnet/CIDR (ör: 10.26.1.0/24):", bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)

        entry = tk.Entry(popup, width=25, bg=THEME["entry_bg"], fg=THEME["fg"], insertbackground=THEME["fg"])
        entry.pack()

        def submit():
            cidr = entry.get().strip()
            popup.destroy()
            on_cidr_entered(cidr)

        tk.Button(popup, text="OK", command=submit, bg=THEME["button_bg"], fg=THEME["button_fg"]).pack(pady=10)

    def open_ip_selector(self, unused_ips, on_selected):
        if not unused_ips:
            messagebox.showinfo("Boş IP Yok", "Bu blokta boş IP bulunamadı.")
            return

        popup = tk.Toplevel(self)
        popup.title("Boş IP Seç")
        popup.geometry("300x300")
        popup.configure(bg=THEME["bg"])

        tk.Label(popup, text="Aşağıdan bir IP seçin:", bg=THEME["bg"], fg=THEME["fg"]).pack(pady=10)

        selected_ip = tk.StringVar(value=unused_ips[0])
        for ip in unused_ips[:15]:
            tk.Radiobutton(popup, text=ip, variable=selected_ip, value=ip,
                           bg=THEME["bg"], fg=THEME["fg"], selectcolor=THEME["entry_bg"]).pack(anchor="w")

        def submit():
            popup.destroy()
            on_selected(selected_ip.get())

        tk.Button(popup, text="Seç", command=submit, bg=THEME["button_bg"], fg=THEME["button_fg"]).pack(pady=10)
