#!/usr/bin/env python3
"""
GYMTECH - Kaggle Cloud Dispatcher & Heavy Compute Bridge
Permite lanzar y monitorear tareas pesadas en Kaggle (GPU T4/P100 gratuita)
desde Antigravity local o desde GitHub Actions.
"""
import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path

# Soporte UTF-8
if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def setup_kaggle_credentials():
    """Configura credenciales de Kaggle desde variables de entorno si están presentes."""
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    if username and key:
        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        kaggle_json = kaggle_dir / "kaggle.json"
        with open(kaggle_json, "w", encoding="utf-8") as f:
            json.dump({"username": username, "key": key}, f)
        if sys.platform != "win32":
            os.chmod(kaggle_json, 0o600)
        print(f"[+] Credenciales de Kaggle configuradas desde variables de entorno para usuario '{username}'.")


def push_kernel(kernel_dir: Path):
    """Envía un kernel de Kaggle a la nube para ejecución con GPU."""
    setup_kaggle_credentials()
    if not kernel_dir.exists():
        raise FileNotFoundError(f"No existe el directorio de kernel: {kernel_dir}")

    meta_file = kernel_dir / "kernel-metadata.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"Falta kernel-metadata.json en {kernel_dir}")

    print(f"[*] Enviando kernel a Kaggle desde: {kernel_dir}...")
    cmd = ["kaggle", "kernels", "push", "-p", str(kernel_dir)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Kernel enviado exitosamente:\n{res.stdout}")
    else:
        print(f"[!] Error al enviar kernel:\n{res.stderr}")
        sys.exit(res.returncode)


def check_status(kernel_slug: str):
    """Verifica el estado de ejecución de un kernel en Kaggle."""
    setup_kaggle_credentials()
    cmd = ["kaggle", "kernels", "status", kernel_slug]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)


def download_output(kernel_slug: str, output_dir: Path):
    """Descarga los resultados procesados por Kaggle (pesos LoRA, JSONs de audio, etc.)."""
    setup_kaggle_credentials()
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Descargando resultados de '{kernel_slug}' hacia: {output_dir}...")
    cmd = ["kaggle", "kernels", "output", kernel_slug, "-p", str(output_dir)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Archivos descargados exitosamente:\n{res.stdout}")
    else:
        print(f"[!] Error al descargar resultados:\n{res.stderr}")


def main():
    parser = argparse.ArgumentParser(description="GYMTECH Kaggle Compute Bridge")
    subparsers = parser.add_subparsers(dest="action")

    p_push = subparsers.add_parser("push", help="Enviar y ejecutar un kernel en Kaggle")
    p_push.add_argument("--dir", required=True, help="Ruta al directorio del kernel")

    p_status = subparsers.add_parser("status", help="Ver estado de un kernel")
    p_status.add_argument("--slug", required=True, help="Slug del kernel (usuario/nombre-kernel)")

    p_out = subparsers.add_parser("output", help="Descargar archivos resultantes de un kernel")
    p_out.add_argument("--slug", required=True, help="Slug del kernel")
    p_out.add_argument("--dest", default="./output", help="Directorio de destino")

    args = parser.parse_args()

    if args.action == "push":
        push_kernel(Path(args.dir))
    elif args.action == "status":
        check_status(args.slug)
    elif args.action == "output":
        download_output(args.slug, Path(args.dest))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
