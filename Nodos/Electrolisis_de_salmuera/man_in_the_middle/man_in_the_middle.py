import asyncio
import json
from asyncua import Client, Server


async def nodo_man_in_the_middle():
    # 1. Definir la dirección de tu servidor

    #creador del server local de escucha para los nodos de la electrolisis de salmuera 
    servidor_local = Server()
    servidor_local.set_endpoint("opc.tcp://0.0.0.0:4841/Electrolisis_Salmuera/")
    servidor_local.set_server_name("Electrolisis_Salmuera")


    await servidor_local.init()
    ns_local = await servidor_local.register_namespace("http://electrolisis.salmuera.cl/local")

    #nodo para cambiar el estado de inyección de ruido
    obj_config = await servidor_local.nodes.objects.add_object(ns_local, "Configuracion")
    var_alter = await obj_config.add_variable(ns_local, "Alterar", False)

    #nodos con sus respectivas variables a medir de el tubo de H2
    obj_tubo_h2 = await servidor_local.nodes.objects.add_object(ns_local, "Tubo_recolector_H2")
    var_presion_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Concentracion", 0.0)
    var_impurezas_tubo_h2 = await obj_tubo_h2.add_variable(ns_local, "Impurezas", False)
    
    #nodos con sus respectivas variables a medir de el tubo de CL2
    obj_tubo_cl2 = await servidor_local.nodes.objects.add_object(ns_local, "Tubo_recolector_CL2")
    var_presion_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Presion", 0.0)
    var_concentracion_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Concentracion", 0.0)
    var_impurezas_tubo_cl2 = await obj_tubo_cl2.add_variable(ns_local, "Impurezas", False)

    #nodos con sus respectivas variables a medir de el deposito de H2
    obj_deposito_h2 = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_H2")
    var_presion_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Presion", 0.0)
    var_cantidad_deposito_h2 = await obj_deposito_h2.add_variable(ns_local, "Cantidad", 0.0)
    
    #nodos con sus respectivas variables a medir de el deposito de CL2
    obj_deposito_cl2 = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_CL2")
    var_presion_deposito_cl2 = await obj_deposito_cl2.add_variable(ns_local, "Presion", 0.0)
    var_cantidad_deposito_cl2 = await obj_deposito_cl2.add_variable(ns_local, "Cantidad", 0.0)

    #nodos con sus respectivas variables a medir de el deposito de NaOH
    obj_deposito_naoh = await servidor_local.nodes.objects.add_object(ns_local, "Deposito_NaOH")
    var_concentracion_deposito_naoh = await obj_deposito_naoh.add_variable(ns_local, "Concentracion", 0.0)
    var_cantidad_deposito_naoh = await obj_deposito_naoh.add_variable(ns_local, "Cantidad", 0.0)
    
    #inicializaciín de variable alter
    await var_alter.set_writable()

    #inicialización de variables de tubo de H2
    await var_presion_tubo_h2.set_writable()
    await var_concentracion_tubo_h2.set_writable()
    await var_impurezas_tubo_h2.set_writable()

    #inicialización de variables de tubo de CL2
    await var_presion_tubo_cl2.set_writable()
    await var_concentracion_tubo_cl2.set_writable()
    await var_impurezas_tubo_cl2.set_writable()

    #inicialización de variables de deposito de H2
    await var_presion_deposito_h2.set_writable()
    await var_cantidad_deposito_h2.set_writable()

    #inicialización de variables de deposito de CL2
    await var_presion_deposito_cl2.set_writable()
    await var_cantidad_deposito_cl2.set_writable()

    #inicialización de variables de deposito de CL2
    await var_concentracion_deposito_naoh.set_writable()
    await var_cantidad_deposito_naoh.set_writable()
    
    await servidor_local.start()
    print("Servidor del Proceso Agua escuchando en puerto 4841...")
    
    #conexion con servidor central en puerto correspondiente 
    url_nodo_salmuera = "opc.tcp://e_salmuera_real:4841/Electrolisis_Salmuera/server/"
    cliente = Client(url=url_nodo_salmuera)

    conectado = False
    try:
        # 2. Establecer la conexión
        print(f"Conectando al servidor OPC UA en {url_nodo_salmuera} ...")
        await cliente.connect()
        conectado = True
        print("¡Conectado exitosamente!")

        #usar el namespace del server salmuera para buscar las variables a actualizar
        ns_server_salmuera = await cliente.get_namespace_index("http://electrolisis.salmuera.cl/local")

        # Obtener la variable específica a actualizar para cada nodo  
        
        # Tubo H2       
        nodo_t_presion_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Tubo_recolector_H2", f"{ns_server_salmuera}:Presion"]
        )
        nodo_t_concentracion_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Tubo_recolector_H2", f"{ns_server_salmuera}:Concentracion"]
        )
        nodo_t_impurezas_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Tubo_recolector_H2", f"{ns_server_salmuera}:Impurezas"]
        )
        
        # Tubo Cl2
        nodo_t_presion_Cl2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Tubo_recolector_CL2", f"{ns_server_salmuera}:Presion"]
        )
        nodo_t_concentracion_Cl2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Tubo_recolector_CL2", f"{ns_server_salmuera}:Concentracion"]
        )
        nodo_t_impurezas_Cl2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Tubo_recolector_CL2", f"{ns_server_salmuera}:Impurezas"]
        )

        # Deposito H2
        nodo_d_presion_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Deposito_H2", f"{ns_server_salmuera}:Presion"]
        )
        nodo_d_cantidad_H2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Deposito_H2", f"{ns_server_salmuera}:Cantidad"]
        )

        # Deposito Cl2
        nodo_d_presion_Cl2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Deposito_CL2", f"{ns_server_salmuera}:Presion"]
        )
        nodo_d_cantidad_Cl2 = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Deposito_CL2", f"{ns_server_salmuera}:Cantidad"]
        )
        
        # Deposito NaOH
        nodo_d_concentracion_NaOH = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Deposito_NaOH", f"{ns_server_salmuera}:Concentracion"]
        )
        nodo_d_cantidad_NaOH = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_server_salmuera}:Deposito_NaOH", f"{ns_server_salmuera}:Cantidad"]
        )

        # 5. Bucle de publicación 
        while True:

            alter = await var_alter.read_value()

            # Tubo H2
            presion_actual = await var_presion_tubo_h2.read_value()
            concentracion_actual = await var_concentracion_tubo_h2.read_value()
            impurezas_actual = await var_impurezas_tubo_h2.read_value()

            if alter:
                print(f"Inyectando ruido en tubo H2. Valores originales: presión = {presion_actual}, concentración = {concentracion_actual}, impureza = {impurezas_actual}")

            await nodo_t_presion_H2.write_value(presion_actual + alter * ruido())
            await nodo_t_concentracion_H2.write_value(concentracion_actual + alter * ruido())
            await nodo_t_impurezas_H2.write_value(bool(impurezas_actual + alter * ruido()))
            
            # Tubo Cl2
            presion_actual = await var_presion_tubo_cl2.read_value()
            concentracion_actual = await var_concentracion_tubo_cl2.read_value()
            impurezas_actual = await var_impurezas_tubo_cl2.read_value()
            
            if alter:
                print(f"Inyectando ruido en tubo Cl2. Valores originales: presión = {presion_actual}, concentración = {concentracion_actual}, impureza = {impurezas_actual}")

            await nodo_t_presion_Cl2.write_value(presion_actual + alter * ruido())
            await nodo_t_concentracion_Cl2.write_value(concentracion_actual + alter * ruido())
            await nodo_t_impurezas_Cl2.write_value(bool(impurezas_actual + alter * ruido()))

            # Deposito H2
            presion_actual = await var_presion_deposito_h2.read_value()  # leer presión
            cantidad_actual = await var_cantidad_deposito_h2.read_value()  # leer cantidad
            
            if alter:
                print(f"Inyectando ruido en deposito H2. Valores originales: presión = {presion_actual}, cantidad = {cantidad_actual}")

            await nodo_d_presion_H2.write_value(presion_actual + alter * ruido())
            await nodo_d_cantidad_H2.write_value(cantidad_actual + alter * ruido())

            # Deposito Cl2
            presion_actual = await var_presion_deposito_cl2.read_value()  # leer presión
            cantidad_actual = await var_cantidad_deposito_cl2.read_value()  # leer cantidad
            
            if alter:
                print(f"Inyectando ruido en deposito Cl2. Valores originales: presión = {presion_actual}, cantidad = {cantidad_actual}")

            await nodo_d_presion_Cl2.write_value(presion_actual + alter * ruido())
            await nodo_d_cantidad_Cl2.write_value(cantidad_actual + alter * ruido())

            # Deposito NaOH
            concentracion_actual = await var_concentracion_deposito_naoh.read_value()  # leer presión
            cantidad_actual = await var_cantidad_deposito_naoh.read_value()  # leer cantidad
            
            if alter:
                print(f"Inyectando ruido en deposito NaOH. Valores originales: concentración = {concentracion_actual}, cantidad = {cantidad_actual}")

            await nodo_d_concentracion_NaOH.write_value(concentracion_actual + alter * ruido())
            await nodo_d_cantidad_NaOH.write_value(cantidad_actual + alter * ruido())

            await asyncio.sleep(2) # Enviar datos cada 2 segundos

    except Exception as e:
        print(f"Error en la conexión: {e}")
    finally:
        if conectado:
            await cliente.disconnect()
            print("Nodo desconectado.")
        await servidor_local.stop()

def ruido():
    return 1


if __name__ == "__main__":
    asyncio.run(nodo_man_in_the_middle())