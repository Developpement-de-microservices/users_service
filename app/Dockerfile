FROM python:3.11.15-trixie

LABEL description="Microservice Flask pour gérer les utilisateurs" 
LABEL service="users_service"

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl && apt-get clean #curl pour healthcheck

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:5000/events || exit 1

CMD ["python", "app.py"]
