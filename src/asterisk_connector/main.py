#!/usr/bin/env python3
"""
Asterisk Connector - Microservicio para conectar con Asterisk
"""

import os
import sys
import time
from datetime import datetime


def main():
    """Función principal del conector Asterisk"""
    print(f"[{datetime.now()}] Asterisk Connector iniciado")
    print(f"[{datetime.now()}] Variables de entorno:")
    print(f"  - ASTERISK_HOST: {os.getenv('ASTERISK_HOST', 'N/A')}")
    print(f"  - ASTERISK_AMI_PORT: {os.getenv('ASTERISK_AMI_PORT', 'N/A')}")
    print(f"  - ASTERISK_AMI_USER: {os.getenv('ASTERISK_AMI_USER', 'N/A')}")
    print(f"  - RABBITMQ_HOST: {os.getenv('RABBITMQ_HOST', 'N/A')}")
    print(f"  - RABBITMQ_USER: {os.getenv('RABBITMQ_USER', 'N/A')}")
    
    print(f"[{datetime.now()}] Servicio ejecutándose. Presiona Ctrl+C para detener.")
    
    try:
        while True:
            # Simulación de trabajo
            print(f"[{datetime.now()}] Asterisk Connector trabajando...")
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"[{datetime.now()}] Deteniendo Asterisk Connector...")
        sys.exit(0)

if __name__ == "__main__":
    main()
