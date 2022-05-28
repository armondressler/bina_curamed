FROM python:3.10

RUN apt-get update -y && \
    apt-get upgrade -y

COPY ./requirements.txt /requirements.txt
RUN /usr/local/bin/python -m pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./app /app

RUN groupadd -g 1000 uvicorn && \
    useradd -m -u 1000 -g uvicorn uvicorn

WORKDIR /app

EXPOSE 8080
	
#CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "main:app"]
CMD ["python3", "main.py"]
