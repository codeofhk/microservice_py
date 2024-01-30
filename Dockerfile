FROM python:3.9-alpine
WORKDIR /app
COPY requirments.txt ./
RUN pip install -r requirments.txt
COPY . .
EXPOSE 5000
CMD ["python","./services/products.py"]
