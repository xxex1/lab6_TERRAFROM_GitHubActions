from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DB_FILE = "pawnshop_data.json"


class PawnItem:
    def __init__(self, item_id, title, owner, loan_amount, status="in_storage"):
        self.item_id = item_id
        self.title = title
        self.owner = owner
        self.loan_amount = loan_amount
        self.status = status

    def to_dict(self):
        return self.__dict__


def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [PawnItem(**d) for d in data]
    return []


def save_data(items):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump([i.to_dict() for i in items], f, ensure_ascii=False, indent=4)


@app.route("/")
def index():
    items = load_data()
    return render_template("index.html", items=items)


@app.route("/add", methods=["POST"])
def add_item():
    items = load_data()
    new_item = PawnItem(
        item_id=len(items) + 1,
        title=request.form["title"],
        owner=request.form["owner"],
        loan_amount=float(request.form["loan_amount"]),
        status="in_storage"
    )
    items.append(new_item)
    save_data(items)
    return redirect(url_for("index"))


@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    items = [i for i in load_data() if i.item_id != item_id]
    save_data(items)
    return redirect(url_for("index"))


@app.route("/update/<int:item_id>", methods=["POST"])
def update_status(item_id):
    items = load_data()
    for i in items:
        if i.item_id == item_id:
            i.status = request.form["status"]
    save_data(items)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
