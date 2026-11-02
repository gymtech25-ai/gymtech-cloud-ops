FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY services/facebook_auto_responder/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/facebook_auto_responder/ services/facebook_auto_responder/

EXPOSE 8080

CMD ["python", "services/facebook_auto_responder/auto_responder_cloud.py"]
