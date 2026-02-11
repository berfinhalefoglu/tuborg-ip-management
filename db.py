import sqlite3

DB_NAME = "tuborg_nat.db"
TABLE_NAME = "nat_table"

def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_line TEXT,
            line_details TEXT,
            inside_vlan_id INTEGER,
            inside_ip_subnet TEXT,
            inside_subnet_mask TEXT,
            inside_ip_gateway TEXT,
            outside_vlan_id INTEGER,
            outside_ip_subnet TEXT,
            outside_subnet_bit INTEGER,
            outside_subnet_mask TEXT,
            outside_ip_gateway TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_record(main_line, line_details, inside_vlan_id, inside_ip_subnet, inside_subnet_mask, inside_ip_gateway,
               outside_vlan_id, outside_ip_subnet, outside_subnet_bit, outside_subnet_mask, outside_ip_gateway):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f'''
        INSERT INTO {TABLE_NAME} (
            main_line, line_details, inside_vlan_id, inside_ip_subnet, inside_subnet_mask, inside_ip_gateway,
            outside_vlan_id, outside_ip_subnet, outside_subnet_bit, outside_subnet_mask, outside_ip_gateway
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        main_line, line_details, inside_vlan_id, inside_ip_subnet, inside_subnet_mask, inside_ip_gateway,
        outside_vlan_id, outside_ip_subnet, outside_subnet_bit, outside_subnet_mask, outside_ip_gateway
    ))
    conn.commit()
    conn.close()

def delete_record(record_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"DELETE FROM {TABLE_NAME} WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

def update_record(record_id, **kwargs):
    if not kwargs:
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    fields = ', '.join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [record_id]
    c.execute(f"UPDATE {TABLE_NAME} SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_used_ips(subnet_column="inside_ip_subnet", subnet_filter=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if subnet_filter:
        c.execute(f"SELECT {subnet_column} FROM {TABLE_NAME} WHERE {subnet_column} LIKE ?", (f"{subnet_filter}%",))
    else:
        c.execute(f"SELECT {subnet_column} FROM {TABLE_NAME}")
    ips = [row[0] for row in c.fetchall() if row[0]]
    conn.close()
    return ips

def search_records_by_term(term):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    like_term = f"%{term}%"
    c.execute(f"""
        SELECT * FROM {TABLE_NAME}
        WHERE main_line LIKE ? OR line_details LIKE ? OR inside_ip_subnet LIKE ? OR outside_ip_subnet LIKE ?
    """, (like_term, like_term, like_term, like_term))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ✅ Yeni fonksiyon: Departmana göre boş IP listesi
def get_empty_ips_by_department(department_name):
    """
    Belirli bir departman adına göre IP kayıtlarını getirir.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(f"SELECT * FROM {TABLE_NAME} WHERE line_details = ?", (department_name,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 🔍 Test amaçlı çalıştırılabilir:
if __name__ == "__main__":
    create_db()

    print("📋 Tüm Kayıtlar:")
    for row in get_all_records():
        print(row)

    print("\n📌 Kullanılan inside_ip_subnet IP'leri:")
    print(get_used_ips("inside_ip_subnet"))

    print("\n📌 Muhasebe departmanındaki IP'ler:")
    print(get_empty_ips_by_department("Muhasebe"))
