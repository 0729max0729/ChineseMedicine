from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about/<section>")
def about(section):
    return render_template("about.html", section=section)

@app.route("/products/<category>")
def products(category):
    return render_template("products.html", category=category)

@app.route("/blog/<topic>")
def blog(topic):
    return render_template("blog.html", topic=topic)

@app.route("/contact/<option>")
def contact(option):
    return render_template("contact.html", option=option)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
