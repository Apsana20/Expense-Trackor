from flask import Flask, render_template, request, redirect
from database import db, Expense
from datetime import datetime
budget = 0
import pandas as pd
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():

    expenses = Expense.query.order_by(Expense.id.desc()).all()

    total = sum(expense.amount for expense in expenses)
    remaining = budget - total

    count = len(expenses)

    current_date = datetime.now().strftime("%d-%m-%Y")
    food = Expense.query.filter_by(category="Food").count()
    travel = Expense.query.filter_by(category="Travel").count()
    shopping = Expense.query.filter_by(category="Shopping").count()
    bills = Expense.query.filter_by(category="Bills").count()
    return render_template(
        'dashboard.html',
         expenses=expenses,
         total=total,
         count=count,
         current_date=current_date,
         food=food,
         travel=travel,
         shopping=shopping,
         bills=bills,
         budget=budget,
         remaining=remaining
    )

@app.route('/add', methods=['GET', 'POST'])
def add_expense():

    if request.method == 'POST':

        title = request.form['title']
        amount = float(request.form['amount'])
        category = request.form['category']

        expense = Expense(
            title=title,
            amount=amount,
            category=category,
            date=datetime.now().strftime("%d-%m-%Y")
        )

        db.session.add(expense)
        db.session.commit()

        return redirect('/')

    return render_template('add_expense.html')


@app.route('/delete/<int:id>')
def delete(id):

    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)
    db.session.commit()

    return redirect('/')
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':

        expense.title = request.form['title']
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']

        db.session.commit()

        return redirect('/')

    return render_template(
        'edit_expense.html',
        expense=expense
    )

@app.route('/search')
def search():

    keyword = request.args.get('keyword')

    expenses = Expense.query.filter(
        Expense.title.contains(keyword)
    ).all()

    total = sum(e.amount for e in expenses)

    count = len(expenses)

    current_date = datetime.now().strftime("%d-%m-%Y")

    food = Expense.query.filter_by(category="Food").count()
    travel = Expense.query.filter_by(category="Travel").count()
    shopping = Expense.query.filter_by(category="Shopping").count()
    bills = Expense.query.filter_by(category="Bills").count()

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total,
        count=count,
        current_date=current_date,
        food=food,
        travel=travel,
        shopping=shopping,
        bills=bills
    )
@app.route('/filter/<category>')
def filter(category):

    expenses = Expense.query.filter_by(category=category).all()

    total = sum(e.amount for e in expenses)

    count = len(expenses)

    current_date = datetime.now().strftime("%d-%m-%Y")

    food = Expense.query.filter_by(category="Food").count()
    travel = Expense.query.filter_by(category="Travel").count()
    shopping = Expense.query.filter_by(category="Shopping").count()
    bills = Expense.query.filter_by(category="Bills").count()

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total,
        count=count,
        current_date=current_date,
        food=food,
        travel=travel,
        shopping=shopping,
        bills=bills
    )
@app.route('/budget', methods=['POST'])
def budget_route():
    global budget
    budget = float(request.form['budget'])
    return redirect('/')
@app.route('/export')
def export():

    expenses = Expense.query.all()

    data = []

    for e in expenses:
        data.append({
            "Title": e.title,
            "Amount": e.amount,
            "Category": e.category,
            "Date": e.date
        })

    df = pd.DataFrame(data)

    file_name = "Expense_Report.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(file_name, as_attachment=True)
@app.route('/pdf')
def pdf():

    expenses = Expense.query.all()

    pdf = SimpleDocTemplate("Expense_Report.pdf")

    data = [["Title", "Amount", "Category", "Date"]]

    for e in expenses:
        data.append([
            e.title,
            str(e.amount),
            e.category,
            e.date
        ])

    table = Table(data)

    pdf.build([table])

    return send_file(
        "Expense_Report.pdf",
        as_attachment=True
    )
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)