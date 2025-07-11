FROM python:3.9-slim-buster

WORKDIR /app


# Instalar dependencias desde requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los archivos proto y generar el código Python de gRPC
COPY proto/ /proto/
RUN python -m grpc_tools.protoc -I/proto --python_out=/app --grpc_python_out=/app /proto/asterisk_service.proto /proto/stt_tts_service.proto

# Copiar el código de la aplicación
COPY src/stt_tts_interface /app

# Asumiendo que tu entrada principal es main.py
CMD ["python", "main.py"]