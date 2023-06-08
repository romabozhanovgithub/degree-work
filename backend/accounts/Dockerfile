FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYROOT /pyroot
ENV PYTHONUSERBASE $PYROOT
RUN env

FROM builder AS base

RUN pip install --no-cache pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy

FROM base AS base-dev

RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy --dev

FROM base-dev AS dev

COPY --from=base-dev $PYROOT/lib/ $PYROOT/lib/

WORKDIR /app

COPY . .

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
