	FROM python:3.7


	EXPOSE 5000

	WORKDIR /app

	COPY . /app
		
	RUN pip install -r requirements.txt

	CMD python src/run.py