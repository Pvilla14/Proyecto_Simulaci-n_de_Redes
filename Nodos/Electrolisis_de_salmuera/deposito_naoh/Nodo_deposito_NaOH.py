import asyncio
from asyncua import Client

async def nodo_deposito_NaOH():

    url_nodo_salmuera = "opc.tcp://e_salmuera:4841/Electrolisis_Salmuera/server/"
    cliente = Client(url=url_nodo_salmuera)

    #conectar con servidor de salmuera
    try:
        print(f"Conectando al servidor OPC UA en {url_nodo_salmuera} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        ns_local = await cliente.get_namespace_index("http://electrolisis.salmuera.cl/local")

        #buscar datos en server
        nodo_concentracion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_NaOH", f"{ns_local}:Concentracion"]
        )
        nodo_cantidad_NaOH = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_NaOH", f"{ns_local}:Cantidad"]
        )

        
        while True:
            #obtener valores
            concentracion_actual = obtener_concentracion()
            cantidad_actual_NaOH = obtener_cantidad_NaOH()
            
            #enviar valores al server de salmuera
            await nodo_concentracion.write_value(concentracion_actual)
            await nodo_cantidad_NaOH.write_value(cantidad_actual_NaOH)

            print(f"Deposito NaOH -> Cantidad de NaOH: {cantidad_actual_NaOH:.2f} | Concentración: {concentracion_actual:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_concentracion():
    return 1.0

def obtener_cantidad_NaOH():
    return 1.0

if __name__ == "__main__":
    asyncio.run(nodo_deposito_NaOH())