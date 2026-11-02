#!/usr/bin/env python3
"""
Exportador de credenciales de YouTube a Base64 para GitHub Secrets.
Lee el token.pickle local de GYMTECH_WORK, valida su vigencia y muestra
la cadena base64 lista para copiar en GitHub Secrets como YOUTUBE_TOKEN_PICKLE_B64.
"""
import base64
import os
import pickle
import sys
from pathlib import Path

# Soporte UTF-8 para Windows consola
if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Rutas estándar
LOCAL_TOKEN = Path("D:/AG_Proyects/GYMTECH_WORK/token.pickle")
ALT_TOKEN = Path(__file__).resolve().parent.parent / "config" / "token.pickle"

def main():
    token_path = None
    if LOCAL_TOKEN.exists():
        token_path = LOCAL_TOKEN
    elif ALT_TOKEN.exists():
        token_path = ALT_TOKEN
    elif len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        token_path = Path(sys.argv[1])
    
    if not token_path:
        print("[!] No se encontró token.pickle en las ubicaciones habituales.")
        print("    Por favor especifica la ruta: python export_youtube_token_b64.py <ruta_a_token.pickle>")
        sys.exit(1)

    print(f"[*] Leyendo token desde: {token_path}")
    with open(token_path, "rb") as f:
        data = f.read()

    try:
        creds = pickle.loads(data)
        print(f"[+] Token deserializado correctamente.")
        print(f"    - Válido: {creds.valid}")
        print(f"    - Expirado: {creds.expired}")
        print(f"    - Tiene Refresh Token: {bool(creds.refresh_token)}")
    except Exception as e:
        print(f"[!] Advertencia al inspeccionar credenciales: {e}")

    b64_str = base64.b64encode(data).decode("utf-8")
    
    output_file = Path(__file__).resolve().parent / "youtube_token_secret.txt"
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(b64_str)

    print("\n" + "=" * 70)
    print("🎯 TOKEN EXPORTADO CON ÉXITO")
    print("=" * 70)
    print(f"El secreto se ha guardado en: {output_file}")
    print("\nPara usarlo en GitHub:")
    print("1. Ve a tu repositorio en GitHub -> Settings -> Secrets and variables -> Actions")
    print("2. Crea un nuevo secreto llamado: YOUTUBE_TOKEN_PICKLE_B64")
    print("3. Pega el contenido guardado en youtube_token_secret.txt")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
