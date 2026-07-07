import asyncio
import random
from asyncua import Client

async def nodo_deposito_H2():


    estado_actual = handler.estado_actual  # Obtener el estado actual desde el manejador

    url_nodo_agua = "opc.tcp://localhost:4842/Electrolisis_Agua/server/"
    cliente = Client(url=url_nodo_agua)

    #conectar con servidor de agua
    try:
        print(f"Conectando al servidor OPC UA en {url_nodo_agua} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        ns_local = await cliente.get_namespace_index("http://electrolisis.agua.cl/local")

        #buscar datos en server
        nodo_presion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_H2", f"{ns_local}:Presion"]
        )
        nodo_cantidad_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_H2", f"{ns_local}:Cantidad de H2"]
        )
        nodo_estado = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_H2", f"{ns_local}:Estado"]
        )

        estado = "NORMAL"
        handler = ProtocoloHandler(estado_actual=estado)
        sub = await cliente.create_subscription(300, handler)
        await sub.subscribe_data_change(nodo_estado)

        

        
        while True:
            estado_actual = handler.estado_actual  # Obtener el estado actual desde el manejador

            #obetener valores anteriores para tomar deciciones
            presion_anterior = await nodo_presion.get_value()
            cantidad_anterior_H2 = await nodo_cantidad_H2.get_value()

            #obtener valores
            presion_actual = obtener_presion(presion_anterior, estado=estado_actual)
            nueva_cantidad_H2 = obtener_cantidad_H2(cantidad_anterior_H2, estado=estado_actual)
            if nueva_cantidad_H2 is not None:
                cantidad_actual_H2 = nueva_cantidad_H2

            #enviar valores al server de salmuera

            #enviar valores al server de agua
            await nodo_presion.write_value(presion_actual)
            await nodo_cantidad_H2.write_value(cantidad_actual_H2)

            print(f"Deposito H2 -> Presión: {presion_actual:.2f} | Cantidad de H2: {cantidad_actual_H2:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion(presion_anterior, estado):
    if estado == "DETENER":
        objetivo = 2.0
        paso = random.uniform(0.1, 0.25)
        if presion_anterior > objetivo:
            return max(objetivo, presion_anterior - paso)
        else:
            return min(objetivo, presion_anterior + paso)
    elif estado == "AJUSTAR":
        return presion_anterior + random.uniform(-0.2, -0.1)
    else:  # NORMAL
        return presion_anterior + random.uniform(-0.2, 0.3)
    
def obtener_cantidad_H2(cantidad_anterior_H2, estado):
    if estado == "DETENER":
        return None
    elif estado == "AJUSTAR":
        # Hubo una baja (fuga o pérdida). 
        # Forzamos una recuperación  (ej. entre 10 y 15 unidades)
        incremento_recuperacion = random.uniform(10.0, 15.0)
        return cantidad_anterior_H2 + incremento_recuperacion
        
    else: # NORMAL
        # Simula el flujo continuo y realista de llenado nominal (ej. entre 2 y 8 unidades)
        llenado_nominal = random.uniform(2.0, 8.0)
        return cantidad_anterior_H2 + llenado_nominal

if __name__ == "__main__":
    asyncio.run(nodo_deposito_H2())


class ProtocoloHandler:
    def __init__(self, estado_actual):
        self.estado_actual = estado_actual

    def datachange_notification(self, node, val, data):
        print(f"Deposito H2 recibió estado: {val}")
        self.estado_actual = val

