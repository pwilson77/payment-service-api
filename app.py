# from dotenv import load_dotenv
from flask import Flask, json, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import func
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
    # Payment with mobile money (MTN)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    mobile_number = db.Column(db.Integer)
    amount = db.Column(db.Float)
    payment_date = db.Column(db.DateTime, nullable=False)  

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
    access_token = os.environ.get('ACCESS_TOKEN')
    my_headers = {'Authorization' : f'Bearer {access_token}', 'Content-Type': 'application/json'}

    payment_data = {
        "amount": amount * 100,  # amount calculated in pesewas
        "email": email,
        "currency": "GHS",
        "mobile_money": {
            "phone" : mobile_number,
            "provider" : "MTN"
        }
    }
    response = requests.post('https://api.paystack.co/charge', headers=my_headers, json=payment_data)

    # return (response.text, response.status_code, response.headers.items())
    # return (response.text)

    new_transaction = Payment(email, mobile_number, amount)
    db.session.add(new_transaction)
    db.session.commit()

    if(response.status_code == 200):
        return "Payment sucessful, you will receive an invoice in your email!"
    else:
        return "Payment Failed"
    


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
@app.route('/transactions/balance/', methods=['GET'])
def get_balance():
    cursor = db.session.query(func.sum(Payment.amount))
    total_balance = cursor.scalar()
    return jsonify({'Transaction balance': total_balance})

"""
Server to run the app
"""
# Server
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
