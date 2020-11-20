import datetime
from sqlalchemy.dialects.postgresql import JSON
from encuesta_app import db


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
	@classmethod
	def eliminar_expirado(cls):
		expiration_time = 15
		limit = datetime.datetime.now() - datetime.timedelta(minutes=expiration_time)
		cls.query.filter(cls.datetime <= limit).delete()
		db.session.commit()
	
	id=db.Column(db.Integer,primary_key=True)
	questionary_id=db.Column(db.Integer,db.ForeignKey('questionary.id'))
	answers=db.Column(JSON)
	datetime=db.Column(db.DateTime)