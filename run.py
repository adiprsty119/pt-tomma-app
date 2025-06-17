from flask import Flask, request, render_template, request as flask_request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app, db
from app.models import Request, Users
from flask_mail import Mail, Message
from twilio.rest import Client
from authlib.integrations.flask_client import OAuth
from markupsafe import escape
from datetime import datetime, timedelta
import random, string
import logging
import secrets
import time
import os
import re
from dotenv import load_dotenv

app = create_app()

# Configure Flask-Mail OTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'adip98816@gmail.com'
app.config['MAIL_PASSWORD'] = 'aiacumtbxgiyssuc'
mail = Mail(app)

# Whatsapp OTP
load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

def send_whatsapp_code(phone, code):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    message_body = f"Kode verifikasi Anda adalah: *{code}*.\nJangan bagikan kode ini kepada siapa pun."
    try:
        message = client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{phone}'
        )
        print("Pesan berhasil dikirim:", message.sid)
    except Exception as e:
        print("Gagal mengirim pesan:", e)

def normalize_phone_number(phone):
    phone = phone.strip()
    if phone.startswith('0'):
        return '+62' + phone[1:]
    elif phone.startswith('+62'):
        return phone
    elif phone.startswith('62'):
        return '+' + phone
    else:
        return phone
    
def generate_username(email):
    name_part = email.split('@')[0]
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{name_part}_{random_suffix}"

# Google OAuth Config
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

# Fungsi untuk mengecek keberadaan username, nomor hp, email dan password serta untuk menghasilkan kode verifikasi 6 digit
def check_username_in_db(username):
    user = Users.query.filter_by(username=username).first()
    return user is not None

def check_phone_in_db(phone):
    user = Users.query.filter_by(nomor_hp=phone).first()
    return user is not None


def check_email_in_db(email):
    user = Users.query.filter_by(email=email).first()
    return user is not None

def check_password_in_db(username, password):
    user = Users.query.filter_by(username=username).first()
    if user:
        return check_password_hash(user.password, password)
    return False

def generate_verification_code():
    return random.randint(100000, 999999)

