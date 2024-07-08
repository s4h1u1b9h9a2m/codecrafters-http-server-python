FROM python:3.9-alpine

WORKDIR /usr/src/app

# COPY requirements.txt ./

# RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PATH /usr/bin:/usr/local/bin:/bin

CMD [ "python", "./app/main.py" ]