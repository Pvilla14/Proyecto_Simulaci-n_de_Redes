import asyncio
import json

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from opcua_server import ServidorOPC
from controlador import Controlador as Controlador


# ---------------------------------------------------------------------------
# Estado compartido con el dashboard: lo actualiza ciclo_control(),
# lo lee/envía el WebSocket. No necesita lock porque todo corre en el
# mismo loop de asyncio (un solo hilo) y nunca se hace await entremedio
# de leer y escribir estas dos claves.
# ---------------------------------------------------------------------------
estado_compartido = {
    "conectado": True,
    "datos": {},   # reporte_dict["server_salmuera"]: lo que sube hacia el controlador
    "estado": {},  # estado_salmuera: lo que baja de vuelta desde el controlador
}
clientes_ws: set[WebSocket] = set()


async def broadcast():
    if not clientes_ws:
        return
    mensaje = json.dumps(estado_compartido)
    caidos = []
    for ws in clientes_ws:
        try:
            await ws.send_text(mensaje)
        except Exception:
            caidos.append(ws)
    for ws in caidos:
        clientes_ws.discard(ws)


# --- FastAPI: sirve la página y el WebSocket ---
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clientes_ws.add(websocket)
    await websocket.send_text(json.dumps(estado_compartido))  # snapshot inicial
    try:
        while True:
            # no esperamos mensajes del navegador, solo mantenemos viva la conexión
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes_ws.discard(websocket)


# --- tu ciclo de control, con el broadcast agregado ---
async def ciclo_control(servidor: ServidorOPC, controler: Controlador):
    while True:
        # Reporte de los datos de los nodos OPC UA
        reporte_json, reporte_dict = await servidor.generar_reporte()

        # Evaluamos los datos del reporte y tomamos decisiones
        estado_agua, estado_salmuera = controler.recibir_datos(reporte_dict)

        # Publicamos los resultados de vuelta en el servidor central
        await servidor.publicar_estados(estado_agua, estado_salmuera)

        # NUEVO: actualizamos el estado compartido y avisamos al dashboard
        estado_compartido["datos"] = reporte_dict.get("server_salmuera", {})
        estado_compartido["estado"] = (
            estado_salmuera if isinstance(estado_salmuera, dict) else {"global": estado_salmuera}
        )
        await broadcast()

        print(f"Ciclo evaluado -> agua: {estado_agua} | salmuera: {estado_salmuera}")

        await asyncio.sleep(2)


async def main():
    servidor = ServidorOPC()
    await servidor.iniciar()

    controler = Controlador()

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
    servidor_web = uvicorn.Server(config)

    try:
        # ambos corren en paralelo, en el mismo loop de asyncio
        await asyncio.gather(
            ciclo_control(servidor, controler),
            servidor_web.serve(),
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Deteniendo servidor...")
    finally:
        await servidor.detener()


if __name__ == "__main__":
    asyncio.run(main())