# app/models.py
from app import db
from sqlalchemy.dialects.mysql import ENUM

class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    nomor_hp = db.Column(db.String(20), nullable=False)
    tipe_aplikasi = db.Column(db.String(50), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    status = db.Column(ENUM('baru', 'diproses', 'selesai', 'ditolak', name='status'), default='baru', nullable=False)
    tanggal = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    bukti_dp = db.Column(db.String(255), nullable=True)
    dp_nominal = db.Column(db.Integer, nullable=True)
    dp_terbayar = db.Column(db.Boolean, default=False)
    
# Access to table users
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    jenis_kelamin = db.Column(db.String(255), nullable=False)
    usia = db.Column(db.String(255), nullable=False)
    foto = db.Column(db.String(255), nullable=False)
    nomor_hp = db.Column(db.String(255), nullable=False)
    level = db.Column(ENUM('admin', 'user', name='user_level'), nullable=False)
    reset_token = db.Column(db.String(255), nullable=True, default="")
    token_exp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
