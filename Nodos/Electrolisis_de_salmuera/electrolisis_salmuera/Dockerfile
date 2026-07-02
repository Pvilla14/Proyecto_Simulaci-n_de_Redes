FROM python:3.9-alpine

RUN adduser -D -h /home/usuario usuario

WORKDIR /nodo
RUN chown -R usuario:usuario /nodo

COPY requirements.txt .

USER usuario
ENV PATH=/home/usuario/.local/bin:$PATH
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=usuario:usuario . .

EXPOSE 4841

HEALTHCHECK --interval=3s --timeout=2s --retries=10 --start-period=5s \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('localhost', 4841)); s.close()" || exit 1


CMD ["python", "Nodo_Esalmuera.py"]
