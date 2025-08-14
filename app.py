from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Database Configuration ---
# Replace with your actual MS SQL Server details
# Make sure to URL-encode the password if it contains special characters
# For example, 'mypassword#123' should be 'mypassword%23123'
USERNAME = 'your_username'
PASSWORD = 'your_password'
SERVER = 'your_server'
DATABASE = 'your_database'
DRIVER = 'ODBC Driver 18 for SQL Server' # Or your specific driver

# Connection String
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---
class PN(db.Model):
    __tablename__ = 'PN'
    id = db.Column(db.Integer, primary_key=True)
    partnumber = db.Column(db.String(50), nullable=False)
    note = db.Column(db.String(200))

    pins = db.relationship('Pin', backref='pn', lazy=True, cascade="all, delete-orphan")

class Pin(db.Model):
    __tablename__ = 'pin'
    id = db.Column(db.Integer, primary_key=True)
    pn_id = db.Column(db.Integer, db.ForeignKey('PN.id'), nullable=False)
    pin = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50))
    base_pin = db.Column(db.String(50))
    note = db.Column(db.String(200))


@app.route('/')
def index():
    pns = PN.query.all()
    return render_template('index.html', pns=pns)

# --- PN Routes ---
@app.route('/pn/add', methods=['POST'])
def add_pn():
    partnumber = request.form.get('partnumber')
    note = request.form.get('note')
    new_pn = PN(partnumber=partnumber, note=note)
    db.session.add(new_pn)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/pn/update/<int:pn_id>', methods=['POST'])
def update_pn(pn_id):
    pn = PN.query.get_or_404(pn_id)
    pn.partnumber = request.form.get('partnumber')
    pn.note = request.form.get('note')
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/pn/delete/<int:pn_id>', methods=['POST'])
def delete_pn(pn_id):
    pn = PN.query.get_or_404(pn_id)
    db.session.delete(pn)
    db.session.commit()
    return redirect(url_for('index'))

# --- Pin Routes ---
@app.route('/pins/<int:pn_id>')
def get_pins(pn_id):
    pins = Pin.query.filter_by(pn_id=pn_id).all()
    pin_list = []
    for pin in pins:
        pin_list.append({
            'id': pin.id,
            'pn_id': pin.pn_id,
            'pin': pin.pin,
            'name': pin.name,
            'base_pin': pin.base_pin,
            'note': pin.note
        })
    return jsonify({'pins': pin_list})

@app.route('/pin/add', methods=['POST'])
def add_pin():
    pn_id = request.form.get('pn_id')
    pin = request.form.get('pin')
    name = request.form.get('name')
    base_pin = request.form.get('base_pin')
    note = request.form.get('note')
    new_pin = Pin(pn_id=pn_id, pin=pin, name=name, base_pin=base_pin, note=note)
    db.session.add(new_pin)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/pin/update/<int:pin_id>', methods=['POST'])
def update_pin(pin_id):
    pin = Pin.query.get_or_404(pin_id)
    pin.pin = request.form.get('pin')
    pin.name = request.form.get('name')
    pin.base_pin = request.form.get('base_pin')
    pin.note = request.form.get('note')
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/pin/delete/<int:pin_id>', methods=['POST'])
def delete_pin(pin_id):
    pin = Pin.query.get_or_404(pin_id)
    db.session.delete(pin)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
