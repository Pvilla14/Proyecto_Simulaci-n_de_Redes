import asyncio
from asyncua import Client

async def nodo_tubo_H2():

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
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Presion"]
        )
        nodo_concentracion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Concentracion"]
        )
        nodo_impurezas = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Impurezas"]
        )

        
        while True:
            #Obtener valores anteriores para tomar deciciones
            presion_anterior = await nodo_presion.get_value()
            concentracion_anterior = await nodo_concentracion.get_value()
            impurezas_anterior = await nodo_impurezas.get_value()
            
            #Obtener valores actuales
            presion_actual = obtener_presion()
            concentracion_actual = obtener_concentracion()
            hay_impurezas = verificar_impurezas()
            
            #enviar valores al server de salmuera
            await nodo_presion.write_value(presion_actual)
            await nodo_concentracion.write_value(concentracion_actual)
            await nodo_impurezas.write_value(hay_impurezas)

            print(f"Tubo H2 -> Presión: {presion_actual:.2f} | Concentración: {concentracion_actual:.2f} | Impurezas: {hay_impurezas}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion(presion_anterior, estado):
    if estado == "DETENER":
        return 1.0
    elif estado == "AJUSTAR":
        return 2
    else: #NORMAL
        return 1

def obtener_concentracion(concentracion_anterior, estado):
    if estado == "DETENER":
        return 1.0
    elif estado == "AJUSTAR":
        return 2
    else: #NORMAL
        return 1
def verificar_impurezas(impurezas_anterior, estado):
    if estado == "DETENER":
        return False
    elif estado == "AJUSTAR":
        return True
    else: #NORMAL
        return True
    
if __name__ == "__main__":
    asyncio.run(nodo_tubo_H2())