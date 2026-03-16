
FROM python:3.11-slim

WORKDIR /app
COPY tautulli_session_exporter.py /app/

RUN pip install flask requests

EXPOSE 9594
CMD ["python","tautulli_session_exporter.py"]
