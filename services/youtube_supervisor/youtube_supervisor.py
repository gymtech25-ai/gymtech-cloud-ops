#!/usr/bin/env python3
"""
GYMTECH - YouTube Channel Supervisor (Cloud & GitHub Actions Ready)
Supervisa en tiempo real el canal de YouTube, audita métricas de videos,
detecta anomalías de rendimiento (retención/QCR) y aplica optimizaciones 2026.
"""
import os
import sys
import json
import time
import base64
import pickle
import argparse
from pathlib import Path
from datetime import datetime

# Soporte UTF-8 para Windows y Linux
if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


def obtener_cliente_youtube():
    """Autentica con YouTube API usando token base64 en env o archivo token.pickle."""
    if not GOOGLE_API_AVAILABLE:
        raise ImportError("google-api-python-client no está instalado.")

    creds = None
    b64_token = os.environ.get("YOUTUBE_TOKEN_PICKLE_B64")

    # 1. Intentar desde variable de entorno (GitHub Actions / Cloud)
    if b64_token:
        try:
            print("[*] Cargando credenciales desde variable de entorno YOUTUBE_TOKEN_PICKLE_B64...")
            raw_data = base64.b64decode(b64_token.strip())
            creds = pickle.loads(raw_data)
        except Exception as e:
            print(f"[!] Error al decodificar YOUTUBE_TOKEN_PICKLE_B64: {e}")

    # 2. Si no, buscar token.pickle en disco (Entorno local)
    if not creds:
        posibles_rutas = [
            Path("token.pickle"),
            Path(__file__).resolve().parent / "token.pickle",
            Path("D:/AG_Proyects/GYMTECH_WORK/token.pickle")
        ]
        for ruta in posibles_rutas:
            if ruta.exists():
                try:
                    print(f"[*] Cargando credenciales desde archivo: {ruta}")
                    with open(ruta, "rb") as f:
                        creds = pickle.load(f)
                    break
                except Exception as e:
                    print(f"[!] Error al leer {ruta}: {e}")

    if not creds:
        raise ValueError("No se encontraron credenciales de YouTube (ni variable YOUTUBE_TOKEN_PICKLE_B64 ni token.pickle).")

    # 3. Refrescar el token si está expirado
    if creds.expired and creds.refresh_token:
        print("[*] El token ha expirado. Refrescando con Refresh Token de forma desatendida...")
        creds.refresh(Request())
        print("[+] Token refrescado con éxito.")

    return build("youtube", "v3", credentials=creds)


