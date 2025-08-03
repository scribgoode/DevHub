FROM python:3.10.11
ENV PYTHONBUFFERED=1
ENV PORT=8080
WORKDIR /projectpals
#creates directory in container
COPY . /projectpals/
#copies current directory where file is located to the container directory
RUN pip install --upgrade pip
RUN pip install -r requirementsforlinuxdocker.txt

RUN python manage.py collectstatic --noinput

CMD gunicorn devhub.asgi:application --bind 0.0.0.0:"${PORT}" --worker-class uvicorn.workers.UvicornWorker --workers 3 --timeout 120
#needed to change the first name to the name of the project that has the setting file in it

EXPOSE ${PORT}