FROM python:3.9-alpine

WORKDIR /app

ADD ./common/example/requirements.txt /app/requirements.txt
RUN pip install chalice==1.27.1 boto3==1.34.2
RUN pip install -r requirements.txt

CMD [ "/bin/sh" ]
