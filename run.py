from flask import Flask, render_template

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

@app.route("/index/")
def index():
    return render_template("index.html")

@app.route("/news/")
def news():
    return render_template("news.html")

@app.route("/portfolio/")
def portfolio():
    return render_template("portfolio.html")

@app.route("/request/")
def request_page():
    return render_template("request.html")

@app.route("/services/")
def services():
    return render_template("services.html")

@app.route("/thankyou/")
def thankyou():
    return render_template("thankyou.html")

if __name__ == "__main__":
    app.run(debug=True)
