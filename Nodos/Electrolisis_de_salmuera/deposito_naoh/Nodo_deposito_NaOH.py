import asyncio
import random
from asyncua import Client

async def nodo_deposito_NaOH():

    url_nodo_salmuera = "opc.tcp://e_salmuera_falso:4841/Electrolisis_Salmuera/server/"
    cliente = Client(url=url_nodo_salmuera)

# === CONFIGURACIÓN DE SEGURIDAD PARA EL CLIENTE DEPÓSITO NaOH ===
    # 1. Inicializar el almacén para generar el certificado de este cliente específico
    await cliente.init_certificate_store(
        cert_path="deposito_naoh_cert.pem", 
        private_key_path="deposito_naoh_key.pem"
    )
    
    # 2. Configurar la política de seguridad requerida por el servidor local de salmuera
    await cliente.set_security_policy(
        "http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256"
    )
    # ==========================================================

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
        nodo_estado = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_NaOH", f"{ns_local}:Estado"]
        )

        estado = "NORMAL"
        handler = ProtocoloHandler(estado_actual=estado)
        sub = await cliente.create_subscription(300, handler)
        await sub.subscribe_data_change(nodo_estado)

        
        while True:

            estado_actual = handler.estado_actual  # Obtener el estado actual desde el manejador

            #Obtener valores anteriores para tomar deciciones
            concentracion_anterior = await nodo_concentracion.get_value()
            cantidad_anterior_NaOH = await nodo_cantidad_NaOH.get_value()   
            #obtener valores
            concentracion_actual = obtener_concentracion(concentracion_anterior, estado=estado_actual)
            nueva_cantidad_NaOH = obtener_cantidad_NaOH(cantidad_anterior_NaOH, estado=estado_actual)
            if nueva_cantidad_NaOH is not None:
                cantidad_actual_NaOH = nueva_cantidad_NaOH

            #enviar valores al server de salmuera
            await nodo_concentracion.write_value(concentracion_actual)
            await nodo_cantidad_NaOH.write_value(cantidad_actual_NaOH)

            print(f"Deposito NaOH [{estado_actual}] ->  -> Cantidad de NaOH: {cantidad_actual_NaOH:.2f} | Concentración: {concentracion_actual:.2f}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_concentracion(concentracion_anterior, estado):
    if estado == "DETENER":
        # migra hacia un punto seguro dentro de rango, con paso menor al umbral de "cambio brusco" (10.0)
        objetivo = 50.0
        paso = random.uniform(3.0, 7.0)
        if concentracion_anterior > objetivo:
            return max(objetivo, concentracion_anterior - paso)
        else:
            return min(objetivo, concentracion_anterior + paso)
    elif estado == "AJUSTAR":
        cambio = random.uniform(-0.5, 0.5)
        nuevo_valor = concentracion_anterior + cambio
        return max(95.0, min(nuevo_valor, 98.0))
    else:  # NORMAL
        cambio = random.uniform(-0.05, 0.05)
        nuevo_valor = concentracion_anterior + cambio
        return max(99.0, min(nuevo_valor, 99.9))

def obtener_cantidad_NaOH(cantidad_anterior_NaOH, estado):
    if estado == "DETENER":
        return None  # se mantiene igual, y el delta=0 resultante ya evalúa NORMAL el próximo ciclo
    elif estado == "AJUSTAR":
        incremento_recuperacion = random.uniform(10.0, 15.0)
        return cantidad_anterior_NaOH + incremento_recuperacion
    else:  # NORMAL
        llenado_nominal = random.uniform(2.0, 8.0)
        return cantidad_anterior_NaOH + llenado_nominal


if __name__ == "__main__":
    asyncio.run(nodo_deposito_NaOH())


class ProtocoloHandler:
    def __init__(self, estado_actual):
        self.estado_actual = estado_actual

    def datachange_notification(self, node, val, data):
        print(f"Deposito NaOH recibió estado: {val}")
        self.estado_actual = val
