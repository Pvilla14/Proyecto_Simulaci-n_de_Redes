import asyncio
import random
from asyncua import Client

async def nodo_tubo_H2():

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
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Presion"]
        )
        nodo_concentracion_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Concentracion de H2"]
        )
        nodo_concentracion_O2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Concentracion de O2"]
        )

        
        while True:
            #obtenemos valores anteriores para tomar decisiones
            presion_anterior = await nodo_presion.get_value()
            concentracion_anterior_H2 = await nodo_concentracion_H2.get_value()
            concentracion_anterior_O2 = await nodo_concentracion_O2.get_value()

            #obtener valores
            presion_actual = obtener_presion()
            concentracion_actual_H2 = obtener_concentracion_H2()
            concentracion_actual_O2 = obtener_concentracion_O2()
            
            #enviar valores al server de agua
            await nodo_presion.write_value(presion_actual)
            await nodo_concentracion_H2.write_value(concentracion_actual_H2)
            await nodo_concentracion_O2.write_value(concentracion_actual_O2)

            print(f"Tubo H2 -> Presión: {presion_actual:.2f} | Concentración de H2: {concentracion_actual_H2:.2f} | Concentración de O2: {concentracion_actual_O2:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion(presion_anterior, estado):
    if estado == "DETENER":
        return 
    elif estado == "AJUSTAR":
        return presion_anterior + random.uniform(-0.2, -0.1)
    else: #NORMAL
        return presion_anterior + random.uniform(-0.2, 0.3)

def obtener_concentracion_H2(concentracion_anterior_H2, estado):
    if estado == "DETENER":
        return 
        
    elif estado == "AJUSTAR":
        # Hay una pérdida leve de eficiencia o inestabilidad.
        # Oscila en un rango sub-óptimo (ej. entre 95% y 98%)
        cambio = random.uniform(-0.5, 0.5)
        nuevo_valor = concentracion_anterior_H2 + cambio
        return max(95.0, min(nuevo_valor, 98.0))
        
    else: # NORMAL
        # Operación óptima. Se mantiene muy alta, pegada al 99.9%
        cambio = random.uniform(-0.05, 0.05)
        nuevo_valor = concentracion_anterior_H2 + cambio
        return max(99.0, min(nuevo_valor, 99.9))

def obtener_concentracion_O2(concentracion_anterior_O2, estado):
    if estado == "DETENER":
        return 
    elif estado == "AJUSTAR":
        # Hay una pérdida leve de eficiencia o inestabilidad.
        # Oscila en un rango sub-óptimo (ej. entre 95% y 98%)
        cambio = random.uniform(-0.5, 0.5)
        nuevo_valor = concentracion_anterior_O2 + cambio
        return max(95.0, min(nuevo_valor, 98.0))
    else: # NORMAL
        # Operación óptima. Se mantiene muy alta, pegada al 99.9%
        cambio = random.uniform(-0.05, 0.05)
        nuevo_valor = concentracion_anterior_O2 + cambio
        return max(99.0, min(nuevo_valor, 99.9))
