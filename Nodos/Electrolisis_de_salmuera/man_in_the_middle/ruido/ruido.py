import asyncio
import sys
from asyncua import Client

async def control_ruido():

    if len(sys.argv) < 2 or sys.argv[1].lower() not in ['true', 'false']:
        print("Uso: python inyectar_ruido.py [true|false]")
        return
    
    valor_objetivo = sys.argv[1].lower() == 'true'

    url_mitm = "opc.tcp://e_salmuera_falso:4841/Electrolisis_Salmuera/"
    cliente = Client(url=url_mitm)

    #conectar con servidor de mitm
    try:
        print(f"Conectando al servidor MitM {url_mitm} ...")
        await cliente.connect()
        print("¡Conectado exitosamente!")

        ns_local = await cliente.get_namespace_index("http://electrolisis.salmuera.cl/local")

        #buscar datos en server
        nodo_alterar = await cliente.nodes.root.get_child(
            ["0:Objects", f"{ns_local}:Configuracion", f"{ns_local}:Alterar"]
        )

        print(f"Cambiando el estado de 'Alterar' a: {valor_objetivo}...")
        await nodo_alterar.write_value(valor_objetivo)
        print("¡Estado modificado correctamente en el servidor!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await cliente.disconnect()

if __name__ == "__main__":
    asyncio.run(control_ruido())
