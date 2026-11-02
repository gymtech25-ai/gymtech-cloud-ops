#!/usr/bin/env python3
"""
GYMTECH - Facebook Auto-Responder 24/7 (Cloud Native Worker)
Diseñado para correr en Render, Koyeb, Railway o VPS.
Monitorea la Fan Page mediante Meta Graph API oficial, responde con
Spintax anti-bloqueo y expone un endpoint /health para mantener el servicio activo.
"""
import os
import sys
import json
import time
import random
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import requests

# Soporte UTF-8
if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configuración desde Variables de Entorno
PAGE_ID = os.environ.get("FB_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
GRAPH_API_VERSION = os.environ.get("FB_GRAPH_API_VERSION", "v19.0")
POLL_INTERVAL_SEC = int(os.environ.get("POLL_INTERVAL_SEC", "180")) # 3 minutos por defecto
PORT = int(os.environ.get("PORT", "8080"))

YOUTUBE_DEFAULT_SEARCH = os.environ.get("YOUTUBE_DEFAULT_SEARCH", "GYMTECH INQUEBRANTABLE")

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "replied_comments_cloud.json"

# Plantillas Spintax Blindadas Anti-Spam
SPINTAX_TEMPLATES = [
    "{¡Claro|Te la comparto|Aquí la tienes|A darle con toda|A romper marcas} @{name}! {Búscalo en YouTube como:|Entra a YouTube y busca:} {query} {Cuéntame en qué minuto sentiste el fallo 🔥|Luego me dices qué tal la pegada de esos bajos 💪|A romperla hoy con toda la disciplina ⚡}",
    "{¡Saludos|Qué tal|Buenas hermano} @{name}! {Para escuchar la sesión completa entra a YouTube y busca:|Encuéntralo en YouTube buscando:} {query} {¡Hoy duele, mañana brilla! 🔥|Deja tu marca en los comentarios de YouTube 👊}",
    "@{name} {¡Listo bro!|¡Servido atleta!|¡Ahí te va!} {Ponte los audífonos y búscalo en YouTube:|Míralo completo en YouTube buscando:} {query} {A romper límites hoy 💪|¡Modo Bestia activado! ⚡}"
]

def resolve_spintax(text: str) -> str:
    pattern = r"\{([^{}]+)\}"
    while re.search(pattern, text):
        def pick(m):
            return random.choice(m.group(1).split("|"))
        text = re.sub(pattern, pick, text)
    return text

def generate_reply(name: str, query: str) -> str:
    template = random.choice(SPINTAX_TEMPLATES)
    first_name = name.split()[0] if name else "atleta"
    raw = template.replace("{name}", first_name).replace("{query}", query)
    return resolve_spintax(raw)

def load_replied_ids() -> set:
    if not STATE_FILE.exists():
        return set()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_replied_id(comment_id: str):
    replied = load_replied_ids()
    replied.add(comment_id)
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(replied), f, indent=2)
    except Exception as e:
        print(f"[!] Error al persistir comment ID: {e}")


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Servidor HTTP simple para Health Checks de Render / Koyeb."""
    def do_GET(self):
        if self.path in ["/", "/health", "/status"]:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            status_data = {
                "status": "healthy",
                "service": "gymtech-facebook-auto-responder",
                "page_id_configured": bool(PAGE_ID),
                "timestamp": int(time.time())
            }
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silenciar logs ruidosos de peticiones HTTP en consola
        return


def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"[+] Health server activo en puerto {PORT} (Escuchando /health)...")
    server.serve_forever()


def responder_comentarios_loop():
    """Bucle 24/7 de monitoreo y respuesta automática."""
    print("=" * 70)
    print("🚀 INICIANDO MONITOR 24/7 DE FACEBOOK (GRAPH API)")
    print(f"Fan Page ID: {PAGE_ID or 'NO CONFIGURADO'}")
    print(f"Intervalo de escaneo: {POLL_INTERVAL_SEC} segundos")
    print("=" * 70)

    if not PAGE_ID or not ACCESS_TOKEN:
        print("[!] ADVERTENCIA: FB_PAGE_ID o FB_PAGE_ACCESS_TOKEN no están configurados.")
        print("[!] El servidor de salud permanecerá activo pero no podrá consultar Graph API.")

    base_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
    replied_ids = load_replied_ids()
    print(f"[*] Comentarios previamente respondidos cargados: {len(replied_ids)}")

    while True:
        try:
            if PAGE_ID and ACCESS_TOKEN:
                # 1. Obtener los últimos posts publicados con sus comentarios
                feed_url = f"{base_url}/{PAGE_ID}/published_posts"
                params = {
                    "fields": "id,message,created_time,comments.limit(25){id,from,message,created_time}",
                    "limit": 5,
                    "access_token": ACCESS_TOKEN
                }
                res = requests.get(feed_url, params=params, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    posts = data.get("data", [])
                    for post in posts:
                        comments = post.get("comments", {}).get("data", [])
                        for c in comments:
                            c_id = c.get("id")
                            c_from = c.get("from", {})
                            c_user_id = c_from.get("id")
                            user_name = c_from.get("name", "atleta")

                            # Omitir si ya se respondió o si el comentario es de la propia página
                            if c_id in replied_ids or c_user_id == PAGE_ID:
                                continue

                            reply_body = generate_reply(user_name, YOUTUBE_DEFAULT_SEARCH)
                            print(f"\n[+] Nuevo comentario de '{user_name}' detectado en post {post.get('id')}!")
                            print(f"    Respuesta: \"{reply_body}\"")

                            # Publicar respuesta como comentario hijo
                            post_reply_url = f"{base_url}/{c_id}/comments"
                            reply_res = requests.post(
                                post_reply_url,
                                data={"message": reply_body, "access_token": ACCESS_TOKEN},
                                timeout=15
                            )

                            if reply_res.status_code == 200:
                                print(f"    ✅ Respuesta enviada con éxito a {user_name}.")
                                save_replied_id(c_id)
                                replied_ids.add(c_id)
                            else:
                                print(f"    [!] Error al responder: {reply_res.text}")

                            # Pausa humana de seguridad anti-detección
                            delay = random.randint(15, 30)
                            time.sleep(delay)

                elif res.status_code == 400:
                    print(f"[!] Error de token o permisos de Graph API: {res.text}")
                else:
                    print(f"[!] Respuesta inesperada de Facebook: HTTP {res.status_code}")

        except Exception as e:
            print(f"[!] Excepción en ciclo de monitoreo: {e}")

        # Esperar hasta el próximo ciclo
        time.sleep(POLL_INTERVAL_SEC)


def main():
    # 1. Iniciar servidor de salud en un hilo secundario
    t_server = threading.Thread(target=start_health_server, daemon=True)
    t_server.start()

    # 2. Iniciar bucle principal de auto-respuesta
    responder_comentarios_loop()


if __name__ == "__main__":
    main()
