# Usar una imagen base de Alpine e instalar Asterisk
FROM alpine:3.18

# Instalar Asterisk y herramientas adicionales
RUN apk add --no-cache \
	asterisk \
	asterisk-sounds-en \
	net-tools \
	iputils \
	vim \
	bash

# Crear directorios necesarios
RUN mkdir -p /etc/asterisk /var/lib/asterisk/sounds

# Copiar configuraciones de Asterisk (dialplan, sip.conf, manager.conf, etc.)
# Se montarán con un volumen en docker-compose, así que esta copia es un fallback
COPY conf/asterisk.conf /etc/asterisk/asterisk.conf
COPY conf/modules.conf /etc/asterisk/modules.conf
COPY conf/logger.conf /etc/asterisk/logger.conf
COPY conf/sip.conf /etc/asterisk/sip.conf
COPY conf/extensions.conf /etc/asterisk/extensions.conf
COPY conf/manager.conf /etc/asterisk/manager.conf

# Copiar sonidos si existen (opcional)
# COPY sounds/ /var/lib/asterisk/sounds/

# Exponer puertos (definidos en docker-compose)
EXPOSE 5060/udp 5061/tcp 5038 8088

# Comando para iniciar Asterisk en primer plano
CMD ["asterisk", "-f"]