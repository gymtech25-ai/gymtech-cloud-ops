# ⚡ GYMTECH Cloud Operations

Sistema integral de operaciones en la nube para **GYMTECH**, diseñado con arquitectura desacoplada para operar **24/7 de forma 100% gratuita o de bajísimo costo**:

1. **Supervisor de Canal de YouTube** ➔ Corre en **GitHub Actions** cada hora (auditoría algorítmica 2026, retención, optimización de títulos/tags).
2. **Auto-Responder 24/7 de Facebook** ➔ Corre como Worker continuo en **Render / Koyeb** conectado a GitHub (Meta Graph API + Spintax anti-baneo + servidor de salud).
3. **Músculo Pesado de IA y Audio** ➔ Corre en **Kaggle** con GPU Nvidia T4 gratuita bajo demanda vía API.

---

## 📁 Estructura del Repositorio

```text
gymtech-cloud-ops/
├── .github/
│   └── workflows/
│       ├── youtube_supervisor.yml    # Cron horario de YouTube en GitHub Actions
│       └── kaggle_dispatch.yml       # Lanzador de tareas pesadas en Kaggle GPU
├── services/
│   ├── facebook_auto_responder/
│   │   ├── auto_responder_cloud.py   # Daemon 24/7 con Graph API y Spintax
│   │   └── requirements.txt
│   ├── youtube_supervisor/
│   │   ├── youtube_supervisor.py     # Auditor y optimizador de videos 2026
│   │   └── requirements.txt
│   └── kaggle_bridge/
│       ├── kaggle_bridge.py          # Conector API para kernels y datasets
│       ├── sample_kernel/            # Kernel plantilla para procesamiento GPU
│       └── requirements.txt
├── scripts/
│   ├── export_youtube_token_b64.py   # Extrae token local a Base64 para GitHub
│   ├── reauth_youtube.py             # Reautenticación interactiva navegador
│   └── test_local.py                 # Validador de salud e integración
├── Dockerfile                        # Despliegue en contenedor (Koyeb / Cloud Run)
├── Procfile                          # Despliegue en PaaS (Render / Railway)
├── render.yaml                       # Configuración de 1-clic para Render
└── README.md
```

---

## 🚀 Guía de Despliegue Paso a Paso

### Paso 1: Subir este Repositorio a tu GitHub

Abre tu terminal en `D:\AG_Proyects\gymtech-cloud-ops` y ejecuta:

```bash
git init
git add .
git commit -m "feat: GYMTECH Cloud Operations inicial"
git branch -M main
# Reemplaza con la URL de tu repositorio privado en GitHub:
git remote add origin https://github.com/TU_USUARIO/gymtech-cloud-ops.git
git push -u origin main
```

---

### Paso 2: Configurar Secretos en GitHub (GitHub Secrets)

En tu repositorio de GitHub, ve a **Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ **New repository secret** y añade:

| Secreto | Descripción | Dónde obtenerlo |
| :--- | :--- | :--- |
| `YOUTUBE_TOKEN_PICKLE_B64` | Token de acceso a YouTube en Base64 | Abre `scripts/youtube_token_secret.txt` y copia todo el texto |
| `NOTIFICATION_WEBHOOK` *(Opcional)* | Webhook de Discord o Telegram para recibir alertas | Configuración de canal en Discord/Telegram |
| `KAGGLE_USERNAME` *(Opcional)* | Tu usuario de Kaggle | Perfil de Kaggle |
| `KAGGLE_KEY` *(Opcional)* | Clave API de Kaggle | Descargada desde tu perfil en `kaggle.json` |

> 💡 **Nota sobre el Token de YouTube:** Si alguna vez necesitas renovar la sesión de YouTube, solo ejecuta:
> ```bash
> python scripts/reauth_youtube.py
> ```
> Abrirá el navegador, autorizarás la cuenta y actualizará `youtube_token_secret.txt` automáticamente.

---

### Paso 3: Desplegar el Auto-Responder de Facebook 24/7 (En Render)

1. Ve a [Render.com](https://render.com/) e inicia sesión con tu cuenta de **GitHub**.
2. Haz clic en **New +** ➔ **Web Service** (o **Background Worker**).
3. Selecciona tu repositorio `gymtech-cloud-ops`.
4. Render detectará automáticamente el archivo `Procfile` y `render.yaml`.
5. En la sección **Environment Variables**, añade:
   * `FB_PAGE_ID` = Tu ID de página de Facebook de GYMTECH.
   * `FB_PAGE_ACCESS_TOKEN` = Tu Token de acceso de página (Page Access Token de Meta Developers).
   * `POLL_INTERVAL_SEC` = `180` (intervalo de 3 minutos).
   * `YOUTUBE_DEFAULT_SEARCH` = `GYMTECH INQUEBRANTABLE` (o el título que quieras promocionar).
6. Haz clic en **Create Web Service**. ¡Listo! El bot estará escuchando y respondiendo 24/7 con Spintax y el servidor `/health` activo.

---

### Paso 4: Validar el Supervisor de YouTube en GitHub Actions

1. En tu repositorio de GitHub, ve a la pestaña **Actions**.
2. Verás el flujo **GYMTECH YouTube Cloud Supervisor**.
3. Haz clic en **Run workflow** (o espera a que se ejecute en su próxima hora programada).
4. El supervisor descargará tus videos, evaluará su score de optimización algorítmica y generará el artefacto `audit_report.json` visible en GitHub.
