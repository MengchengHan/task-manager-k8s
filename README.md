# Task Manager - Kubernetes (K8s)

Este proyecto despliega una aplicación de gestión de tareas completa (API, base de datos y proxy inverso) en un clúster local de Kubernetes (`kind`).

## Arquitectura

El sistema está compuesto por los siguientes servicios:
- **API**: Aplicación Python (Flask/FastAPI) que sirve como backend.
- **Base de Datos**: Instancia de PostgreSQL para persistir las tareas.
- **Nginx**: Actúa como proxy inverso y balanceador de carga frontal.

La infraestructura en Kubernetes incluye despliegues (`Deployments`), servicios (`Services`), Autoescalado de Pods (`HPA`) y la gestión de secretos.

## Requisitos Previos

Asegúrate de tener instaladas las siguientes herramientas en tu máquina local:
- [Docker](https://docs.docker.com/get-docker/)
- [Kind (Kubernetes in Docker)](https://kind.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Inicio Rápido

Para levantar toda la infraestructura (imágenes, clúster kind y manifiestos de Kubernetes) simplemente ejecuta el script principal:

```bash
./start.sh
```

El script se encargará automáticamente de:
1. Construir las imágenes Docker de la API y Nginx y subirlas al registry local.
2. Crear un clúster Kubernetes utilizando `kind`.
3. Crear los secretos necesarios (como contraseñas de la DB).
4. Desplegar los recursos de la carpeta `/k8s/`.
5. Exponer la aplicación usando Port-Forwarding.

Una vez esté todo listo y la terminal te lo indique, podrás acceder a la aplicación en:
👉 **http://localhost:8080**

## Estructura del Proyecto

- `api/`: Código fuente de la API en Python (app.py, requirements.txt, Dockerfile).
- `nginx/`: Configuración del servidor Nginx y su Dockerfile.
- `k8s/`: Manifiestos YAML para el despliegue en Kubernetes de los diferentes servicios y el HPA de la API.
- `start.sh`: Script principal de orquestación local para levantar el entorno.
- `createCluster.sh`: Script utilizado para inicializar el clúster `kind`.
- `imagesEnRegistry.sh`: Script para construir y enviar las imágenes al registry local de Kubernetes.

## Desmontar el Clúster

Cuando hayas terminado, puedes eliminar el clúster local de Kind con el siguiente comando:

```bash
kind delete cluster --name task-manager
```
*(Asegúrate de introducir el nombre de tu clúster si el script lo nombra diferente)*