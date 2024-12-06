FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# List installed packages to verify installation
RUN pip list

COPY . .

CMD ["python", "CallApi.py"]