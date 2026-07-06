import asyncio
from opcua_server import ServidorOPC
from controlador import Controlador

async def main():
    servidor = ServidorOPC()
    await servidor.iniciar()

    controler = Controlador()
    
    try:
        while True:
            # Reporte de los datos de los nodos OPC UA
            reporte_json, reporte_dict = await servidor.generar_reporte()

            # Evaluadmos los datos del reporte y tomamos decisiones
            estado_agua, estado_salmuera = controler.recibir_datos(reporte_dict)

            # Publicamos los resultados de vuelta en el servidor central
            await servidor.publicar_estados(estado_agua, estado_salmuera)

            print(f"Ciclo evaluado -> agua: {estado_agua} | salmuera: {estado_salmuera}")

            await asyncio.sleep(2)
            
    except KeyboardInterrupt:
        print("Deteniendo servidor...")
        await servidor.detener()

if __name__ == "__main__":
    asyncio.run(main())