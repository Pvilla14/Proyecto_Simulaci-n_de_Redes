# Proyecto_Simulaci-n_de_Redes
Proyecto semestral del ramo Redes de Computadoras, donde se implementa la comunciación entre servicios de datos de reacciones químicas

Para ejecutar el servidor de electrolisis hay que situarse en la carpeta de /Electrolisis_de_salmuera y ejecutar el siguiente comando

```
docker compose up --build
```

Para activar/desactivar la inyección de ruido desde MITM ejecutar el siguiente comando

```
docker compose up --build ruido_<on/off>
```

Para visualizar los datos desde navegador: **http://localhost:8000/**
