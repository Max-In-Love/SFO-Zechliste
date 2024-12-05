from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialisieren der Flask-App und SQLAlchemy-Datenbank
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'  # Ein geheimer Schlüssel für die Sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if __name__ == "__main__":
    # Hole den PORT aus der Umgebungsvariable, falls gesetzt, oder benutze 5000 als Standardport
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)
    
db = SQLAlchemy(app)

# Datenbankmodell für Benutzer und Bestellungen
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    drink = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    member = db.relationship('Member', backref=db.backref('orders', lazy=True))

# Startseite
@app.route('/')
def home():
    return render_template('index.html')

# Anmelde-Seite
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Member.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('order'))
        else:
            return "Anmeldung fehlgeschlagen. Bitte versuche es erneut."
    return render_template('login.html')

# Bestellseite
@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        drink = request.form['drink']
        price = 0
        if drink == 'Bier' or drink == 'Softgetränk':
            price = 1.50
        elif drink == 'Wasser':
            price = 1.00

        order = Order(member_id=session['user_id'], drink=drink, price=price)
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('order'))

    drinks = ['Bier', 'Softgetränk', 'Wasser']
    return render_template('order.html', drinks=drinks)

# Übersicht der Bestellungen und zu zahlender Betrag
@app.route('/summary')
def summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    orders = Order.query.filter_by(member_id=session['user_id']).all()
    total_amount = sum(order.price for order in orders)
    return render_template('summary.html', orders=orders, total_amount=total_amount)

# Administratorseite für Barzahlung
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        paid_amount = request.form['paid_amount']
        if paid_amount:
            # Der Administrator kann den zu zahlenden Betrag als bar bezahlt markieren
            # Hier könnte die Logik zur Abwicklung der Barzahlung ergänzt werden.
            return "Zahlung erfolgreich abgebucht"
    members = Member.query.all()
    return render_template('admin.html', members=members)

# Abmelden
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Erstellt die Tabellen bei jedem Start, wenn sie nicht existieren.
    app.run(debug=True)

