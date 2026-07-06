import asyncio
import random
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
            #Obtener valores anteriores para tomar deciciones
            concentracion_anterior = await nodo_concentracion.get_value()
            cantidad_anterior_NaOH = await nodo_cantidad_NaOH.get_value()   
            #obtener valores
            concentracion_actual = obtener_concentracion(concentracion_anterior, estado="NORMAL") #hay que poder sacarlo de un nodo de control 
            cantidad_actual_NaOH = obtener_cantidad_NaOH(cantidad_anterior_NaOH, estado="NORMAL")

            #enviar valores al server de salmuera
            await nodo_concentracion.write_value(concentracion_actual)
            await nodo_cantidad_NaOH.write_value(cantidad_actual_NaOH)

            print(f"Deposito NaOH -> Cantidad de NaOH: {cantidad_actual_NaOH:.2f} | Concentración: {concentracion_actual:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_concentracion(concentracion_anterior, estado):
    if estado == "DETENER":
        return None
        
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

def obtener_cantidad_NaOH(cantidad_anterior_NaOH, estado):
    if estado == "DETENER":
        return None
    elif estado == "AJUSTAR":
        # Hubo una baja (fuga o pérdida). 
        # Forzamos una recuperación  (ej. entre 10 y 15 unidades)
        incremento_recuperacion = random.uniform(10.0, 15.0)
        return cantidad_anterior_NaOH + incremento_recuperacion
        
    else: # NORMAL
        # Simula el flujo continuo y realista de llenado nominal (ej. entre 2 y 8 unidades)
        llenado_nominal = random.uniform(2.0, 8.0)
        return cantidad_anterior_NaOH + llenado_nominal


if __name__ == "__main__":
    asyncio.run(nodo_deposito_NaOH())