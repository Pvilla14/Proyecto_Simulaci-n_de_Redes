import asyncio
import random
from asyncua import Client

class ProtocoloHandler:
    def __init__(self, estado_actual):
        self.estado_actual = estado_actual

    def datachange_notification(self, node, val, data):
        print(f"Tubo H2 recibió estado: {val}")
        self.estado_actual = val

async def nodo_tubo_H2():

    url_nodo_salmuera = "opc.tcp://e_salmuera_falso:4841/Electrolisis_Salmuera/server/"
    cliente = Client(url=url_nodo_salmuera)

# === CONFIGURACIÓN DE SEGURIDAD PARA EL CLIENTE TUBO H2 ===
    # 1. Inicializar el almacén para generar el certificado único de este componente
    await cliente.init_certificate_store(
        cert_path="tubo_h2_cert.pem", 
        private_key_path="tubo_h2_key.pem"
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
        nodo_presion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Presion"]
        )
        nodo_concentracion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Concentracion"]
        )
        nodo_impurezas = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Impurezas"]
        )
        nodo_estado = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Tubo_recolector_H2", f"{ns_local}:Estado"]
        )


        estado = "NORMAL"

        handler = ProtocoloHandler(estado_actual=estado)
        sub = await cliente.create_subscription(300, handler)
        await sub.subscribe_data_change(nodo_estado)
        
        while True:

            estado_actual = handler.estado_actual  # Obtener el estado actual desde el manejador

            #Obtener valores anteriores para tomar deciciones
            presion_anterior = await nodo_presion.get_value()
            concentracion_anterior = await nodo_concentracion.get_value()
            impurezas_anterior = await nodo_impurezas.get_value()
            
            #Obtener valores actuales
            presion_actual = obtener_presion(presion_anterior, estado=estado_actual) #hay que poder sacarlo de un nodo de control
            concentracion_actual = obtener_concentracion(concentracion_anterior, estado=estado_actual)
            hay_impurezas = verificar_impurezas(impurezas_anterior, estado=estado_actual)
            
            #enviar valores al server de salmuera
            await nodo_presion.write_value(presion_actual)
            await nodo_concentracion.write_value(concentracion_actual)
            await nodo_impurezas.write_value(hay_impurezas)

            print(f"Tubo H2 [{estado_actual}] -> Presión: {presion_actual:.2f} | "f"Concentración: {concentracion_actual:.2f} | Impurezas: {hay_impurezas}")
             
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

def obtener_presion(presion_anterior, estado):
    if estado == "DETENER":
        objetivo = 2.0
        paso = random.uniform(0.1, 0.25)
        if presion_anterior > objetivo:
            return max(objetivo, presion_anterior - paso)
        else:
            return min(objetivo, presion_anterior + paso)
    elif estado == "AJUSTAR":
        return presion_anterior + random.uniform(-0.2, -0.1)
    else:  # NORMAL
        return presion_anterior + random.uniform(-0.2, 0.3)


def obtener_concentracion(concentracion_anterior, estado):
    if estado == "DETENER":
        objetivo = 99.5
        paso = random.uniform(1.0, 3.0)  # menor que el umbral de "cambio brusco" (5.0 / 10.0)
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

def verificar_impurezas(impurezas_anterior, estado):
    if estado == "DETENER":
        return False

    elif estado == "AJUSTAR":
        if impurezas_anterior:
            if random.random() < 0.3:  # 30% de resolverse por ciclo
                return False
            return True
        else:
            return False

    else:  # NORMAL
        if random.random() < 0.02:
            return True
        return False

    
if __name__ == "__main__":
    asyncio.run(nodo_tubo_H2())


