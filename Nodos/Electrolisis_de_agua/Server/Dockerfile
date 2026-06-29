FROM python:3.9-alpine

RUN adduser -D -h /home/usuario usuario

WORKDIR /server
RUN chown -R usuario:usuario /server

COPY requirements.txt .

USER usuario
ENV PATH=/home/usuario/.local/bin:$PATH
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=usuario:usuario . .

EXPOSE 4840

CMD ["python", "main.py"]
