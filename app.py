from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import uuid 
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
import datetime

app=Flask(__name__)

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:''@localhost/encuesta'

db=SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'users'
	id= db.Column(db.Integer,primary_key=True)
	public_id=db.Column(db.String(50),unique=True)
	name=db.Column(db.String(50))
	password=db.Column(db.String(80))
	admin=db.Column(db.Boolean)


@app.route('/user',methods=['POST'])
def create_user():
	data=request.get_json()
	hashed_password=generate_password_hash(data['password'],method='sha256')
	new_user=User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password,admin=False)
	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message':'Nuevo usuario creado'})

if __name__ == '__main__':
	app.run(debug=True)
