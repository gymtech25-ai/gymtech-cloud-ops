#!/usr/bin/env python3
"""
Reautenticador interactivo de YouTube API para GYMTECH.
Abre el navegador una vez para renovar el token OAuth cuando expire,
guarda el nuevo token.pickle y genera automáticamente la clave base64 para GitHub Secrets.
"""
import base64
import os
import pickle
import sys
from pathlib import Path

# Soporte UTF-8 consola Windows
if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("[!] Error: Requiere google-auth-oauthlib y google-api-python-client")
    sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

CLIENT_SECRETS = Path("D:/AG_Proyects/GYMTECH_WORK/client_secrets.json")
OUTPUT_TOKEN = Path("D:/AG_Proyects/gymtech-cloud-ops/config/token.pickle")
OUTPUT_WORK_TOKEN = Path("D:/AG_Proyects/GYMTECH_WORK/token.pickle")
SECRET_TXT = Path("D:/AG_Proyects/gymtech-cloud-ops/scripts/youtube_token_secret.txt")

def main():
    if not CLIENT_SECRETS.exists():
        print(f"[!] No se encontró {CLIENT_SECRETS}")
        sys.exit(1)

    print("=" * 70)
    print("🔑 INICIANDO REAUTENTICACIÓN DE YOUTUBE (OAUTH)")
    print("=" * 70)
    print("Se abrirá una ventana en tu navegador para autorizar la app de GYMTECH.")
    print("Por favor inicia sesión con la cuenta administradora del canal.")

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
    creds = flow.run_local_server(port=0)

    OUTPUT_TOKEN.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_TOKEN, "wb") as f:
        pickle.dump(creds, f)

    # Actualizar también la ruta de GYMTECH_WORK
    with open(OUTPUT_WORK_TOKEN, "wb") as f:
        pickle.dump(creds, f)

    b64_str = base64.b64encode(pickle.dumps(creds)).decode("utf-8")
    with open(SECRET_TXT, "w", encoding="utf-8") as f:
        f.write(b64_str)

    print("\n" + "=" * 70)
    print("✅ REAUTENTICACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print(f"Token actualizado en: {OUTPUT_TOKEN}")
    print(f"Secreto para GitHub actualizado en: {SECRET_TXT}")
    print("\nCopia el valor de youtube_token_secret.txt y pégalo en:")
    print("GitHub -> Repositorio -> Settings -> Secrets -> YOUTUBE_TOKEN_PICKLE_B64")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
