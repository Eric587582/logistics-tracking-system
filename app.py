from flask import Flask, render_template_string, request
from datetime import datetime, timedelta

app = Flask(__name__)

orders = [
    {"訂單編號": "2025051500049", "姓名": "Angel", "Email": "aa0970211340@gmail.com", "寄件代碼": "D20516198333", "物流方式": "賣貨便"},
    {"訂單編號": "2025051500050", "姓名": "Kevin", "Email": "kevin@example.com", "寄件代碼": "D20516198399", "物流方式": "賣貨便"}
]

def query_status(tracking_code):
    return "已到店未取", datetime.today() - timedelta(days=4)

def send_email(to, name, order_code):
    print(f"寄送提醒信至 {to}（{name}），代碼：{order_code}")

@app.route("/")
def index():
    notify_list = []
    for order in orders:
        if order["物流方式"] == "賣貨便":
            status, arrive_date = query_status(order["寄件代碼"])
            days = (datetime.today() - arrive_date).days
            if days >= 3 and "未取" in status:
                notify_list.append({
                    **order,
                    "貨態": status,
                    "到店日": arrive_date.strftime("%Y-%m-%d"),
                    "已過天數": days
                })
    return render_template_string("""<h2>未取貨超過3天的訂單提醒列表</h2>
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
    send_email(to, name, code)
    return f"已寄送提醒信至 {to}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
