FROM python:3.10-alpine
WORKDIR /app
COPY main.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["python", "main.py"]
