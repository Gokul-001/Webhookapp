FROM python:3.11.5-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR C:\Users\gokul\Desktop\Webhookapp -deploy
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN touch log.txt
COPY . .
EXPOSE 8080
CMD ["waitress-serve", "--port=8080", "run:app"]