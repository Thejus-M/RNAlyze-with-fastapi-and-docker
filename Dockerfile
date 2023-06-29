FROM python:3.10-slim

WORKDIR /code
EXPOSE 80

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/crud.py ./src/crud.py
COPY ./src/database.py ./src/database.py
COPY ./src/features.py ./src/features.py
COPY ./src/main.py ./src/main.py
COPY ./src/models.py ./src/models.py
COPY ./src/schemas.py ./src/schemas.py


COPY ./static ./static
COPY ./templates ./templates
COPY ./model.pkl ./model.pkl

CMD ["uvicorn","src.main:app","--host","0.0.0.0","--port","80","--reload"]
