# VoIP Agent

Este proyecto es una solución para gestionar y automatizar agentes VoIP utilizando Asterisk. Permite la integración, monitoreo y administración de llamadas de manera eficiente.

## Características

- Integración con Asterisk PBX
- Microservicios Python para conectores y servicios STT/TTS
- Cola de mensajes con RabbitMQ
- Base de datos MongoDB para persistencia
- Cache con Redis
- Interfaz web de gestión de RabbitMQ
- Arquitectura basada en Docker y microservicios

## Arquitectura

El proyecto está compuesto por los siguientes servicios:

- **Asterisk**: PBX (Private Branch Exchange) para gestión de llamadas VoIP
- **RabbitMQ**: Broker de mensajes para comunicación entre microservicios
- **MongoDB**: Base de datos NoSQL para almacenamiento de datos
- **Redis**: Sistema de caché en memoria
- **Asterisk Connector**: Microservicio Python para conectar con Asterisk AMI
- **STT/TTS Service**: Microservicio Python para Speech-to-Text y Text-to-Speech

## Requisitos Previos

- Docker Desktop instalado y funcionando
- Docker Compose
- Git
- PowerShell (Windows) o Bash (Linux/Mac)

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd voip-agent
```

### 2. Verificar que Docker Desktop esté funcionando

```powershell
# Verificar versión de Docker
docker --version

# Verificar estado de Docker daemon
docker info
```

### 3. Construir y levantar todos los servicios

```powershell
# Construir y levantar todos los servicios en modo daemon (segundo plano)
docker compose up -d --build

# Alternativa: levantar con logs visibles
docker compose up --build
```

### 4. Verificar que todos los servicios estén funcionando

```powershell
# Ver estado de todos los contenedores
docker compose ps

# Ver estado con formato de tabla personalizado
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
```

## Uso del Sistema

### Comandos Principales

```powershell
# Levantar todos los servicios
docker compose up -d

# Ver logs de todos los servicios
docker compose logs

# Ver logs de un servicio específico
docker logs asterisk
docker logs asterisk_connector
docker logs stt_tts_service
docker logs rabbitmq
docker logs mongodb
docker logs redis

# Ver logs en tiempo real
docker logs -f asterisk_connector

# Detener todos los servicios
docker compose stop

# Detener y eliminar contenedores
docker compose down

# Detener, eliminar contenedores y volúmenes
docker compose down -v

# Reconstruir servicios después de cambios en código
docker compose up -d --build
```

### Acceso a Interfaces Web

#### RabbitMQ Management Interface
- **URL**: http://localhost:15672
- **Usuario**: `user`
- **Contraseña**: `password`
- **Descripción**: Interfaz web para gestionar colas, intercambios y monitorear mensajes

### Puertos Expuestos

| Servicio | Puerto | Protocolo | Descripción |
|----------|--------|-----------|-------------|
| Asterisk SIP | 5060 | UDP | Puerto principal SIP |
| Asterisk SIP TLS | 5061 | TCP | Puerto SIP seguro |
| Asterisk AMI | 5038 | TCP | Asterisk Manager Interface |
| Asterisk HTTP | 8088 | TCP | API REST de Asterisk |
| RabbitMQ AMQP | 5672 | TCP | Puerto de mensajería |
| RabbitMQ Management | 15672 | HTTP | Interfaz web de gestión |
| MongoDB | 27017 | TCP | Base de datos |
| Redis | 6379 | TCP | Cache |

## Verificación de Servicios

### Verificar Estado de Servicios

```powershell
# Ver todos los contenedores y su estado
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Ver solo contenedores activos
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Verificar Funcionalidad de Servicios

#### Asterisk
```powershell
# Ver logs de Asterisk
docker logs asterisk --tail 10

# Conectar a CLI de Asterisk
docker exec -it asterisk asterisk -r
```

#### RabbitMQ
```powershell
# Verificar API de RabbitMQ
curl -u user:password http://localhost:15672/api/overview

# Ver estado de colas
curl -u user:password http://localhost:15672/api/queues
```

#### MongoDB
```powershell
# Conectar a MongoDB
docker exec -it mongodb mongosh

# Verificar con autenticación
docker exec -it mongodb mongosh -u user -p password
```

#### Redis
```powershell
# Verificar conexión a Redis
docker exec redis redis-cli ping

# Conectar a CLI de Redis
docker exec -it redis redis-cli
```

#### Microservicios Python
```powershell
# Ver logs de asterisk_connector
docker logs asterisk_connector

# Ver logs de stt_tts_service
docker logs stt_tts_service

# Verificar que los contenedores estén ejecutándose
docker exec asterisk_connector ps aux
docker exec stt_tts_service ps aux
```

### Comandos de Depuración

