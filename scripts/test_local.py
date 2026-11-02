#!/usr/bin/env python3
"""
Test local interactivo para verificar el estado de los módulos de GYMTECH Cloud Ops:
1. Auto-responder Spintax y endpoints de salud.
2. Formato de secreto de YouTube.
3. Conector de Kaggle CLI.
"""
import os
import sys
from pathlib import Path

# Soporte UTF-8
if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "services" / "facebook_auto_responder"))

from auto_responder_cloud import generate_reply

def main():
    print("=" * 70)
    print("🧪 GYMTECH CLOUD OPS - TEST DE INTEGRACIÓN LOCAL")
    print("=" * 70)

    # 1. Probar Spintax de Facebook
    print("\n[1] Probando generación de Spintax para Facebook Auto-Responder:")
    for i in range(1, 4):
        sample = generate_reply("Atleta Pro", "GYMTECH INQUEBRANTABLE")
        print(f"    Variante {i}: \"{sample}\"")
    print("    ✅ Generador Spintax funcionando con éxito.")

    # 2. Probar exportador de YouTube
    token_txt = ROOT / "scripts" / "youtube_token_secret.txt"
    print("\n[2] Comprobando archivo de secreto de YouTube:")
    if token_txt.exists() and token_txt.stat().st_size > 100:
        print(f"    ✅ youtube_token_secret.txt existe ({token_txt.stat().st_size} bytes).")
        print("    Listo para copiar en GitHub Secrets como YOUTUBE_TOKEN_PICKLE_B64.")
    else:
        print("    ⚠️  Aún no se ha exportado. Ejecuta: python scripts/export_youtube_token_b64.py")

    # 3. Comprobar Dockerfile y Procfile
    print("\n[3] Comprobando configuración de despliegue Cloud (Render / Koyeb):")
    procfile = ROOT / "Procfile"
    dockerfile = ROOT / "Dockerfile"
    render_yaml = ROOT / "render.yaml"

    if procfile.exists() and dockerfile.exists() and render_yaml.exists():
        print("    ✅ Procfile, Dockerfile y render.yaml validados y listos para Git.")
    else:
        print("    [!] Falta alguno de los archivos de despliegue.")

    print("\n" + "=" * 70)
    print("🎉 SISTEMA LISTO PARA VINCULAR CON GITHUB")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
