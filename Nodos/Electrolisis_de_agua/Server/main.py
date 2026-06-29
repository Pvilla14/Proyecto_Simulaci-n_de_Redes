import asyncio
from opcua_server import ServidorOPC

async def main():
    servidor = ServidorOPC()
    
    await servidor.iniciar()
    
    try:
        while True:
            await asyncio.sleep(1)
            # Aquí irá el ciclo principal donde lees las variables de los nodos OPC UA
            # pasas esos valores a evaluador.evaluar_datos()
            # y tomas decisiones (seguir o detener la reacción)
            
    except KeyboardInterrupt:
        print("Deteniendo servidor...")
        await servidor.detener()

if __name__ == "__main__":
    asyncio.run(main())