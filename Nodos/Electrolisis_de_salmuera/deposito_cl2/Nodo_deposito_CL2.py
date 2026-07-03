import asyncio
import random
from asyncua import Client

async def nodo_deposito_CL2():

    url_nodo_salmuera = "opc.tcp://e_salmuera:4841/Electrolisis_Salmuera/server/"
    cliente = Client(url=url_nodo_salmuera)

    #conectar con servidor de salmuera
    try:
        print(f"Conectando al servidor OPC UA en {url_nodo_salmuera} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        ns_local = await cliente.get_namespace_index("http://electrolisis.salmuera.cl/local")

        #buscar datos en server
        nodo_presion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_CL2", f"{ns_local}:Presion"]
        )
        nodo_cantidad_CL2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_CL2", f"{ns_local}:Cantidad"]
        )

        
        while True:
                #Obtener valores anteriores para tomar deciciones
            presion_anterior = await nodo_presion.get_value()
            cantidad_anterior_CL2 = await nodo_cantidad_CL2.get_value()

            #obtener valores
            presion_actual = obtener_presion(presion_anterior, estado="NORMAL") #hay que poder sacarlo de un nodo de control
            cantidad_actual_CL2 = obtener_cantidad_CL2(cantidad_anterior_CL2, estado="NORMAL")

            #enviar valores al server de salmuera
            await nodo_presion.write_value(presion_actual)
            await nodo_cantidad_CL2.write_value(cantidad_actual_CL2)

            print(f"Deposito CL2 -> Presión: {presion_actual:.2f} | Cantidad de CL2: {cantidad_actual_CL2:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion(presion_anterior, estado):
    if estado == "DETENER":
        return None
    elif estado == "AJUSTAR":
        return presion_anterior + random.uniform(-0.2, -0.1)
    else: #NORMAL
        return presion_anterior + random.uniform(-0.2, 0.3)

def obtener_cantidad_CL2(cantidad_anterior_CL2, estado):
    if estado == "DETENER":
        return None
    elif estado == "AJUSTAR":
        # Hubo una baja (fuga o pérdida). 
        # Forzamos una recuperación  (ej. entre 10 y 15 unidades)
        incremento_recuperacion = random.uniform(10.0, 15.0)
        return cantidad_anterior_CL2 + incremento_recuperacion
        
    else: # NORMAL
        # Simula el flujo continuo y realista de llenado nominal (ej. entre 2 y 8 unidades)
        llenado_nominal = random.uniform(2.0, 8.0)
        return cantidad_anterior_CL2 + llenado_nominal


if __name__ == "__main__":
    asyncio.run(nodo_deposito_CL2())
