import asyncio
import json
from asyncua import Server, ua

class ServidorOPC:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4840/freeopcua/server/"):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.server.set_server_name("Servidor")
        self.namespace = None
        self.nodos = {} 


    async def iniciar(self):
        await self.server.init()
        self.namespace = await self.server.register_namespace("http://redes.servidor_opcua.cl/procesos")
        
        # variables nodo salmuera
        Server_Salmuera = await self.server.nodes.objects.add_object(self.namespace, "Server_Salmuera")
        
        # Usamos self. para que sean accesibles desde toda la clase
        self.datos_tubo_h2_salmuera = await Server_Salmuera.add_variable(self.namespace, "Datos_Tubo_H2", "{}")
        self.datos_tubo_cl2_salmuera = await Server_Salmuera.add_variable(self.namespace, "Datos_Tubo_CL2", "{}")
        self.datos_deposito_h2_salmuera = await Server_Salmuera.add_variable(self.namespace, "Datos_Deposito_H2", "{}")
        self.datos_deposito_cl2_salmuera = await Server_Salmuera.add_variable(self.namespace, "Datos_Deposito_CL2", "{}")
        self.datos_deposito_naoh_salmuera = await Server_Salmuera.add_variable(self.namespace, "Datos_Deposito_NaOH", "{}")

        await self.datos_tubo_h2_salmuera.set_writable()
        await self.datos_tubo_cl2_salmuera.set_writable()
        await self.datos_deposito_h2_salmuera.set_writable()
        await self.datos_deposito_cl2_salmuera.set_writable()
        await self.datos_deposito_naoh_salmuera.set_writable()

        # variables nodo agua
        Server_Agua = await self.server.nodes.objects.add_object(self.namespace, "Server_Agua")
        
        # Usamos self. para que sean accesibles desde toda la clase
        self.datos_tubo_h2_agua = await Server_Agua.add_variable(self.namespace, "Datos_Tubo_H2", "{}")
        self.datos_tubo_o2_agua = await Server_Agua.add_variable(self.namespace, "Datos_Tubo_O2", "{}")
        self.datos_deposito_h2_agua = await Server_Agua.add_variable(self.namespace, "Datos_Deposito_H2", "{}")
        self.datos_deposito_o2_agua = await Server_Agua.add_variable(self.namespace, "Datos_Deposito_O2", "{}")

        await self.datos_tubo_h2_agua.set_writable()
        await self.datos_tubo_o2_agua.set_writable()
        await self.datos_deposito_h2_agua.set_writable()
        await self.datos_deposito_o2_agua.set_writable()

        self.estado_salmuera = await Server_Salmuera.add_variable(self.namespace, "Estado_Salmuera", "{}")
        await self.estado_salmuera.set_writable()

        self.estado_agua = await Server_Agua.add_variable(self.namespace, "Estado_Agua", "{}")
        await self.estado_agua.set_writable()
        
        await self.server.start()
        print(f"Servidor OPC UA iniciado en {self.server.endpoint}")

    async def detener(self):
        await self.server.stop()

    async def generar_reporte(self):
        # 1. Leemos los strings crudos desde el servidor OPC UA
        raw_tubo_h2_agua = await self.datos_tubo_h2_agua.read_value()
        raw_tubo_o2_agua = await self.datos_tubo_o2_agua.read_value()
        raw_deposito_h2_agua = await self.datos_deposito_h2_agua.read_value()
        raw_deposito_o2_agua = await self.datos_deposito_o2_agua.read_value()

        raw_tubo_h2_salmuera = await self.datos_tubo_h2_salmuera.read_value()
        raw_tubo_cl2_salmuera = await self.datos_tubo_cl2_salmuera.read_value()
        raw_deposito_h2_salmuera = await self.datos_deposito_h2_salmuera.read_value()
        raw_deposito_cl2_salmuera = await self.datos_deposito_cl2_salmuera.read_value()
        raw_deposito_naoh_salmuera = await self.datos_deposito_naoh_salmuera.read_value()

        
        # Usamos un diccionario vacío en caso de que json.loads falle por un string mal formado
        try:
            datos_server_agua = {
                "tubo_h2_agua": json.loads(raw_tubo_h2_agua),
                "tubo_o2_agua": json.loads(raw_tubo_o2_agua),
                "deposito_h2_agua": json.loads(raw_deposito_h2_agua),
                "deposito_o2_agua": json.loads(raw_deposito_o2_agua)
            }

            datos_server_salmuera = {
                "tubo_h2_salmuera": json.loads(raw_tubo_h2_salmuera),
                "tubo_cl2_salmuera": json.loads(raw_tubo_cl2_salmuera),
                "deposito_h2_salmuera": json.loads(raw_deposito_h2_salmuera),
                "deposito_cl2_salmuera": json.loads(raw_deposito_cl2_salmuera),
                "deposito_naoh_salmuera": json.loads(raw_deposito_naoh_salmuera)
            }

        except json.JSONDecodeError:
            print("Error: Uno de los nodos envió un JSON inválido.")
            datos_server_agua = {}
            datos_server_salmuera = {}

        # 3. Retornamos o imprimimos el JSON grande
        reporte_final = {
            "server_agua": datos_server_agua,
            "server_salmuera": datos_server_salmuera
        }
        
        reporte_final_json = json.dumps(reporte_final, indent=4)

        return reporte_final_json, reporte_final
    
    async def publicar_estados(self, estado_agua, estado_salmuera):
        def normalizar(estado):
            # primer ciclo: viene "NORMAL" (str). Ciclos siguientes: dict con un estado por sub-nodo.
            if isinstance(estado, dict):
                return estado
            return {"global": estado}

        await self.estado_salmuera.write_value(json.dumps(normalizar(estado_salmuera)))
        await self.estado_agua.write_value(json.dumps(normalizar(estado_agua)))