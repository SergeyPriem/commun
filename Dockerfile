FROM python:3.12 AS compile-image
RUN apt-get update -y && apt-get install -y sudo && mkdir /app && python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

FROM python:3.12 AS run-image
RUN apt-get update -y && apt-get install -y sudo && mkdir /app
COPY --from=compile-image /app /app
ENV PATH="/app/venv/bin:$PATH"
WORKDIR /app

ENTRYPOINT [ "streamsync", "run" ]
EXPOSE 5000
CMD [ ".",  "--port", "5000", "--host", "0.0.0.0" ]