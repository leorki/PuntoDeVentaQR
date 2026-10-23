#!/usr/bin/env node
/**
 * GENERADOR EXTERNO DE CÓDIGOS DE ACTIVACIÓN (Node.js) - PUNTO DE VENTA QR
 * =========================================================================
 * Uso en la PC del dueño:
 *   node generar_codigos.js 100000 2099-12-31 lote_100k_licencias.csv
 *
 * Nunca se incluye en el APK de Android. Usa la clave privada RSA-2048 para
 * firmar cada código y exportarlo a CSV compatible con Excel.
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const cantidad = parseInt(process.argv[2] || '100', 10);
const vencimiento = process.argv[3] || '2099-12-31';
const archivoSalida = process.argv[4] || path.join(__dirname, 'lote_licencias_node.csv');
const privateKeyPath = path.join(__dirname, 'private_key.pem');

if (!fs.existsSync(privateKeyPath)) {
  console.error('Error: No se encontró private_key.pem en', privateKeyPath);
  process.exit(1);
}

const privateKeyPem = fs.readFileSync(privateKeyPath, 'utf8');

function toBase64Url(buffer) {
  return buffer
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function firmarLicencia(idLicencia, fechaExp) {
  const payload = `${idLicencia}|${fechaExp}|FULL`;
  const signer = crypto.createSign('RSA-SHA256');
  signer.update(payload, 'utf8');
  signer.end();
  const signature = signer.sign(privateKeyPem);
  return `PDV1.${toBase64Url(Buffer.from(payload, 'utf8'))}.${toBase64Url(signature)}`;
}

console.log(`Generando ${cantidad} licencias firmadas con RSA-2048...`);
const stream = fs.createWriteStream(archivoSalida, { encoding: 'utf8' });
stream.write('ID_LICENCIA,FECHA_EMISION,FECHA_VENCIMIENTO,PLAN,CODIGO_ACTIVACION\n');

const fechaEmision = new Date().toISOString().slice(0, 10);

for (let i = 1; i <= cantidad; i++) {
  const randomSuffix = crypto.randomBytes(3).toString('hex').toUpperCase();
  const idLicencia = `LIC-${String(i).padStart(6, '0')}-${randomSuffix}`;
  const codigo = firmarLicencia(idLicencia, vencimiento);
  stream.write(`${idLicencia},${fechaEmision},${vencimiento},FULL,${codigo}\n`);
}

stream.end(() => {
  console.log(`¡Listo! Archivo generado en: ${archivoSalida}`);
});
