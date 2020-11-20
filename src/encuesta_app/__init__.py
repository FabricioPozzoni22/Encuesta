from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from flask_apscheduler import APScheduler


app=Flask(__name__)
scheduler=APScheduler()

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:''@localhost/encuesta'

db=SQLAlchemy(app)

from encuesta_app import routes