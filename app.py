from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    products = [
        {"name": "四物湯包", "desc": "補血調經，適合女性日常保養", "img": "siwutang.jpg"},
        {"name": "十全大補湯包", "desc": "滋補強身，提升元氣", "img": "buyao.jpg"},
        {"name": "枇杷膏", "desc": "潤喉止咳，清涼解熱", "img": "pipagao.jpg"},
        {"name": "養生花茶包", "desc": "嚴選枸杞、菊花、紅棗等天然材料", "img": "tea.jpg"},
        {"name": "冬蟲夏草（禮盒）", "desc": "名貴滋補首選，送禮自用兩相宜", "img": "dongchongxiacao.jpg"}
    ]
    return render_template("index.html", products=products)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        print(f"新留言：{name} / {email}：{message}")
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