# Endpoint login
@app.route('/login/', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Query user dari database
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("Username salah!", "danger")
        elif not check_password_hash(user.password, password):
            flash("Password salah!", "danger")
        else:
            session['username'] = username
            safe_username = escape(username)
            flash(f"Login berhasil! Selamat datang, {safe_username}.", "success")
            return redirect(url_for('index'))
    return render_template('login.html', message=message)

# Endpoint login with Google
@app.route('/login/google/', methods=['GET', 'POST'])
def login_google():
    redirect_uri = url_for('login_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

# Endpoint Callback Login With Google
@app.route('/login/google/callback/')
def login_google_callback():
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')  # ambil data user dari Google
        resp.raise_for_status()  # pastikan response OK (status code 200)
        user_info = resp.json()
    except Exception as e:
        print(f"Google login error: {e}") 
        flash("Gagal login dengan Google. Silakan coba lagi.", "danger")
        return redirect(url_for('login'))
    
    # Proses lanjut jika data user berhasil diambil
    email = user_info['email']
    user = Users.query.filter_by(email=email).first()
    if user:
        # Simpan ke session atau database
        session['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nama_lengkap': user.nama_lengkap,
            'foto': user.foto,
            'level': user.level
        }
        flash(f"Login berhasil! Selamat datang", "success")
        return redirect(url_for('index'))
    else:
        # Jika belum ada, arahkan ke konfirmasi registrasi
        session['pending_user'] = user_info
        flash("Akun belum terdaftar. Lanjutkan untuk registrasi?", "warning")
        return redirect(url_for('confirm_register'))

# Endpoint Fisrt Confirm Register With Google
@app.route('/confirm-register/')
def confirm_register():
    user_info = session.get('pending_user')
    if not user_info:
        flash("Data user tidak ditemukan. Silakan login ulang.", "danger")
        return redirect(url_for('login'))
    return render_template("confirm_register.html", user=user_info)

# Endpoint Second Confirm Register With Google
@app.route('/confirm-register', methods=['POST'])
def do_register():
    user_info = session.get('pending_user')
    if not user_info:
        flash("Data user tidak ditemukan. Silakan login ulang.", "danger")
        return redirect(url_for('login'))
    email = user_info['email']
    username = generate_username(email)
    
    # Simpan ke database
    new_user = Users(
            username=username,
            password=generate_password_hash(secrets.token_urlsafe(12), method='pbkdf2:sha256'),
            nama_lengkap=user_info['name'],
            email=user_info['email'],
            jenis_kelamin=None,
            usia=None,
            foto=user_info['picture'],
            nomor_hp=None,
            level='user',
            reset_token=None,
            token_exp=None
    )
    if Users.query.filter_by(email=email).first():
        flash("Email sudah digunakan. Silakan login.", "warning")
        return redirect(url_for('login'))
    db.session.add(new_user)
    db.session.commit()

    # Login langsung setelah registrasi
    session['user'] = {
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email,
        'nama_lengkap': new_user.nama_lengkap,
        'foto': new_user.foto,
        'level': new_user.level
    }
    flash("Registrasi otomatis berhasil! Anda sudah login.", "success")
    return redirect(url_for('index'))

# Endpoint register
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        level = request.form['level']
        
        # Validasi password dengan regex
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_pattern, password):
            flash("Password must have at least 8 characters, including uppercase, lowercase, number, and special character.", "danger")
            return redirect(url_for('register'))
        # Validasi apakah password dan confirmPassword cocok
        if password != confirm_password:
            flash("Password and Confirm Password must match!", "danger")
            return redirect(url_for('register'))
        # Validasi level user
        valid_levels = ['admin', 'user']
        if level not in valid_levels:
            flash("Invalid level selected. Please try again.", "danger")
            return redirect(url_for('register'))
        # Cek keberadaan username dan email di database
        user_exists = check_username_in_db(username)
        email_exists = check_email_in_db(email)
        if not user_exists and not email_exists:
           # Enkripsi password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16) 
            # Masukkan data ke database
            try:
                new_user = Users(
                    username=username,
                    password=hashed_password,
                    nama_lengkap=full_name,
                    email=email,
                    level=level
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful! You can now login.", "success")
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error during registration: {e}")
                flash("An error occurred during registration.Please try again.", "danger")
                print(e)
        elif user_exists and email_exists:
            flash("Usernam dan email Anda telah terdaftar.", "danger")
        elif user_exists:
            flash("Username Anda telah terdaftar.", "danger")
        elif email_exists:
            flash("Email Anda telah terdaftar.", "danger")
        return redirect(url_for('register'))
    return render_template('register.html')

# Endpoint Register With Google
@app.route('/register/google/', methods=['GET', 'POST'])
def register_google():
    redirect_uri = url_for('register_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

# Endpoint Callback Register With Google
@app.route('/register/google/callback/')
def register_google_callback():
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        resp.raise_for_status() 
        user_info = resp.json()
    except Exception as e:
        print(f"Google registrasi error: {e}") 
        flash("Gagal melakukan registrasi dengan Google. Silakan coba lagi.", "danger")
        return redirect(url_for('register'))
    
    email = user_info['email']
    username = generate_username(email)
    
    # Simpan ke database
    new_user = Users(
            username=username,
            password=generate_password_hash(secrets.token_urlsafe(12), method='pbkdf2:sha256'),
            nama_lengkap=user_info['name'],
            email=user_info['email'],
            jenis_kelamin=None,
            usia=None,
            foto=user_info['picture'],
            nomor_hp=None,
            level='user',
            reset_token=None,
            token_exp=None
    )
    if Users.query.filter_by(email=email).first():
        flash("Email sudah digunakan. Silakan login.", "warning")
        return redirect(url_for('login'))
    db.session.add(new_user)
    db.session.commit()
    
    # Login langsung setelah registrasi
    session['user'] = {
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email,
        'nama_lengkap': new_user.nama_lengkap,
        'foto': new_user.foto,
        'level': new_user.level
    }
    flash("Registrasi otomatis berhasil! Anda sudah login.", "success")
    return redirect(url_for('index'))

# Endpoint Find Account
@app.route('/find_account/', methods=['GET', 'POST'])
def find_account():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('no-hp')
        # Pastikan username diisi
        if not username:
            flash('Username wajib diisi.', 'danger')
            return redirect(url_for('find_account'))

        # ===== Kondisi 1: Username + Email =====
        if email and not phone:
            # Validasi format email
            email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            if not re.match(email_pattern, email):
                flash('Alamat email tidak valid.', 'danger')
                return redirect(url_for('find_account'))
            user_exists = check_username_in_db(username)
            email_exists = check_email_in_db(email)

            if user_exists and email_exists:
                verification_code = generate_verification_code()
                session['verification_code'] = verification_code
                session['verification_code_expiry'] = time.time() + 180
                session['username'] = username
                # Kirim kode via email
                msg = Message('Verifikasi Akun Anda',
                              sender='adip98816@gmail.com',
                              recipients=[email])
                safe_code = escape(verification_code)
                msg.html = f"""
                <p>Halo,</p>
                <p>Berikut adalah kode verifikasi 6 digit untuk mengakses akun Anda:</p>
                <h2>{safe_code}</h2>
                <p>Atau klik <a href="{url_for('verify_code', _external=True)}" style="color: blue;">link ini</a> untuk melanjutkan.</p>
                """
                mail.send(msg)
                flash(f'Kode verifikasi telah dikirim ke email {escape(email)}', 'success')
                return redirect(url_for('verify_code'))
            elif not user_exists and not email_exists:
                flash('Username dan email tidak ditemukan.', 'danger')
            elif not user_exists:
                flash('Username tidak ditemukan.', 'danger')
            elif not email_exists:
                flash('Email tidak ditemukan.', 'danger')
    
        # ===== Kondisi 2: Username + Nomor HP =====
        elif phone and not email:
            normalized_phone = normalize_phone_number(phone)
            phone_pattern = r'^\+628\d{7,12}$'
            if not re.match(phone_pattern, normalized_phone):
                flash('Format nomor HP tidak valid. Gunakan nomor Indonesia.', 'danger')
                return redirect(url_for('find_account'))
            # Cek keberadaan username dan nomor HP di database
            user_exists = check_username_in_db(username)
            hp_exists = check_phone_in_db(normalized_phone)
            if user_exists and hp_exists:
                verification_code = generate_verification_code()
                session['verification_code'] = verification_code
                session['verification_code_expiry'] = time.time() + 180  # berlaku 3 menit
                session['username'] = username
                session['phone'] = normalized_phone
                send_whatsapp_code(normalized_phone, verification_code)
                flash(f'Kode verifikasi telah dikirim ke nomor WhatsApp {normalized_phone}', 'success')
                return redirect(url_for('verify_code'))
            # Penanganan error spesifik
            if not user_exists and not hp_exists:
                flash('Username dan nomor HP tidak ditemukan.', 'danger')
            elif not user_exists:
                flash('Username tidak ditemukan.', 'danger')
            elif not hp_exists:
                flash('Nomor HP tidak ditemukan.', 'danger')
            return redirect(url_for('find_account'))
        else:
            flash('Harap isi email atau nomor HP.', 'danger')
        return redirect(url_for('find_account'))
    return render_template('find_account.html')

# Endpoint untuk verify_code
@app.route('/verify_code/', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'GET':
        expiry_time = session.get('verification_code_expiry', 0)
        return render_template('verify_code.html', expiry_time=int(expiry_time))
    # Metode untuk memproses data JSON
    expiry_time = session.get('verification_code_expiry', 0)
    data = request.get_json()
    if not data or 'verification_code' not in data:
        return jsonify({'message': 'Verification code is required.'}), 400
    code = data['verification_code']
    if time.time() > expiry_time:
        return jsonify({'message': 'Verification code has expired.'}), 400
    if 'verification_code' in session and session['verification_code'] == int(code):
        # Generate reset token dan set waktu kedaluwarsa
        reset_token = secrets.token_hex(16)
        expiry_time = datetime.now() + timedelta(minutes=10)
        username = session.get('username')
        user = Users.query.filter_by(username=username).first()
        if not user:
            return jsonify({'message': 'User not found.'}), 404
        # Simpan token dan waktu kedaluwarsa di database lalu sertakan URL reset password dengan token
        user.reset_token = reset_token
        user.token_exp = expiry_time
        db.session.commit()
        reset_password_url = escape(url_for('reset_password', token=reset_token, _external=True))
        return jsonify({
            'message': 'Verification successful.',
            'redirect_url': reset_password_url
        }), 200
    else:
        return jsonify({'message': 'Incorrect verification code.'}), 400

# Endpoint Reset Password
@app.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        reset_token = request.args.get('token')
        if not reset_token:
            return jsonify({'error': "Token tidak ditemukan."}), 400
        # Validasi token
        user = Users.query.filter_by(reset_token=reset_token).first()
        if not user or datetime.now() > user.token_exp:
            if user:
                user.reset_token = None
                user.token_exp = None
                db.session.commit()
            return jsonify({'error': "Token tidak valid atau telah kedaluwarsa."}), 400
        # Jika token valid, arahkan ke halaman reset password
        return render_template('reset_password.html', token=escape(reset_token))
    if request.method == 'POST':
        data = request.get_json()
        reset_token = data.get('reset_token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        # Debug input
        print(f"Reset token: {reset_token}, Password baru: {new_password}")
        # Validasi input
        if not reset_token or not new_password or not confirm_password:
            return jsonify({'error': "Semua data harus diisi."}), 400
        # Validasi pola password
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_pattern, new_password):
            return jsonify({'error': "Password harus terdiri dari minimal 8 karakter, termasuk huruf besar, kecil, angka, dan simbol."}), 400
        if new_password != confirm_password:
            return jsonify({'error': "Password dan konfirmasi password tidak cocok."}), 400
        # Validasi token
        user = Users.query.filter_by(reset_token=reset_token).first()
        if not user:
            return jsonify({'error': "Token reset password tidak valid."}), 400
        if datetime.now() > user.token_exp:
            user.reset_token = None
            user.token_exp = None
            db.session.commit()
            return jsonify({'error': "Token reset password telah kedaluwarsa."}), 400
        # Update password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
        user.password = hashed_password
        user.reset_token = None
        user.token_exp = None
        db.session.commit()
        print("Password berhasil diubah.")
        return jsonify({'message': "Password Anda telah berhasil diubah!"}), 200

@app.route("/index/")
def index():
    return render_template("index.html")

@app.route("/request/", methods=["GET", "POST"])
def request_page():   
    if flask_request.method == "POST":
        nama = flask_request.form.get("name")
        email = flask_request.form.get("email")
        nomor_hp = flask_request.form.get("nomor_hp")
        tipe_aplikasi = flask_request.form.get("tipe_aplikasi")
        deskripsi = flask_request.form.get("deskripsi")

        # Validasi wajib isi
        if not all([nama, email, nomor_hp, tipe_aplikasi, deskripsi]):
            flash("Semua field harus diisi!", "danger")
            return redirect(request.url)

        # Validasi email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Email tidak valid!", "danger")
            return redirect(request.url)

        # Normalisasi nomor
        if nomor_hp.startswith("+62"):
            nomor_hp = "0" + nomor_hp[3:]

        # Validasi nomor HP
        hp_regex = r"^(08\d{8,11}|0\d{9,12})$"
        valid_prefixes = {
            "0811", "0812", "0813", "0821", "0822", "0823",
            "0851", "0852", "0853", "0817", "0818", "0819",
            "0857", "0858", "0896", "0897", "0898", "0899",
        }
        
        if not re.match(hp_regex, nomor_hp):
            flash("Nomor HP harus dimulai dengan 08, panjang 10-13 digit!", "danger")
            return redirect(request.url)

        if nomor_hp[:4] not in valid_prefixes:
            flash("Prefix nomor HP tidak dikenal. Periksa kembali nomor Anda.", "danger")
            return redirect(request.url)

        if re.match(r"^(0+|08[0-9]{7}1234|08[0-9]{9}000)$", nomor_hp):
            flash("Nomor HP tampaknya tidak valid!", "danger")
            return redirect(request.url)
        
        # Simpan ke DB jika lolos validasi
        new_request = Request(
            nama=nama,
            email=email,
            nomor_hp=nomor_hp,
            tipe_aplikasi=tipe_aplikasi,
            deskripsi=deskripsi
        )
        db.session.add(new_request)
        db.session.commit()

        flash("Permintaan Anda berhasil dikirim!", "success")
        return redirect(request.url)
    return render_template("request.html")

@app.route("/konfirmasi-dp/<int:request_id>", methods=["GET", "POST"])
def konfirmasi_dp(request_id):
    req = Request.query.get_or_404(request_id)

    if flask_request.method == "POST":
        file = flask_request.files.get("bukti_dp")
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join("static/uploads", filename)
            file.save(filepath)
            req.bukti_dp = filename
            req.dp_terbayar = True
            req.status = "DP Dikonfirmasi"
            db.session.commit()
            flash("Bukti pembayaran DP berhasil dikonfirmasi.", "success")
            return redirect(url_for("request_page"))
        flash("Bukti DP tidak valid!", "danger")

    return render_template("konfirmasi_dp.html", request_data=req)

@app.route("/news/")
def news():
    return render_template("news.html")

@app.route("/portfolio/")
def portfolio():
    return render_template("portfolio.html")

@app.route("/services/")
def services():
    return render_template("services.html")

@app.route("/thankyou/")
def thankyou():
    return render_template("thankyou.html")

if __name__ == "__main__":
    app.run(debug=True)
