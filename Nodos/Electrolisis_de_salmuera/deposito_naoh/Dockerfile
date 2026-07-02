FROM python:3.9-alpine

RUN adduser -D -h /home/usuario usuario

WORKDIR /nodo
RUN chown -R usuario:usuario /nodo

COPY requirements.txt .

USER usuario
ENV PATH=/home/usuario/.local/bin:$PATH
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=usuario:usuario . .

CMD ["python", "Nodo_deposito_NaOH.py"]
