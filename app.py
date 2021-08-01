from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import requests
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
    email = db.Column(db.String(100), unique=True)
    mobile_number = db.Column(db.Integer)
    amount = db.Column(db.Float)
    payment_date = db.Column(db.DateTime, nullable=False)  # Example 11/21

    def __init__(self, email, mobile_number, amount):
        self.email = email
        self.mobile_number = mobile_number
        self.amount = amount
        self.payment_date = datetime.now()


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
        fields = ('id', 'email', 'mobile_number',
                  'amount', 'payment_date')


# Init Schema
payment_schema = PaymentSchema()
payment_schema = PaymentSchema(many=True)


"""
API Routes Endpoints
"""
# Make a payment
@app.route('/transactions', methods=['POST'])
def make_payment():
    email = request.json['email']
    mobile_number = request.json['mobile_number']
    amount = request.json['amount']
    access_token = "sk_test_0b1400c14af0802885d23b0b198b2b0c015f74de"
    my_headers = {'Authorization' : f'Bearer {access_token}'}
    payment_data = {
        "amount": amount, 
        "email": email,
        "currency": "GHS",
        "mobile_money": {
            "phone" : mobile_number,
            "provider" : "MTN"
        }
    }
    response = requests.post('https://api.paystack.co/charge', headers=my_headers, data = payment_data)

    return response
    # new_transaction = Payment(email, mobile_number, amount )
    # db.session.add(new_transaction)
    # db.session.commit()

    # return payment_schema.jsonify(new_transaction)

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

# Test get request
@app.route('/test', methods=['GET'])
def get_test():
    return "Hello"

"""
Server to run the app
"""
# Server
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
