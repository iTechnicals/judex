# To avoid forkbombs, run with --ulimit nproc=20:20 or similar.

FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN apt-get update
RUN apt install sudo

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]