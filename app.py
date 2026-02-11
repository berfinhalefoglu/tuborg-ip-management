from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db import create_db, get_all_records, add_record, delete_record, update_record
from db import create_db, get_all_records, add_record, delete_record, update_record, search_records_by_term
import ipaddress
from flask import request, jsonify

app = Flask(__name__)
app.secret_key = 'tuborg-secret-key'
create_db()

USERNAME = 'admin'
PASSWORD = '123'


# Giriş kontrolü
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return redirect(url_for("index"))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            flash("Başarıyla giriş yaptınız.")
            return redirect(url_for("index"))
        else:
            flash("Kullanıcı adı veya şifre hatalı.")
    theme = session.get('theme', 'light')
    return render_template("login.html", theme=theme)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Başarıyla çıkış yaptınız.")
    return redirect(url_for("login"))


@app.route('/toggle-theme')
def toggle_theme():
    current = session.get('theme', 'light')
    session['theme'] = 'dark' if current == 'light' else 'light'
    return redirect(request.referrer or url_for('index'))


@app.route('/index')
@login_required
def index():
    records = get_all_records()
    theme = session.get('theme', 'light')
    return render_template("index.html", records=records, theme=theme)


@app.route('/add', methods=["POST"])
@login_required
def add():
    form = request.form
    try:
        add_record(
            form['main_line'], form['line_details'],
            int(form['inside_vlan_id'] or 0),
            form['inside_ip_subnet'], form['inside_subnet_mask'], form['inside_ip_gateway'],
            int(form['outside_vlan_id'] or 0),
            form['outside_ip_subnet'], int(form['outside_subnet_bit'] or 0),
            form['outside_subnet_mask'], form['outside_ip_gateway']
        )
        flash("Kayıt başarıyla eklendi.")
    except Exception as e:
        flash(f"Kayıt eklenirken hata oluştu: {str(e)}")
    return redirect(url_for("index"))


@app.route('/update', methods=["POST"])
@login_required
def update():
    record_id = request.form.get("record_id")
    if not record_id:
        flash("Güncelleme için kayıt ID'si eksik.")
        return redirect(url_for("index"))

    updated_data = {
        'main_line': request.form.get('main_line'),
        'line_details': request.form.get('line_details'),
        'inside_vlan_id': int(request.form.get('inside_vlan_id') or 0),
        'inside_ip_subnet': request.form.get('inside_ip_subnet'),
        'inside_subnet_mask': request.form.get('inside_subnet_mask'),
        'inside_ip_gateway': request.form.get('inside_ip_gateway'),
        'outside_vlan_id': int(request.form.get('outside_vlan_id') or 0),
        'outside_ip_subnet': request.form.get('outside_ip_subnet'),
        'outside_subnet_bit': int(request.form.get('outside_subnet_bit') or 0),
        'outside_subnet_mask': request.form.get('outside_subnet_mask'),
        'outside_ip_gateway': request.form.get('outside_ip_gateway'),
    }

    try:
        update_record(record_id, **updated_data)
        flash("Kayıt başarıyla güncellendi.")
    except Exception as e:
        flash(f"Güncelleme başarısız: {str(e)}")

    return redirect(url_for("index"))

@app.route('/search')
@login_required
def search():
    term = request.args.get('q', '')
    if term:
        records = search_records_by_term(term)
    else:
        records = get_all_records()
    theme = session.get('theme', 'light')
    return render_template('index.html', records=records, theme=theme)

@app.route('/delete/<int:id>', methods=["POST"])
@login_required
def delete(id):
    try:
        delete_record(id)
        flash("Kayıt başarıyla silindi.")
    except Exception as e:
        flash(f"Silme işlemi başarısız: {str(e)}")
    return redirect(url_for("index"))


@app.route('/handle-department', methods=["POST"])
@login_required
def handle_department():
    existing = request.form.get("existing_department")
    new = request.form.get("new_department")
    selected_department = new.strip() if new.strip() else existing
    flash(f"Seçilen departman: {selected_department}")
    return redirect(url_for("index"))


@app.route('/edit-selected')
@login_required
def edit_selected():
    flash("Düzenleme işlevi henüz geliştirilmedi.")
    return redirect(url_for("index"))


@app.route('/delete-selected')
@login_required
def delete_selected():
    flash("Seçili kayıt silme işlevi henüz geliştirilmedi.")
    return redirect(url_for("index"))


@app.route('/show-add-empty-ip')
@login_required
def show_add_empty_ip():
    flash("Boş IP ekleme işlevi henüz geliştirilmedi.")
    return redirect(url_for("index"))


@app.route('/show-empty-ip-cidr')
@login_required
def show_empty_ip_cidr():
    flash("CIDR IP sorgulama işlevi henüz geliştirilmedi.")
    return redirect(url_for("index"))


# ✅ Yeni API: Departmana göre boş IP'leri getir
@app.route('/api/empty-ips')
@login_required
def get_empty_ips():
    department = request.args.get('department')
    
    # Örnek veri - burada veritabanından departmana göre filtreleme yapılabilir
    sample_data = [
        {
            "main_line": "Metro-01",
            "line_details": department,
            "inside_vlan_id": "103",
            "inside_ip_subnet": "192.168.30.0",
            "inside_subnet_mask": "255.255.255.0",
            "inside_ip_gateway": "192.168.30.1",
            "outside_vlan_id": "203",
            "outside_ip_subnet": "10.10.3.0",
            "outside_subnet_bit": "24",
            "outside_subnet_mask": "255.255.255.0",
            "outside_ip_gateway": "10.10.3.1"
        }
    ]

    return jsonify(sample_data)

# Kullanılan IP'leri veritabanından almak için bir fonksiyon ekle (örnek)
def get_used_ips_for_subnet(subnet):
    """
    subnet: "10.26.1.0/24" gibi CIDR stringi
    return: Kullanılan IP'lerin string listesi
    """
    # TODO: Kendi veritabanı sorgunu buraya yazabilirsin.
    # Basit örnek: sadece test amaçlı, boş liste dönüyor.
    return []

# CIDR'den boş IP listesini döndürür
@app.route('/find_ips')
@login_required
def find_ips():
    cidr = request.args.get('cidr')
    if not cidr:
        return jsonify({'error': 'CIDR parametresi eksik'}), 400

    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except Exception as e:
        return jsonify({'error': f'Geçersiz CIDR formatı: {e}'}), 400

    used_ips = set(get_used_ips_for_subnet(cidr))  # Burada kendi fonksiyonunu kullanabilirsin!
    empty_ips = [str(ip) for ip in net.hosts() if str(ip) not in used_ips]
    return jsonify(empty_ips[:15])  # ilk 15 boş IP'yi döndür
if __name__ == "__main__":
    app.run(debug=True)
