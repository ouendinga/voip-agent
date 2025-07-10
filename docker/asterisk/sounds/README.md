# Archivos de Audio para Asterisk

Esta carpeta contiene archivos de audio personalizados para Asterisk.

Puedes agregar aquí:
- Mensajes de bienvenida personalizados (.wav, .gsm)
- Música en espera (.wav, .gsm)
- Tonos de llamada personalizados
- Anuncios de IVR

## Formatos soportados:
- WAV (recomendado)
- GSM
- ALAW/ULAW

## Ejemplo de uso en el dialplan:
```
exten => 1000,1,Playback(custom-welcome)
```
