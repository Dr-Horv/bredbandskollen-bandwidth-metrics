FROM ubuntu

RUN mkdir /opt/log
COPY  ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN apt update && apt -y install pip
RUN pip install -r requirements.txt

COPY . /app

CMD [ "python3",  "bandwidth.py" ]