```powershell
# Inspeccionar configuración de un contenedor
docker inspect asterisk

# Ver uso de recursos
docker stats

# Ver redes de Docker
docker network ls

# Ver volúmenes
docker volume ls

# Acceder al shell de un contenedor
docker exec -it asterisk /bin/bash
docker exec -it asterisk_connector /bin/bash

# Ver logs con timestamps
docker logs asterisk --timestamps

# Seguir logs en tiempo real
docker logs -f asterisk_connector
```

## Desarrollo

### Estructura del Proyecto

```
voip-agent/
├── docker-compose.yml          # Configuración de servicios
├── docker/
│   └── asterisk/               # Configuración de Asterisk
│       ├── Dockerfile
│       ├── conf/               # Archivos de configuración
│       │   ├── asterisk.conf
│       │   ├── extensions.conf
│       │   ├── logger.conf
│       │   ├── manager.conf
│       │   ├── modules.conf
│       │   └── sip.conf
│       └── sounds/             # Archivos de audio
├── proto/                      # Definiciones gRPC
│   ├── asterisk_service.proto
│   └── stt_tts_service.proto
└── src/                        # Código fuente de microservicios
    ├── asterisk_connector/     # Conector con Asterisk
    ├── common/                 # Código compartido
    ├── conversation_engine/    # Motor de conversaciones
    ├── persistence_manager/    # Gestor de persistencia
    ├── prompt_manager/         # Gestor de prompts
    └── stt_tts_interface/      # Interfaz STT/TTS
```

### Variables de Entorno

Los servicios utilizan las siguientes variables de entorno configuradas en `docker-compose.yml`:

#### Asterisk Connector
- `ASTERISK_HOST`: Hostname del servicio Asterisk
- `ASTERISK_AMI_PORT`: Puerto AMI de Asterisk (5038)
- `ASTERISK_AMI_USER`: Usuario AMI
- `ASTERISK_AMI_PASS`: Contraseña AMI
- `RABBITMQ_HOST`: Hostname de RabbitMQ
- `RABBITMQ_USER`: Usuario de RabbitMQ
- `RABBITMQ_PASS`: Contraseña de RabbitMQ

#### STT/TTS Service
- `RABBITMQ_HOST`: Hostname de RabbitMQ
- `RABBITMQ_USER`: Usuario de RabbitMQ
- `RABBITMQ_PASS`: Contraseña de RabbitMQ

## TODO's

- [ ] Cambiar el módulo obsoleto `chan_sip` por una alternativa moderna (`chan_pjsip`)
- [ ] Implementar lógica de negocio en los microservicios Python
- [ ] Agregar pruebas automatizadas
- [ ] Implementar autenticación de usuarios
- [ ] Configurar SSL/TLS para comunicaciones seguras
- [ ] Añadir monitoreo y métricas con Prometheus/Grafana
- [ ] Implementar CI/CD pipeline
- [ ] Optimizar el rendimiento del sistema
- [ ] Documentar API endpoints
- [ ] Agregar ejemplos de uso y casos de prueba

## Contribución

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).

### Resumen de la licencia:
- ✅ **Puedes**: Usar, modificar, distribuir y compartir el código
- ❌ **No puedes**: Usar el código para fines comerciales o lucrativos
- ⚠️ **Debes**: Mantener la atribución al autor original
- 🛡️ **Sin garantías**: El software se proporciona "tal como está"

Ver el archivo [LICENSE](LICENSE) para más detalles o consulta: https://creativecommons.org/licenses/by-nc/4.0/

## Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la sección de [Solución de Problemas Comunes](#solución-de-problemas-comunes)
2. Busca en los [Issues existentes](../../issues)
3. Crea un nuevo Issuee si no encuentras solución

## Notas Adicionales

### Warnings Conocidos

- **Asterisk chan_sip deprecated**: El módulo `chan_sip` está obsoleto. Se recomienda migrar a `chan_pjsip` en futuras versiones.
- **MongoDB sin autenticación**: En desarrollo, MongoDB no tiene autenticación habilitada. Configurar credenciales para producción.

### Comandos Útiles de Monitoreo

```powershell
# Ver uso de recursos en tiempo real
docker stats

# Ver logs agregados de todos los servicios
docker compose logs -f

# Limpiar contenedores e imágenes no utilizados
docker system prune -a

# Ver tamaño de imágenes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

## Solución de Problemas Comunes

### 1. Los contenedores no se levantan

**Problema**: `docker compose up` falla o los contenedores no inician correctamente.

**Soluciones**:
```powershell
# Verificar que Docker Desktop esté funcionando
docker info

# Limpiar contenedores e imágenes previas
docker compose down -v
docker system prune -a

# Reconstruir desde cero
docker compose up -d --build --force-recreate
```

### 2. Error "Port already in use"

**Problema**: Error indicando que un puerto ya está en uso.

**Soluciones**:
```powershell
# Verificar qué proceso está usando el puerto (ejemplo puerto 5060)
netstat -ano | findstr :5060

