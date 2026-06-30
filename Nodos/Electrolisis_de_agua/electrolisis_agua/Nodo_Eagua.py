import asyncio
import json
from asyncua import Client, Server

async def nodo_electrolisis_de_agua():
    # 1. Definir la dirección de tu servidor

    #creador del server local de escucha para los nodos de la electrolisis de agua 
    servidor_local = Server()
    servidor_local.set_endpoint("opc.tcp://0.0.0.0:4842/Electrolisis_Agua/")
    servidor_local.set_server_name("Electrolisis_Agua")

    await servidor_local.init()
    ns_local = await servidor_local.register_namespace("http://electrolisis.agua.cl/local")


    #nodos con sus rfespectivas variables a medir
        #tubo de H2 y sus recpectivas variables
    obj_tubo_h2 = await servidor_local.nodes.objects.add_object(ns_local, "Tubo_recolector_H2")
    var_presion_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Concentracion", 0.0)
    var_impurezas_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Impurezas", False)

        #tubo de O2 y sus recpectivas variables
    obj_tubo_o2 = await servidor_local.nodes.objects.add_object(ns_local, "Tubo_recolector_O2")
    var_presion_tubo_o2 = await obj_tubo_o2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_tubo_o2 = await obj_tubo_o2.add_variable(ns_local, "Concentracion", 0.0)
    var_impurezas_tubo_o2 = await obj_tubo_o2.add_variable(ns_local, "Impurezas", False)

        #deposito de H2 y sus variables
    obj_deposito_h2 = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_H2")
    var_presion_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Cantidad", 0.0)

        #deposito de O2 y sus variables
    obj_deposito_o2 = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_O2")
    var_presion_deposito_o2 = await obj_deposito_o2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_deposito_o2 = await obj_deposito_o2.add_variable(ns_local, "Cantidad", 0.0)

    #inicialización de variables
        #variables de tubo de h2
    await var_presion_tubo_h2.set_writable()
    await var_concentracion_tubo_h2.set_writable()
    await var_impurezas_tubo_h2.set_writable()

        #variables de tubo de o2
    await var_presion_tubo_o2.set_writable()
    await var_concentracion_tubo_o2.set_writable()
    await var_impurezas_tubo_o2.set_writable()

        #variables de deposito de h2
    await var_presion_deposito_h2.set_writable()
    await var_concentracion_deposito_h2.set_writable()

        #variables de deposito de o2
    await var_presion_deposito_o2.set_writable()
    await var_concentracion_deposito_o2.set_writable()

    
    await servidor_local.start()
    print("Servidor del Proceso Agua escuchando en puerto 4842...")
    
    #conexion con servidor central en puerto correspondiente 
    url_server_central = "opc.tcp://localhost:4840/freeopcua/server/"
    cliente = Client(url=url_server_central)


    try:
        # 2. Establecer la conexión
        print(f"Conectando al servidor OPC UA en {url_server_central} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        #usar el namespace del server centrar para buscar las variables a actualizar
        ns_server_central = await cliente.get_namespace_index("http://redes.servidor_opcua.cl/procesos")

        # Obtener la variable específica a actualizar para cada nodo        
        server_tubo_h2_agua = await cliente.nodes.root.get_child(
        ["0:Objects", f"{ns_server_central}:Server_Agua", f"{ns_server_central}:Datos_Tubo_H2"]
)

        # 5. Bucle de publicación 
        
        while True:
            # Escribir el jason de datos al servidor

            datos_tubo_h2 = {
                "presion": await var_presion_tubo_h2.read_value(),  # leer presión
                "concentracion": await var_concentracion_tubo_h2.read_value(),  # leer concentración
                "impurezas": await var_impurezas_tubo_h2.read_value()  # leer impurezas
            }
            #trasformamos datos a json y los enviamos al servidor central
            json_datos_tubo_h2 = json.dumps(datos_tubo_h2)
            print(f"Publicando datos al servidor central: {json_datos_tubo_h2}")
            await server_tubo_h2_agua.write_value(json_datos_tubo_h2)
            
            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error en la conexión: {e}")
    finally:
        # 6. Desconectar limpiamente al terminar
        await cliente.disconnect()
        print("Nodo desconectado.")

if __name__ == "__main__":
    asyncio.run(nodo_electrolisis_de_agua())