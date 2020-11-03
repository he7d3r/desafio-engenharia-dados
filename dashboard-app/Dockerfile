FROM python:3

ENV APPPATH /code
COPY dashboard-app $APPPATH
WORKDIR $APPPATH/app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["src/app.py"]
