from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import uuid 
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
import datetime
from functools import wraps

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

class Questionary(db.Model):
	__tablename__='questionary'
	id=db.Column(db.Integer,primary_key=True)
	user_public_id=db.Column(db.String(50))
	quest_ans=db.Column(JSON)
	questionary_solved=db.relationship('Solved_questionary',backref='questionary')

class Solved_questionary(db.Model):
	__tablename__='solved_questionary'
	id=db.Column(db.Integer,primary_key=True)
	questionary_id=db.Column(db.Integer,db.ForeignKey('questionary.id'))
	answers=db.Column(JSON)
	datetime=db.Column(db.DateTime)	

def token_required(f):
	@wraps(f)
	def decorated(*args,**kwargs):
		token=None

		if 'x-access-token' in request.headers:
			token=request.headers['x-access-token']

		if not token:
			return jsonify({'message':'Token invalido'}),401

		try:
			data= jwt.decode(token,app.config['SECRET_KEY'])
			current_user=User.query.filter_by(public_id=data['public_id']).first()
		except:
			return ({'message':'Token invalido'}),401

		return f(current_user,*args,**kwargs)	

	return decorated

@app.route('/post/encuestas/<public_id>',methods=['POST'])
@token_required
def create_questionary(current_user,public_id):

	data=request.get_json()
	
	for data_quest in data['questionary']:
		cantidad_respuestas=len(data_quest['answer'])
		if cantidad_respuestas>4 or cantidad_respuestas<1:
			return jsonify({'message':'Cantidad de respuestas invalida'}) 


	new_questionary=Questionary(user_public_id=public_id,quest_ans=data)
	db.session.add(new_questionary)
	db.session.commit()

	return jsonify({'message':'Nuevo cuestionario creado'})

@app.route('/get/encuestas/<public_id>',methods=['GET'])
@token_required
def get_questionaries(current_user,public_id):

	if not current_user.admin: 
		return jsonify({'message':'No se puede realizar esta funcion sin permisos'})

	questionaries=Questionary.query.all()
	output= []

	for questionary in questionaries:
		questionary_data={}
		questionary_data['user_public_id']=questionary.user_public_id
		questionary_data['quest_ans']=questionary.quest_ans
		output.append(questionary_data)

	return jsonify({'questionaries':output})

@app.route('/post/encuesta',methods=['POST'])
def solve_questionary():

	data=request.get_json()
	questionary_id=data['questionary_id']
	questionary_data=data['questionary']
	questionary=Questionary.query.filter_by(id=questionary_id).first()
	output=[]


	for quest_ans_data in questionary_data:
		for quest_ans in questionary.quest_ans["questionary"]:
			if quest_ans['question']==quest_ans_data['question']:
				solved_questionary={}
				answer=quest_ans_data['answer']
				qty_answer=len(quest_ans['answer'])
				if  answer<1 or answer>qty_answer:
					return jsonify({'message':'Respuesta invalida'})

				solved_questionary['question']=quest_ans['question']
				solved_questionary['answer']=answer
				output.append(solved_questionary)

	
	new_solved_questionary=Solved_questionary(questionary_id=questionary_id,answers=output,datetime=datetime.datetime.now())
	db.session.add(new_solved_questionary)
	db.session.commit()

	return jsonify({'message':'Encuesta completa'})

@app.route('/get/encuestas_resueltas',methods=['GET'])
@token_required
def get_solved_questioaries(current_user):

	if not current_user.admin: #funcion?
		return jsonify({'message':'No se puede realizar esta funcion sin permisos'})

	solved_questionaries=Solved_questionary.query.all()
	output= []

	for questionary in solved_questionaries:
		questionary_data={}
		questionary_data['questionary_id']=questionary.questionary_id
		questionary_data['answers']=questionary.answers
		questionary_data['datetime']=questionary.datetime
		output.append(questionary_data)

	return jsonify({'solved_questionaries':output})

@app.route('/user',methods=['POST'])
@token_required
def create_user(current_user):

	data=request.get_json()
	hashed_password=generate_password_hash(data['password'],method='sha256')
	new_user=User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password,admin=False)
	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message':'Nuevo usuario creado'})


@app.route('/user',methods=['GET'])
@token_required	
def get_all_users(current_user):

	if not current_user.admin:
		return jsonify({'message':'No se puede realizar esta funcion sin permisos'})

	users=User.query.all()
	output= []

	for user in users:
		user_data={} 
		user_data['public_id']=user.public_id
		user_data['name']=user.name
		user_data['password']=user.password
		user_data['admin']=user.admin
		output.append(user_data)

	return jsonify({'users':output})

@app.route('/user/<public_id>',methods=['GET'])
@token_required	
def get_one_user(current_user,public_id):

	if not current_user.admin:
		return jsonify({'message':'No se puede realizar esta funcion sin permisos'})

	user=User.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message': 'Usuario no encontrado'})

	user_data={}
	user_data['public_id']=user.public_id
	user_data['name']=user.name
	user_data['password']=user.password
	user_data['admin']=user.admin

	return jsonify({'user':user_data})

@app.route('/user/<public_id>',methods=['PUT'])
@token_required	
def promote_user(current_user,public_id):

	if not current_user.admin:
		return jsonify({'message':'No se puede realizar esta funcion sin permisos'})

	user=User.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message': 'Usuario no encontrado'})

	user.admin=True
	db.session.commit()

	return jsonify({'message':'Usuario promovido'})

@app.route('/user/<public_id>',methods=['DELETE'])
@token_required	
def delete_user(current_user,public_id):

	if not current_user.admin:
		return jsonify({'message':'No se puede realizar esta funcion sin permisos'})

	user=User.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message': 'Usuario no encontrado'})

	db.session.delete(user)
	db.session.commit()

	return jsonify({'message':'Usuario eliminado'})

@app.route('/login',methods=['GET'])
def login():
	auth=request.authorization

	if not auth or not auth.username or not auth.password:
		return make_response('Could not verify',401,{'WWW-Authenticate':'Basic realm="Login required'})

	user=User.query.filter_by(name=auth.username).first()

	if not user:
		return make_response('No se encontro el usuario')

	if check_password_hash(user.password,auth.password):
		token=jwt.encode({'public_id':user.public_id,'exp': datetime.datetime.utcnow()+ datetime.timedelta(minutes=60)},app.config['SECRET_KEY'])
		return jsonify({'token':token.decode('UTF-8')})
	return make_response('Could not verify',401,{'WWW-Authenticate':'Basic realm="Login required"'})

if __name__ == '__main__':
	app.run(debug=True)
