FROM python

WORKDIR /home/app
ADD toServer/ /home/app/

RUN pip install flask
RUN pip install pysqlite3

CMD [ "python", "web/web.py" ]

EXPOSE 80