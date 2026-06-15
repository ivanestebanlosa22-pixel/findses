"""
upload_youtube.py — Sube shorts a TU canal de YouTube (OAuth).
================================================================

IMPORTANTE: esto se ejecuta EN TU PC, con TU sesión de Google. Ni Claude ni
ningún servidor tiene acceso a tu cuenta. La primera vez se abre el navegador
para que autorices; luego se guarda un token local (`youtube_token.json`) y ya
no hace falta volver a iniciar sesión.

--------------------------------------------------------------------------------
CONFIGURACIÓN (una sola vez, ~10-15 min)
--------------------------------------------------------------------------------
1. Entra en https://console.cloud.google.com/  e inicia sesión.
2. Crea un proyecto (arriba, "Select project" -> "New project").
3. Menú -> "APIs & Services" -> "Library" -> busca "YouTube Data API v3"
   -> ENABLE.
4. "APIs & Services" -> "OAuth consent screen":
      - User type: External -> Create
      - Rellena nombre de app y tu email; en "Test users" AÑADE tu propio
        correo de Google (el del canal). Guarda.
5. "APIs & Services" -> "Credentials" -> "Create credentials"
   -> "OAuth client ID" -> Application type: "Desktop app" -> Create.
6. Descarga el JSON y guárdalo en la carpeta del proyecto como
   `client_secret.json` (o pon su ruta en .env como YOUTUBE_CLIENT_SECRET).

Instala dependencias:
    pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

--------------------------------------------------------------------------------
USO
--------------------------------------------------------------------------------
    python3 upload_youtube.py storage/shorts/verano.mp4 --privacy private

Por seguridad el valor por defecto es `private` (solo tú lo ves) para que
revises antes de hacerlo público. Cuando estés conforme: --privacy public.

Cada vídeo usa su archivo `<video>.json` (título, descripción y tags) generado
por make_short.py.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "youtube_token.json"


def _load_env(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def get_service():
    """Autentica (OAuth) y devuelve el cliente de la YouTube Data API."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Faltan dependencias. Ejecuta:\n  pip install "
                 "google-api-python-client google-auth-oauthlib google-auth-httplib2")

    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "client_secret.json")
    if not Path(client_secret).exists():
        sys.exit(f"No encuentro '{client_secret}'. Sigue los pasos del "
                 f"encabezado de este archivo para crearlo.")

    creds = None
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(TOKEN_FILE).write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def upload_video(video: Path, privacy: str = "private", service=None) -> str:
    """Sube un vídeo usando su sidecar <video>.json. Devuelve el ID del vídeo."""
    from googleapiclient.http import MediaFileUpload

    video = Path(video)
    meta_file = video.with_suffix(".json")
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    else:
        meta = {"title": video.stem, "description": "", "tags": []}

    service = service or get_service()
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "categoryId": "22",                     # People & Blogs
        },
        "status": {
            "privacyStatus": privacy,               # private | unlisted | public
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video), chunksize=-1, resumable=True,
                            mimetype="video/mp4")
    req = service.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"  Subiendo {video.name} ...")
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"    {int(status.progress() * 100)}%")
    vid = resp["id"]
    print(f"  [OK] https://youtu.be/{vid}  (privacidad: {privacy})")
    return vid


def main() -> int:
    _load_env()
    ap = argparse.ArgumentParser(description="Sube shorts a YouTube.")
    ap.add_argument("videos", nargs="+", help="Rutas de .mp4 a subir")
    ap.add_argument("--privacy", default="private",
                    choices=["private", "unlisted", "public"])
    args = ap.parse_args()

    service = get_service()
    for v in args.videos:
        try:
            upload_video(Path(v), args.privacy, service)
        except Exception as e:
            print(f"  [ERROR] {v}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
