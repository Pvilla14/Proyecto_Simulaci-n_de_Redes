import asyncio
from asyncua import Client

async def nodo_tubo_CL2():

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
            ["0:Objects", f"{ns_local}:Tubo_recolector_CL2", f"{ns_local}:Presion"]
        )
        nodo_concentracion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_CL2", f"{ns_local}:Concentracion"]
        )
        nodo_impurezas = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_CL2", f"{ns_local}:Impurezas"]
        )

        
        while True:
            #obtener valores
            presion_actual = obtener_presion()
            concentracion_actual = obtener_concentracion()
            hay_impurezas = verificar_impurezas()
            
            #enviar valores al server de salmuera
            await nodo_presion.write_value(presion_actual)
            await nodo_concentracion.write_value(concentracion_actual)
            await nodo_impurezas.write_value(hay_impurezas)

            print(f"Tubo CL2 -> Presión: {presion_actual:.2f} | Concentración: {concentracion_actual:.2f} | Impurezas: {hay_impurezas}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion():
    return 1.0

def obtener_concentracion():
    return 1.0

def verificar_impurezas():
    return True


if __name__ == "__main__":
    asyncio.run(nodo_tubo_CL2())