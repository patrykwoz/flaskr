ARG PYTHON_VERSION=3.10.12
FROM python:${PYTHON_VERSION}-slim as flaskrbase

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV C_FORCE_ROOT true
ENV PYTHONUNBUFFERED=1

WORKDIR /flaskr

COPY requirements.txt /flaskr/

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt



COPY . .



EXPOSE 5000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--timeout", "60"]


