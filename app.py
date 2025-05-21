# Web 後台系統：查詢物流狀態 + 顯示未取貨訂單 + 支援上傳 CSV

from flask import Flask, render_template_string, request, redirect
from datetime import datetime, timedelta
import os, json, csv
from io import TextIOWrapper

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './'

LOG_FILE = "sent_log.json"
ORDERS_FILE = "orders.csv"

# 假查詢邏輯（可替換為實際爬蟲/API）
def query_status(tracking_code):
    return "已到店未取", datetime.today() - timedelta(days=4)

def send_email(to, name, order_code):
    print(f"寄送提醒信至 {to}（{name}），代碼：{order_code}")

def load_sent_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_sent_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

@app.route("/", methods=["GET"])
def index():
    orders = load_orders()
    sent_log = load_sent_log()
    notify_list = []

    for order in orders:
        order_key = order["訂單編號"] + "_" + order["寄件代碼"]
        if order_key in sent_log:
            continue

        status, arrive_date = query_status(order["寄件代碼"])
        if arrive_date:
            days = (datetime.today() - arrive_date).days
            if days >= 3 and "未取" in status:
                notify_list.append({
                    **order,
                    "貨態": status,
                    "到店日": arrive_date.strftime("%Y-%m-%d"),
                    "已過天數": days
                })

    return render_template_string("""<h2>未取貨超過3天的訂單提醒列表</h2>
        <form method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" name="csvfile" accept=".csv">
            <button type="submit">上傳訂單資料</button>
        </form>
        <br>
        <table border=1 cellpadding=6>
            <tr><th>訂單編號</th><th>姓名</th><th>Email</th><th>貨態</th><th>到店日</th><th>已過天數</th><th>操作</th></tr>
            {% for o in orders %}
            <tr>
                <td>{{ o["訂單編號"] }}</td>
                <td>{{ o["姓名"] }}</td>
                <td>{{ o["Email"] }}</td>
                <td>{{ o["貨態"] }}</td>
                <td>{{ o["到店日"] }}</td>
                <td>{{ o["已過天數"] }}</td>
                <td>
                    <form method="post" action="/notify">
                        <input type="hidden" name="email" value="{{ o['Email'] }}">
                        <input type="hidden" name="name" value="{{ o['姓名'] }}">
                        <input type="hidden" name="code" value="{{ o['寄件代碼'] }}">
                        <input type="hidden" name="order" value="{{ o['訂單編號'] }}">
                        <button type="submit">寄送提醒</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>""", orders=notify_list)

@app.route("/notify", methods=["POST"])
def notify():
    to = request.form.get("email")
    name = request.form.get("name")
    code = request.form.get("code")
    order_id = request.form.get("order")
    send_email(to, name, code)

    sent_log = load_sent_log()
    key = order_id + "_" + code
    sent_log[key] = {"email": to, "date": datetime.today().strftime("%Y-%m-%d")}
    save_sent_log(sent_log)

    return f"已寄送提醒信至 {to}"

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("csvfile")
    if file and file.filename.endswith(".csv"):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], ORDERS_FILE)
        file.save(filepath)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
