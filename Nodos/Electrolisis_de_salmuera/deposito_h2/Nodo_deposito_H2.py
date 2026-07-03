import asyncio
from asyncua import Client

async def nodo_deposito_H2():

    url_nodo_salmuera = "opc.tcp://e_salmuera_falso:4841/Electrolisis_Salmuera/server/"
    cliente = Client(url=url_nodo_salmuera)

    #conectar con servidor de salmuera
    try:
        print(f"Conectando al servidor OPC UA en {url_nodo_salmuera} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        ns_local = await cliente.get_namespace_index("http://electrolisis.salmuera.cl/local")

        #buscar datos en server
        nodo_presion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_H2", f"{ns_local}:Presion"]
        )
        nodo_cantidad_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_H2", f"{ns_local}:Cantidad"]
        )

        
        while True:
            #obtener valores
            presion_actual = obtener_presion()
            cantidad_actual_H2 = obtener_cantidad_H2()
            
            #enviar valores al server de salmuera
            await nodo_presion.write_value(presion_actual)
            await nodo_cantidad_H2.write_value(cantidad_actual_H2)

            print(f"Deposito H2 -> Presión: {presion_actual:.2f} | Cantidad de H2: {cantidad_actual_H2:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion():
    return 1.0

def obtener_cantidad_H2():
    return 1.0

if __name__ == "__main__":
    asyncio.run(nodo_deposito_H2())