# Detener servicios que puedan estar usando los puertos
docker compose down

# Si hay procesos bloqueando puertos, terminarlos con el PID
taskkill /PID <PID> /F
```

### 3. Asterisk no responde en AMI

**Problema**: El conector no puede conectarse al AMI de Asterisk.

**Soluciones**:
```powershell
# Verificar logs de Asterisk
docker logs asterisk

# Conectar a CLI de Asterisk y verificar configuración AMI
docker exec -it asterisk asterisk -r
# En CLI de Asterisk:
# manager show settings
# manager show users
```

### 4. RabbitMQ no acepta conexiones

**Problema**: Los microservicios no pueden conectarse a RabbitMQ.

**Soluciones**:
```powershell
# Verificar estado de RabbitMQ
docker logs rabbitmq

# Verificar que RabbitMQ esté listo
docker exec rabbitmq rabbitmq-diagnostics ping

# Reiniciar RabbitMQ si es necesario
docker restart rabbitmq
```

### 5. MongoDB no se conecta

**Problema**: Error de conexión a MongoDB.

**Soluciones**:
```powershell
# Verificar logs de MongoDB
docker logs mongodb

# Conectar manualmente para probar
docker exec -it mongodb mongosh

# Verificar estado del servicio
docker exec mongodb mongosh --eval "db.runCommand('ping')"
```

### 6. Los microservicios Python fallan al iniciar

**Problema**: Los contenedores de Python se cierran inmediatamente.

**Soluciones**:
```powershell
# Ver logs detallados del microservicio
docker logs asterisk_connector
docker logs stt_tts_service

# Verificar dependencias de Python
docker exec asterisk_connector pip list
docker exec stt_tts_service pip list

# Reconstruir contenedores Python
docker compose up -d --build asterisk_connector stt_tts_service
```

### 7. Error "No space left on device"

**Problema**: Docker se queda sin espacio en disco.

**Soluciones**:
```powershell
# Limpiar imágenes, contenedores y volúmenes no utilizados
docker system prune -a --volumes

# Ver uso de espacio de Docker
docker system df

# Limpiar solo imágenes no utilizadas
docker image prune -a
```

### 8. Contenedores se reinician constantemente

**Problema**: Los contenedores entran en un bucle de reinicio.

**Soluciones**:
```powershell
# Ver logs para identificar el problema
docker logs --tail 50 <nombre_contenedor>

# Verificar límites de memoria
docker stats

# Detener servicios problemáticos temporalmente
docker compose stop <servicio>

# Verificar configuración de health checks
docker inspect <contenedor> | grep -i health
```

### 9. Problemas de red entre contenedores

**Problema**: Los contenedores no pueden comunicarse entre sí.

**Soluciones**:
```powershell
# Verificar redes de Docker
docker network ls

# Inspeccionar la red del proyecto
docker network inspect voip-agent_default

# Probar conectividad entre contenedores
docker exec asterisk_connector ping asterisk
docker exec asterisk_connector ping rabbitmq
```

### 10. Cambios en código no se reflejan

**Problema**: Los cambios en el código fuente no se ven reflejados en los contenedores.

**Soluciones**:
```powershell
# Reconstruir servicios específicos
docker compose up -d --build asterisk_connector

# Forzar recreación completa
docker compose up -d --build --force-recreate

# Verificar que los volúmenes estén correctamente montados
docker inspect asterisk_connector | grep -i mounts
```

### 11. Error en permisos de archivos (Linux/Mac)

**Problema**: Errores de permisos en archivos de configuración.

**Soluciones**:
```bash
# Ajustar permisos de archivos de configuración
sudo chmod -R 755 docker/asterisk/conf/

# Verificar propietario de archivos
ls -la docker/asterisk/conf/
```

### 12. Problemas de DNS dentro de contenedores

**Problema**: Los contenedores no pueden resolver nombres de host.

**Soluciones**:
```powershell
# Verificar resolución DNS dentro del contenedor
docker exec asterisk_connector nslookup rabbitmq
docker exec asterisk_connector ping rabbitmq

# Reiniciar Docker daemon si es necesario
# En Windows: reiniciar Docker Desktop
```

### Comandos de Diagnóstico Rápido

```powershell
# Script completo de diagnóstico
echo "=== Estado de contenedores ==="
docker compose ps

echo "=== Uso de recursos ==="
docker stats --no-stream

echo "=== Logs recientes de servicios críticos ==="
docker logs --tail 5 asterisk
docker logs --tail 5 rabbitmq
docker logs --tail 5 asterisk_connector

echo "=== Verificación de puertos ==="
netstat -ano | findstr ":5060"
netstat -ano | findstr ":5672"
netstat -ano | findstr ":15672"

echo "=== Espacio en disco ==="
docker system df
```
