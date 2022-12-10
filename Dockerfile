FROM python:3.11.1-alpine3.17

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
RUN mkdir -p /app/backend
COPY ./backend /app/backend
WORKDIR /app/backend
EXPOSE 8000

ARG DEV=false
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /venv/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        backend-user

ENV PATH="/venv/bin:$PATH"

USER backend-user
