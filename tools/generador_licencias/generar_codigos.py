#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR EXTERNO DE CÓDIGOS DE ACTIVACIÓN - PUNTO DE VENTA QR
==============================================================
Este script se ejecuta ÚNICAMENTE en la computadora del dueño/administrador.
NUNCA se incluye en el APK de Android.
Utiliza criptografía asimétrica RSA-2048 (SHA256withRSA) con la clave privada
para firmar lotes de hasta 100,000+ códigos únicos de licencia y exportarlos a CSV.
"""

import argparse
import base64
import csv
import os
import subprocess
import sys
import uuid
from datetime import datetime


def firmar_payload_openssl(payload_str: str, private_key_path: str) -> str:
    proceso = subprocess.Popen(
        ["openssl", "dgst", "-sha256", "-sign", private_key_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    firma_bytes, error = proceso.communicate(payload_str.encode("utf-8"))
    if proceso.returncode != 0:
        raise RuntimeError(f"Error al firmar con OpenSSL: {error.decode('utf-8')}")
    firma_b64 = base64.urlsafe_b64encode(firma_bytes).decode("ascii").rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(payload_str.encode("utf-8")).decode("ascii").rstrip("=")
    return f"PDV1.{payload_b64}.{firma_b64}"


def generar_lote(cantidad: int, vencimiento: str, salida_csv: str, private_key_path: str):
    print(f"Generando {cantidad} códigos de activación firmados digitalmente...")
    fecha_emision = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(salida_csv, mode="w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(["ID_LICENCIA", "FECHA_EMISION", "FECHA_VENCIMIENTO", "PLAN", "CODIGO_ACTIVACION"])
        for i in range(1, cantidad + 1):
            sufijo = uuid.uuid4().hex[:6].upper()
            id_licencia = f"LIC-{i:06d}-{sufijo}"
            payload = f"{id_licencia}|{vencimiento}|FULL"
            codigo_firmado = firmar_payload_openssl(payload, private_key_path)
            writer.writerow([id_licencia, fecha_emision, vencimiento, "FULL", codigo_firmado])
            if i % 1000 == 0:
                print(f"  -> {i}/{cantidad} códigos generados...")
    print(f"¡Completado! Lote exportado exitosamente en: {salida_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de licencias RSA-2048 para Punto de Venta QR")
    parser.add_argument("--cantidad", type=int, default=100, help="Cantidad de códigos a generar (ej. 100000)")
    parser.add_argument("--vencimiento", type=str, default="2099-12-31", help="Fecha de expiración YYYY-MM-DD")
    parser.add_argument("--salida", type=str, default="lote_licencias.csv", help="Archivo CSV de salida")
    parser.add_argument("--key", type=str, default="private_key.pem", help="Ruta a la clave privada PEM")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = args.key if os.path.exists(args.key) else os.path.join(script_dir, args.key)
    out_path = args.salida if os.path.isabs(args.salida) else os.path.join(script_dir, args.salida)

    generar_lote(args.cantidad, args.vencimiento, out_path, key_path)
