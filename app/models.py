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
