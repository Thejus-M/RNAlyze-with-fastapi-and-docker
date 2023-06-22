FROM python:3.10-slim

WORKDIR /code
EXPOSE 80

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./static ./static
COPY ./templates ./templates
COPY ./model.pkl ./model.pkl

CMD ["uvicorn","src.main:app","--host","0.0.0.0","--port","80","--reload"]
