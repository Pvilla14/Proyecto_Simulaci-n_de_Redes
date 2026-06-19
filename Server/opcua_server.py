import asyncio
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
        
        # Crear el objeto para salmuera y para agua con cada variables para cada uno de sus subnodos
        Server_Salmuera = await self.server.nodes.objects.add_object(f"{self.namespace}:Salmuera", "Server_Salmuera")
        datos_tubo_h2 =await Server_Salmuera.add_variable(f"{self.namespace}:Salmuera", "Datos_Tubo_H2", "{}")

        #inicialiazar las variables
        await datos_tubo_h2.set_writable()

        
        # Aquí crearías las variables a monitorizar (voltaje, corriente, etc.)
        
        await self.server.start()
        print(f"Servidor OPC UA iniciado en {self.server.endpoint}")

    async def detener(self):
        await self.server.stop()