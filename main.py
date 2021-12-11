from datetime import datetime
from flask import Flask , render_template, request, redirect

from flask_sqlalchemy import SQLAlchemy
import json 



with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
#  Intializing the application

app = Flask(__name__)

#database Intializing

if(local_server):
       app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] 
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Customers(db.Model):
    '''sno, name, email, balance, address, phoneno'''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phoneno = db.Column(db.String(20), nullable=False)
    

class Transfers(db.Model):
    '''sno, sender_email, amount, reciever_email, time'''
    sno = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reciever_email = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(6), nullable=False)
    

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/users', methods=['GET'])
def users():
    customers = Customers.query.all()
    return render_template('users.html', customers = customers)

@app.route('/view/<string:sno>', methods=['GET'])
def view(sno):
    customer = Customers.query.filter_by(sno=sno).first()
    return render_template('view.html', customer = customer)

@app.route('/transaction')
def transaction():
    transfers = Transfers.query.all()
    return render_template('transaction.html', transfers=transfers)


@app.route("/view/payment/<string:sno>", methods=['GET','POST'])
def payment(sno):
    customer = Customers.query.filter_by(sno = sno).first
    balance_data = Customers.query.get_or_404(sno)
  
    
    # customer = Customers.query.filter_by(amount=customer.amount).first()
    customers = Customers.query.all()
    user_id = int(sno)-1
    # print(customers[0].sno)
    balance = customers[user_id].balance
    email = customers[user_id].email
    # print(email)
    # currentAmount = customer.amount
    newAmount = 0
    
    
    
    if(request.method=='POST'):
        sender_email = request.form.get('sender_email')
        reciever_email = request.form.get('reciever_email')
        amount = int(request.form.get('amount'))
        # Reciever Address 
        reciever = Customers.query.filter_by(email=reciever_email).first()
        balance1 = reciever.balance
        print(reciever.balance)
        
        if(amount < balance):
            if(sender_email):
                newAmount = balance - amount
                balance_data.balance = newAmount
                db.session.commit()
                
            if(reciever_email):
                reciever.balance +=amount
                db.session.commit()
                
                
            
            transfers = Transfers(sender_email=sender_email,reciever_email=reciever_email,amount=amount,time=datetime.now())
            db.session.add(transfers)
            
            db.session.commit()        
    
        return render_template('payment.html', customer = customer, sno=sno, email=email)
    else:
        return render_template('payment.html', customer = customer, sno=sno, email=email)

            

app.run(debug=True)