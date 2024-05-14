FROM python:3.10.5-bullseye

RUN apt-get clean all
RUN apt-get update
RUN apt-get install -y vim

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./backend /app

WORKDIR /app

COPY ./entrypoint.sh /

EXPOSE 8000 8100

ENTRYPOINT ["sh", "/entrypoint.sh"]