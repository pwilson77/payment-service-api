from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


"""
App configurations
"""
# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init database
db = SQLAlchemy(app)

# Initilize marshmallow
ma = Marshmallow(app)


"""
Database models
"""
# Payment Model
class Payment(db.Model):
    # Say payment with a credit card
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    card_number = db.Column(db.Integer)
    cvv_number = db.Column(db.Integer)
    expiration_date = db.Column(db.String(5))  # Example 11/21

    def __init__(self, username, card_number, cvv_number, expiration_date):
        self.username = username
        self.card_number = card_number
        self.cvv_number = cvv_number
        self.expiration_date = expiration_date


"""
Create tables for the database
"""
# Create tables
db.drop_all()
db.create_all()


"""
Database schema for the models
"""
# Payment Schema
class PaymentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'card_number',
                  'cvv_number', 'expiration_date')


# Init Schema
payment_schema = PaymentSchema()
payment_schema = PaymentSchema(many=True)


"""
API Routes Endpoints
"""
# Make a payment
@app.route('/transactions', methods=['POST'])
def make_payment():
    username = request.json['username']
    card_number = request.json['card_number']
    cvv_number = request.json['cvv_number']
    expiration_date = request.json['expiration_date']

    new_transaction = Payment(username, card_number,
                              cvv_number, expiration_date)
    db.session.add(new_transaction)
    db.session.commit()

    return payment_schema.jsonify(new_transaction)

# Get all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    all_transactions = Payment.query.all()
    result = payment_schema.dump(all_transactions)
    return jsonify(result)

# Get single payment (Not part of the task)
@app.route('/transactions/<id>', methods=['GET'])
def get_transaction(id):
    transaction = Payment.query.get(id)
    return payment_schema.jsonify(transaction)

# Get payment balance
@app.route('/transaction/balance/<id>', methods=['GET'])
def get_balance(id):
    pass


"""
Server to run the app
"""
# Server
if __name__ == '__main__':
    app.run(debug=True)
