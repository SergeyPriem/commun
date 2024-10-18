#FROM python:3.12 AS compile-image
#RUN apt-get update -y && mkdir /app && python3 -m venv /app/venv
#ENV PATH="/app/venv/bin:$PATH"
#COPY . /app
#WORKDIR /app
#RUN pip3 install -r requirements.txt
#
#FROM python:3.12 AS run-image
#RUN apt-get update -y && mkdir /app
#COPY --from=compile-image /app /app
#ENV PATH="/app/venv/bin:$PATH"
#
#WORKDIR /app
#
##COPY /app/static/index.html /app/venv/lib/python3.12/site-packages/writer/static/index.html
#
#ENTRYPOINT [ "writer", "run" ]
#EXPOSE 5000
#CMD [ ".",  "--port", "5000", "--host", "0.0.0.0" ]

# Stage 1: Build Stage
FROM python:3.12-slim AS build-stage
WORKDIR /app
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Stage 2: Final Stage
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update -y && apt-get install -y --no-install-recommends libpq-dev
COPY --from=build-stage /app /app
ENV PATH="/app/venv/bin:$PATH"
COPY . .
ENTRYPOINT [ "writer", "run" ]
EXPOSE 5000
CMD [ ".", "--port", "5000", "--host", "0.0.0.0" ]


