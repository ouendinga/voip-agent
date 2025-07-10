#!/usr/bin/env python3
"""
STT/TTS Service - Microservicio para Speech-to-Text y Text-to-Speech
"""

import os
import sys
import time
from datetime import datetime


def main():
    """Función principal del servicio STT/TTS"""
    print(f"[{datetime.now()}] STT/TTS Service iniciado")
    print(f"[{datetime.now()}] Variables de entorno:")
    print(f"  - RABBITMQ_HOST: {os.getenv('RABBITMQ_HOST', 'N/A')}")
    print(f"  - RABBITMQ_USER: {os.getenv('RABBITMQ_USER', 'N/A')}")
    
    print(f"[{datetime.now()}] Servicio ejecutándose. Presiona Ctrl+C para detener.")
    
    try:
        while True:
            # Simulación de trabajo
            print(f"[{datetime.now()}] STT/TTS Service trabajando...")
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"[{datetime.now()}] Deteniendo STT/TTS Service...")
        sys.exit(0)

if __name__ == "__main__":
    main()
