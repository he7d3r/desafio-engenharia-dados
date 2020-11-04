FROM python:3

WORKDIR /code
COPY dashboard/requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["src/app.py"]
