from flask import Flask, render_template, request as flask_request, redirect, url_for, flash
from app import create_app, db
from app.models import Request

app = create_app()

@app.route("/index/")
def index():
    return render_template("index.html")


@app.route("/news/")
def news():
    return render_template("news.html")

@app.route("/portfolio/")
def portfolio():
    return render_template("portfolio.html")

@app.route("/request/", methods=["GET", "POST"])
def request_page():
    if flask_request.method == "POST":
        nama = flask_request.form.get("name")
        email = flask_request.form.get("email")
        nomor_hp = flask_request.form.get("nomor_hp")
        tipe_aplikasi = flask_request.form.get("tipe_aplikasi")
        deskripsi = flask_request.form.get("deskripsi")

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
        return redirect(url_for("request_page"))

    return render_template("request.html")

@app.route("/services/")
def services():
    return render_template("services.html")

@app.route("/thankyou/")
def thankyou():
    return render_template("thankyou.html")

if __name__ == "__main__":
    app.run(debug=True)
