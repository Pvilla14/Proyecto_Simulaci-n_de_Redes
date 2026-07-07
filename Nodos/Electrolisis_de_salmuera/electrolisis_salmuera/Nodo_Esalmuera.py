import asyncio
import json
from asyncua import Client, Server
from firma import verificar

class EstadoHandler:
    """Recibe el JSON grande de estado desde el central y lo reparte
    a las variables locales de cada tubo/depósito."""

    def __init__(self, mapa_variables_locales):
        # nombre del sub-proceso (igual a las keys que usa el controlador) -> variable OPC UA local
        self.mapa = mapa_variables_locales

    def datachange_notification(self, node, val, data):
        try:
            estados = json.loads(val)
        except json.JSONDecodeError:
            print(f"Estado inválido recibido: {val}")
            return

        if "global" in estados:
            # primer ciclo del controlador: mismo estado para todos
            valor_global = estados["global"]
            for var_local in self.mapa.values():
                asyncio.create_task(var_local.write_value(valor_global))
            return

        for nombre, var_local in self.mapa.items():
            if nombre in estados:
                print(f"Reenviando estado de {nombre}: {estados[nombre]}")
                asyncio.create_task(var_local.write_value(estados[nombre]))

async def nodo_electrolisis_de_salmuera():
    # 1. Definir la dirección de tu servidor

    #creador del server local de escucha para los nodos de la electrolisis de salmuera 
    servidor_local = Server()
    servidor_local.set_endpoint("opc.tcp://0.0.0.0:4841/Electrolisis_Salmuera/")
    servidor_local.set_server_name("Electrolisis_Salmuera")

    await servidor_local.init()
    ns_local = await servidor_local.register_namespace("http://electrolisis.salmuera.cl/local")

    

    #nodos con sus respectivas variables a medir de el tubo de H2
    obj_tubo_h2 = await servidor_local.nodes.objects.add_object(ns_local, "Tubo_recolector_H2")
    var_presion_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Concentracion", 0.0)
    var_impurezas_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Impurezas", False)
    var_estado_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Estado", "NORMAL")
    var_firma_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Firma", "")


    #nodos con sus respectivas variables a medir de el tubo de CL2
    obj_tubo_cl2 = await servidor_local.nodes.objects.add_object(ns_local, "Tubo_recolector_CL2")
    var_presion_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Concentracion", 0.0)
    var_impurezas_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Impurezas", False)
    var_estado_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Estado", "NORMAL")
    var_firma_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Firma", "")

    #nodos con sus respectivas variables a medir de el deposito de H2
    obj_deposito_h2 = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_H2")
    var_presion_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Presion", 0.0)
    var_cantidad_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Cantidad", 0.0)
    var_estado_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Estado", "NORMAL")
    var_firma_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Firma", "")

    #nodos con sus respectivas variables a medir de el deposito de CL2
    obj_deposito_cl2 = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_CL2")
    var_presion_deposito_cl2 = await obj_deposito_cl2.add_variable(ns_local, "Presion", 0.0)
    var_cantidad_deposito_cl2 = await obj_deposito_cl2.add_variable(ns_local, "Cantidad", 0.0)
    var_estado_deposito_cl2 = await obj_deposito_cl2.add_variable(ns_local, "Estado", "NORMAL")
    var_firma_deposito_cl2 = await obj_deposito_cl2.add_variable(ns_local, "Firma", "")

    #nodos con sus respectivas variables a medir de el deposito de NaOH
    obj_deposito_naoh = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_NaOH")
    var_presion_deposito_naoh = await obj_deposito_naoh.add_variable(ns_local, "Concentracion", 0.0)
    var_cantidad_deposito_naoh = await obj_deposito_naoh.add_variable(ns_local, "Cantidad", 0.0)
    var_estado_deposito_naoh = await obj_deposito_naoh.add_variable(ns_local, "Estado", "NORMAL")
    var_firma_deposito_naoh = await obj_deposito_naoh.add_variable(ns_local, "Firma", "")

    #inicialización de variables de tubo de H2
    await var_presion_tubo_h2.set_writable()
    await var_concentracion_tubo_h2.set_writable()
    await var_impurezas_tubo_h2.set_writable()
    await var_estado_tubo_h2.set_writable()

    #inicialización de variables de tubo de CL2
    await var_presion_tubo_cl2.set_writable()
    await var_concentracion_tubo_cl2.set_writable()
    await var_impurezas_tubo_cl2.set_writable()
    await var_estado_tubo_cl2.set_writable()

    #inicialización de variables de deposito de H2
    await var_presion_deposito_h2.set_writable()
    await var_cantidad_deposito_h2.set_writable()
    await var_estado_deposito_h2.set_writable()

    #inicialización de variables de deposito de CL2
    await var_presion_deposito_cl2.set_writable()
    await var_cantidad_deposito_cl2.set_writable()
    await var_estado_deposito_cl2.set_writable()

    #inicialización de variables de deposito de CL2
    await var_presion_deposito_naoh.set_writable()
    await var_cantidad_deposito_naoh.set_writable()
    await var_estado_deposito_naoh.set_writable()

    #firmas escribibles (las publica el nodo intermedio/sensores)
    await var_firma_tubo_h2.set_writable()
    await var_firma_tubo_cl2.set_writable()
    await var_firma_deposito_h2.set_writable()
    await var_firma_deposito_cl2.set_writable()
    await var_firma_deposito_naoh.set_writable()

    await servidor_local.start()
    print("Servidor del Proceso Salmuera escuchando en puerto 4841...")
    
    #conexion con servidor central en puerto correspondiente 
    url_server_central = "opc.tcp://server:4840/freeopcua/server/"
    cliente = Client(url=url_server_central)


    try:
        # 2. Establecer la conexión
        print(f"Conectando al servidor OPC UA en {url_server_central} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        #usar el namespace del server centrar para buscar las variables a actualizar
        ns_server_central = await cliente.get_namespace_index("http://redes.servidor_opcua.cl/procesos")

        # Obtener la variable específica a actualizar para cada nodo        
        server_tubo_h2_salmuera = await cliente.nodes.root.get_child(
        ["0:Objects", f"{ns_server_central}:Server_Salmuera", f"{ns_server_central}:Datos_Tubo_H2"]
)       
        server_tubo_cl2_salmuera = await cliente.nodes.root.get_child(
        ["0:Objects", f"{ns_server_central}:Server_Salmuera", f"{ns_server_central}:Datos_Tubo_CL2"]
)       
        server_deposito_h2_salmuera = await cliente.nodes.root.get_child(
        ["0:Objects", f"{ns_server_central}:Server_Salmuera", f"{ns_server_central}:Datos_Deposito_H2"]
)       
        server_deposito_cl2_salmuera = await cliente.nodes.root.get_child(
        ["0:Objects", f"{ns_server_central}:Server_Salmuera", f"{ns_server_central}:Datos_Deposito_CL2"]
)       
        server_deposito_naoh_salmuera = await cliente.nodes.root.get_child(
        ["0:Objects", f"{ns_server_central}:Server_Salmuera", f"{ns_server_central}:Datos_Deposito_NaOH"]
)
        server_estado_salmuera = await cliente.nodes.root.get_child(
        ["0:Objects", f"{ns_server_central}:Server_Salmuera", f"{ns_server_central}:Estado_Salmuera"]
)
        
        mapa_variables_locales = {
            "tubo_h2_salmuera": var_estado_tubo_h2,
            "tubo_cl2_salmuera": var_estado_tubo_cl2,
            "deposito_h2_salmuera": var_estado_deposito_h2,
            "deposito_cl2_salmuera": var_estado_deposito_cl2,
            "deposito_naoh_salmuera": var_estado_deposito_naoh,
        }
        handler = EstadoHandler(mapa_variables_locales)
        sub = await cliente.create_subscription(300, handler)
        await sub.subscribe_data_change(server_estado_salmuera)


        # 5. Bucle de publicación 
        while True:
            # Escribir el jason de datos al servidor

            presion = await var_presion_tubo_h2.read_value()
            concentracion = await var_concentracion_tubo_h2.read_value()
            impurezas = await var_impurezas_tubo_h2.read_value()
            firma = await var_firma_tubo_h2.read_value()
            firma_ok = verificar(firma, [presion, concentracion, impurezas])
            if firma and not firma_ok:
                print("MANIPULADO: la firma del Tubo H2 no cuadra, datos alterados en transito")
            datos_tubo_h2 = {
                "presion": presion,  # leer presión
                "concentracion": concentracion,  # leer concentración
                "impurezas": impurezas,  # leer impurezas
                "firma_valida": firma_ok
            }
            #trasformamos datos a json y los enviamos al servidor central
            json_datos_tubo_h2 = json.dumps(datos_tubo_h2)
            print(f"Publicando datos de Tubo H2 al servidor central: {json_datos_tubo_h2}")
            await server_tubo_h2_salmuera.write_value(json_datos_tubo_h2)

            presion = await var_presion_tubo_cl2.read_value()
            concentracion = await var_concentracion_tubo_cl2.read_value()
            impurezas = await var_impurezas_tubo_cl2.read_value()
            firma = await var_firma_tubo_cl2.read_value()
            firma_ok = verificar(firma, [presion, concentracion, impurezas])
            if firma and not firma_ok:
                print("MANIPULADO: la firma del Tubo CL2 no cuadra, datos alterados en transito")
            datos_tubo_cl2 = {
                "presion": presion,  # leer presión
                "concentracion": concentracion,  # leer concentración
                "impurezas": impurezas,  # leer impurezas
                "firma_valida": firma_ok
            }
            #trasformamos datos a json y los enviamos al servidor central
            json_datos_tubo_cl2 = json.dumps(datos_tubo_cl2)
            print(f"Publicando datos de Tubo CL2 al servidor central: {json_datos_tubo_cl2}")
            await server_tubo_cl2_salmuera.write_value(json_datos_tubo_cl2)

            presion = await var_presion_deposito_h2.read_value()
            cantidad = await var_cantidad_deposito_h2.read_value()
            firma = await var_firma_deposito_h2.read_value()
            firma_ok = verificar(firma, [presion, cantidad])
            if firma and not firma_ok:
                print("MANIPULADO: la firma del Deposito H2 no cuadra, datos alterados en transito")
            datos_deposito_h2 = {
                "presion": presion,  # leer presión
                "cantidad": cantidad,  # leer cantidad
                "firma_valida": firma_ok
            }
            #trasformamos datos a json y los enviamos al servidor central
            json_datos_deposito_h2 = json.dumps(datos_deposito_h2)
            print(f"Publicando datos de Deposito H2 al servidor central: {json_datos_deposito_h2}")
            await server_deposito_h2_salmuera.write_value(json_datos_deposito_h2)

            presion = await var_presion_deposito_cl2.read_value()
            cantidad = await var_cantidad_deposito_cl2.read_value()
            firma = await var_firma_deposito_cl2.read_value()
            firma_ok = verificar(firma, [presion, cantidad])
            if firma and not firma_ok:
                print("MANIPULADO: la firma del Deposito CL2 no cuadra, datos alterados en transito")
            datos_deposito_cl2 = {
                "presion": presion,  # leer presión
                "cantidad": cantidad,  # leer cantidad
                "firma_valida": firma_ok
            }
            #trasformamos datos a json y los enviamos al servidor central
            json_datos_deposito_cl2 = json.dumps(datos_deposito_cl2)
            print(f"Publicando datos de Deposito CL2 al servidor central: {json_datos_deposito_cl2}")
            await server_deposito_cl2_salmuera.write_value(json_datos_deposito_cl2)

            concentracion = await var_presion_deposito_naoh.read_value()  # esta variable guarda la concentracion
            cantidad = await var_cantidad_deposito_naoh.read_value()
            firma = await var_firma_deposito_naoh.read_value()
            firma_ok = verificar(firma, [concentracion, cantidad])
            if firma and not firma_ok:
                print("MANIPULADO: la firma del Deposito NaOH no cuadra, datos alterados en transito")
            datos_deposito_naoh = {
                "presion": concentracion,  # leer presión
                "cantidad": cantidad,  # leer cantidad
                "firma_valida": firma_ok
            }
            #trasformamos datos a json y los enviamos al servidor central
            json_datos_deposito_naoh = json.dumps(datos_deposito_naoh)
            print(f"Publicando datos de NaOH al servidor central: {json_datos_deposito_naoh}")
            await server_deposito_naoh_salmuera.write_value(json_datos_deposito_naoh)

            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error en la conexión: {e}")
    finally:
        # 6. Desconectar limpiamente al terminar
        await cliente.disconnect()
        print("Nodo desconectado.")

if __name__ == "__main__":
    asyncio.run(nodo_electrolisis_de_salmuera())


