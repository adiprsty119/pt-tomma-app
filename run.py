from flask import Flask, request, render_template, request as flask_request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app, db
from app.models import Request, Users
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
import random
import logging
from markupsafe import escape
import os
import re
from dotenv import load_dotenv
load_dotenv()

app = create_app()

# Configure Flask-Mail OTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'adip98816@gmail.com'
app.config['MAIL_PASSWORD'] = 'aiacumtbxgiyssuc'
mail = Mail(app)

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
            return redirect(url_for('dashboard'))
    return render_template('login.html', message=message)

# Endpoint login with Google
@app.route('/login/google/', methods=['GET', 'POST'])
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback/')
def google_callback():
    token = google.authorize_access_token()
    resp = google.get('userinfo')  # ambil data user
    user_info = resp.json()

    # Simpan ke session atau database
    session['user'] = {
        'name': user_info['name'],
        'email': user_info['email'],
        'picture': user_info['picture']
    }
    flash(f"Login berhasil! Selamat datang", "success")
    return redirect(url_for('dashboard'))

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
