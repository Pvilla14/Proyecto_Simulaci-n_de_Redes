import asyncio
import random
from asyncua import Client

class ProtocoloHandler:
    def __init__(self, estado_actual):
        self.estado_actual = estado_actual

    def datachange_notification(self, node, val, data):
        print(f"Deposito CL2 recibió estado: {val}")
        self.estado_actual = val

async def nodo_deposito_CL2():

    url_nodo_salmuera = "opc.tcp://e_salmuera_falso:4841/Electrolisis_Salmuera/server/"
    cliente = Client(url=url_nodo_salmuera)

    # === CONFIGURACIÓN DE SEGURIDAD PARA EL CLIENTE DEPÓSITO CL2 ===
    # Inicializar el almacén para generar el certificado de este cliente específico
    await cliente.init_certificate_store(
        cert_path="deposito_cl2_cert.pem", 
        private_key_path="deposito_cl2_key.pem"
    )
    
    # Configurar la política de seguridad requerida por el servidor local de salmuera
    await cliente.set_security_policy(
        "http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256"
    )
    # ==========================================================

    # conectar con servidor de salmuera
    try:
        print(f"Conectando al servidor OPC UA en {url_nodo_salmuera} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        ns_local = await cliente.get_namespace_index("http://electrolisis.salmuera.cl/local")

        # buscar datos en server
        nodo_presion = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_CL2", f"{ns_local}:Presion"]
        )
        nodo_cantidad_CL2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_CL2", f"{ns_local}:Cantidad"]
        )
        nodo_estado = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Deposito_CL2", f"{ns_local}:Estado"]
        )

        estado = "NORMAL"
        handler = ProtocoloHandler(estado_actual=estado)
        sub = await cliente.create_subscription(300, handler)
        await sub.subscribe_data_change(nodo_estado)

        # Establecer un valor inicial por defecto para evitar UnboundLocalError
        cantidad_actual_CL2 = 0.0
        
        while True:

            estado_actual = handler.estado_actual  # Obtener el estado actual desde el manejador
            
            # Obtener valores anteriores para tomar decisiones
            presion_anterior = await nodo_presion.get_value()
            cantidad_anterior_CL2 = await nodo_cantidad_CL2.get_value()

            # obtener valores
            presion_actual = obtener_presion(presion_anterior, estado=estado_actual)
            nueva_cantidad_CL2 = obtener_cantidad_CL2(cantidad_anterior_CL2, estado=estado_actual)
            if nueva_cantidad_CL2 is not None:
                cantidad_actual_CL2 = nueva_cantidad_CL2

            # enviar valores al server de salmuera
            await nodo_presion.write_value(presion_actual)
            await nodo_cantidad_CL2.write_value(cantidad_actual_CL2)

            print(f"Deposito CL2 -> Presión: {presion_actual:.2f} | Cantidad de CL2: {cantidad_actual_CL2:.2f}")
             
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
    
def obtener_cantidad_CL2(cantidad_anterior_CL2, estado):
    if estado == "DETENER":
        return None  # se mantiene igual
    elif estado == "AJUSTAR":
        incremento_recuperacion = random.uniform(10.0, 15.0)
        return cantidad_anterior_CL2 + incremento_recuperacion
    else:  # NORMAL
        llenado_nominal = random.uniform(2.0, 8.0)
        return cantidad_anterior_CL2 + llenado_nominal

if __name__ == "__main__":
    asyncio.run(nodo_deposito_CL2())