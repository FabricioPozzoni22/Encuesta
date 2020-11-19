from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:''@localhost/encuesta'

db=SQLAlchemy(app)

if __name__ == '__main__':
	app.run(debug=True)
