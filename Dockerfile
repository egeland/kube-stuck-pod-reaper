FROM python:3-alpine

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY kube-stuck-pod-reaper.py .

RUN chmod 700 kube-stuck-pod-reaper.py
