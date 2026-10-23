# Sistema de Generación de Licencias Criptográficas - Punto de Venta QR

Esta carpeta (`/tools/generador_licencias/`) es para uso **exclusivo del dueño en su computadora (PC/Mac/Linux)** y **NO se empaqueta dentro del archivo APK de Android**.

## Arquitectura de Seguridad

1. **Criptografía Asimétrica (RSA-2048 / SHA256withRSA)**:
   - `private_key.pem`: Clave privada (solo en la computadora del dueño).
   - `public_key.pem`: Clave pública (embebida y ofuscada dentro de la app Android).
2. **Formato del Código de Activación**:
   - Estructura: `PDV1.<PAYLOAD_BASE64URL>.<FIRMA_RSA2048_BASE64URL>`
   - Contenido del Payload: `ID_LICENCIA|FECHA_VENCIMIENTO|PLAN` (ejemplo: `LIC-00001|2099-12-31|FULL`).
3. **Vinculación al Dispositivo y Cifrado SQLite**:
   - Al activar un código, la app verifica la firma digital RSA-2048 contra la clave pública embebida.
   - Calcula la huella única del hardware (`ANDROID_ID` + hash SHA-256 de placa, modelo, marca y hardware).
   - Cifra con **AES-256-GCM** el vínculo `(código + huella_dispositivo + firma)` y lo guarda en SQLite (`licencia_activacion`).
   - En cada inicio verifica tanto la firma digital de la APK como la coincidencia exacta del dispositivo.

## Cómo generar lotes de 100,000 códigos en su PC

### Con Python 3:
```bash
python3 generar_codigos.py --cantidad 100000 --vencimiento 2099-12-31 --salida lote_100k.csv
```

### Con Node.js:
```bash
node generar_codigos.js 100000 2099-12-31 lote_100k.csv
```
