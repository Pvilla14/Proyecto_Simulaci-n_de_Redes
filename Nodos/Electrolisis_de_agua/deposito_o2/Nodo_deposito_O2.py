import asyncio
from asyncua import Client

async def nodo_deposito_O2():

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
            ["0:Objects", f"{ns_local}:Deposito_O2", f"{ns_local}:Presion"]
        )
        nodo_cantidad_O2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_O2", f"{ns_local}:Cantidad de O2"]
        )

        
        while True:
            #obtener valores
            presion_actual = obtener_presion()
            cantidad_actual_O2 = obtener_cantidad_O2()
            
            #enviar valores al server de agua
            await nodo_presion.write_value(presion_actual)
            await nodo_cantidad_O2.write_value(cantidad_actual_O2)

            print(f"Deposito O2 -> Presión: {presion_actual:.2f} | Cantidad de O2: {cantidad_actual_O2:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion():
    return

def obtener_cantidad_O2():
    return
