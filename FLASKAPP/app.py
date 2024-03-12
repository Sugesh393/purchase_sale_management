from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///purchasesale.db'
db = SQLAlchemy(app)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    cash_balance = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"Company(id='{self.id}', name='{self.name}', cash_balance={self.cash_balance})"
    
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Item(id='{self.id}', name='{self.name}', rate={self.rate})"

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False) #Foreign Key
    company = db.relationship('Company', backref=db.backref('purchases', lazy=True))

    def __repr__(self):
        return f"Purchase(id='{self.id}', company_id='{self.company_id}' , product='{self.product}', quantity={self.quantity}, rate={self.rate}, total_amount={self.total_amount})"

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False) #Foreign Key
    company = db.relationship('Company', backref=db.backref('sales', lazy=True))

    def __repr__(self):
        return f"Sale(id='{self.id}', company_id='{self.company_id}', product='{self.product}', quantity={self.quantity}, rate={self.rate}, total_amount={self.total_amount})"

app.app_context().push()
db.create_all()


@app.route('/')
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form['name']
    rate = float(request.form['rate'])

    new_item = Item(name=name, rate=rate)
    db.session.add(new_item)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/purchase')
def purchase():
    return render_template('purchase.html')

@app.route('/store_purchase', methods=['POST'])
def store_purchase():
    company_name = request.form['company']
    company = Company.query.filter_by(name=company_name).first()
    if not company:
        return jsonify({"error": f"Company '{company_name}' not found"}), 404
    
    product = request.form['product']
    quantity = int(request.form['quantity'])
    rate = float(request.form['rate'])
    total_amount = quantity * rate

    # Update company's cash balance
    company.cash_balance -= total_amount
    db.session.add(company)

    # Here you can store the purchase data in the database
    new_purchase = Purchase(product=product, quantity=quantity, rate=rate, total_amount=total_amount, company=company)
    db.session.add(new_purchase)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/sale')
def sale():
    return render_template('sale.html')

@app.route('/store_sale', methods=['POST'])
def store_sale():
    company_name = request.form['company']
    company = Company.query.filter_by(name=company_name).first()
    if not company:
        return jsonify({"error" : f"Company '{company_name}' not found"}), 404

    product = request.form['product']
    quantity = int(request.form['quantity'])
    rate = float(request.form['rate'])
    total_amount = quantity * rate

    # Update company's cash balance
    company.cash_balance += total_amount
    db.session.add(company)
    
    # Here you can store the sale data in the database
    new_sale = Sale(product=product, quantity=quantity, rate=rate, total_amount=total_amount, company=company)
    db.session.add(new_sale)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)