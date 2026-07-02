import asyncio
import random
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
        return 
    elif estado == "AJUSTAR":
        return presion_anterior + random.uniform(-0.2, -0.1)
    else: #NORMAL
        return presion_anterior + random.uniform(-0.2, 0.3)

def obtener_concentracion(concentracion_anterior, estado):
    if estado == "DETENER":
        return 
        
    elif estado == "AJUSTAR":
        # Hay una pérdida leve de eficiencia o inestabilidad.
        # Oscila en un rango sub-óptimo (ej. entre 95% y 98%)
        cambio = random.uniform(-0.5, 0.5)
        nuevo_valor = concentracion_anterior + cambio
        return max(95.0, min(nuevo_valor, 98.0))
        
    else: # NORMAL
        # Operación óptima. Se mantiene muy alta, pegada al 99.9%
        cambio = random.uniform(-0.05, 0.05)
        nuevo_valor = concentracion_anterior + cambio
        return max(99.0, min(nuevo_valor, 99.9))

def verificar_impurezas(impurezas_anterior, estado):
    if estado == "DETENER":
        # Tras la parada de emergencia y purga, el peligro cede.
        # Volvemos a False para limpiar el sistema.
        return False
        
    elif estado == "AJUSTAR":
        # Si ya estábamos en AJUSTAR, mantenemos las impurezas en True
        # para cumplir la condición (Actual: True y Anterior: True) de tu evaluación.
        return True
        
    else: # NORMAL
        # En condiciones normales, el sistema está limpio (False).
        # random que un 1% de las veces devuelva True para forzar el fallo.
        if random.random() < 0.02: # 2% de probabilidad de que aparezca un fallo de la nada
            return True
        return False

    
if __name__ == "__main__":
    asyncio.run(nodo_tubo_H2())