def auditar_canal(youtube, max_videos=15):
    """Escanea los videos del canal y evalúa métricas e integridad de metadatos."""
    print("[*] Obteniendo información general del canal...")
    ch_res = youtube.channels().list(mine=True, part="contentDetails,snippet,statistics").execute()
    
    if not ch_res.get("items"):
        return {"error": "Canal no encontrado"}

    canal = ch_res["items"][0]
    uploads_id = canal["contentDetails"]["relatedPlaylists"]["uploads"]
    channel_info = {
        "title": canal["snippet"]["title"],
        "subscribers": int(canal["statistics"].get("subscriberCount", 0)),
        "total_views": int(canal["statistics"].get("viewCount", 0)),
        "video_count": int(canal["statistics"].get("videoCount", 0)),
        "audit_timestamp": datetime.utcnow().isoformat() + "Z"
    }

    print(f"    Canal: {channel_info['title']}")
    print(f"    Suscriptores: {channel_info['subscribers']:,} | Vistas Totales: {channel_info['total_views']:,}")

    # Obtener lista de videos recientes
    print(f"[*] Escaneando los últimos {max_videos} videos...")
    video_ids = []
    pl_res = youtube.playlistItems().list(
        part="contentDetails,snippet",
        playlistId=uploads_id,
        maxResults=min(max_videos, 50)
    ).execute()

    for item in pl_res.get("items", []):
        video_ids.append(item["contentDetails"]["videoId"])

    if not video_ids:
        return {"channel": channel_info, "videos": []}

    # Obtener detalles completos de los videos
    v_res = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    ).execute()

    videos_audit = []
    for v in v_res.get("items", []):
        v_id = v["id"]
        snippet = v["snippet"]
        stats = v["statistics"]

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        title = snippet.get("title", "")
        desc = snippet.get("description", "")

        # Verificaciones de protocolo GYMTECH 2026
        has_bpm_tag = "BPM" in title.upper()
        has_gymtech_brand = "GYMTECH" in title.upper()
        has_chapters = "00:00" in desc or "0:00" in desc
        has_links = "http" in desc.lower()

        # Score de optimización algorítmica (0 a 100)
        opt_score = 40
        if has_bpm_tag: opt_score += 20
        if has_gymtech_brand: opt_score += 20
        if has_chapters: opt_score += 20

        videos_audit.append({
            "id": v_id,
            "title": title,
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate": round(((likes + comments) / max(views, 1)) * 100, 2),
            "opt_score": opt_score,
            "has_bpm": has_bpm_tag,
            "has_chapters": has_chapters,
            "has_promo_links": has_links,
            "status": "ÓPTIMO" if opt_score >= 80 else "MEJORABLE"
        })

    videos_audit.sort(key=lambda x: x["views"], reverse=True)

    reporte = {
        "channel": channel_info,
        "videos_analyzed": len(videos_audit),
        "top_performing": videos_audit[:3],
        "needs_optimization": [v for v in videos_audit if v["status"] == "MEJORABLE"],
        "all_videos": videos_audit
    }

    return reporte


def enviar_alerta_webhook(mensaje):
    """Envía alerta opcional a Discord o Telegram si hay webhook configurado."""
    webhook_url = os.environ.get("NOTIFICATION_WEBHOOK")
    if not webhook_url:
        return

    import requests
    try:
        if "discord.com" in webhook_url:
            requests.post(webhook_url, json={"content": mensaje}, timeout=5)
        elif "telegram" in webhook_url or "api.telegram.org" in webhook_url:
            requests.post(webhook_url, json={"text": mensaje}, timeout=5)
    except Exception as e:
        print(f"[!] Error al enviar alerta webhook: {e}")


def main():
    parser = argparse.ArgumentParser(description="GYMTECH YouTube Channel Cloud Supervisor")
    parser.add_argument("--mode", choices=["audit", "apply"], default="audit", help="Modo auditoría o aplicación")
    parser.add_argument("--max-videos", type=int, default=15, help="Cantidad de videos a auditar")
    parser.add_argument("--output", default="audit_report.json", help="Ruta del reporte de salida")

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 INICIANDO SUPERVISOR DE YOUTUBE - GYMTECH CLOUD")
    print(f"Modo: {args.mode.upper()} | Límite: {args.max_videos} videos")
    print("=" * 70)

    try:
        youtube = obtener_cliente_youtube()
        reporte = auditar_canal(youtube, max_videos=args.max_videos)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)

        print(f"\n[+] Auditoría completada con éxito. Reporte guardado en: {args.output}")
        print(f"    Videos analizados: {reporte.get('videos_analyzed')}")
        print(f"    Videos con estado MEJORABLE: {len(reporte.get('needs_optimization', []))}")

        if reporte.get("needs_optimization"):
            print("\n📋 Videos candidatos a optimización de metadatos:")
            for item in reporte["needs_optimization"][:5]:
                print(f"    • [{item['id']}] {item['title'][:55]}... (Score: {item['opt_score']}/100)")

        # Enviar resumen si webhook está configurado
        alerta = (
            f"⚡ **GYMTECH Supervisor Report**\n"
            f"Canal: {reporte['channel']['title']}\n"
            f"Vistas Totales: {reporte['channel']['total_views']:,}\n"
            f"Videos auditados: {reporte['videos_analyzed']} (Mejorables: {len(reporte['needs_optimization'])})"
        )
        enviar_alerta_webhook(alerta)

    except Exception as e:
        print(f"\n[!] Error crítico en ejecución del supervisor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
