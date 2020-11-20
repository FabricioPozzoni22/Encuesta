from encuesta_app import app
from encuesta_app import scheduler
from encuesta_app.routes import eliminar_encuestas_expiradas


if __name__ == '__main__':
	scheduler.add_job(id='Scheduled task',func=eliminar_encuestas_expiradas, trigger='interval',seconds=5)
	scheduler.start()
	app.run(host="0.0.0.0",port=5000,debug=True)
