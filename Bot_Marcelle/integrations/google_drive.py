"""
Integração com Google Drive via OAuth2.

Fluxo de autenticação:
  1. Executar setup_drive_auth.py uma vez para gerar token.json
  2. Este módulo lê token.json e auto-renova quando expira

Estrutura de pastas criadas automaticamente no Drive:
  [ROOT_FOLDER]/
  ├── Imagens/
  ├── Áudios/
  ├── Documentos/
  └── Atas/
"""

import asyncio
import io
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from core.config import get_settings
from core.logger import bot_logger

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Cache de folder_name → folder_id (por processo)
_folder_cache: dict[str, str] = {}


def _load_creds() -> Credentials:
    """
    Solicita token fresco ao Rails (credential broker).
    O Rails é responsável por refresh e persistência — Python só consome.
    """
    import json
    from integrations.rails_client import get_token_sync

    token_data = get_token_sync("google_drive")
    return Credentials.from_authorized_user_info(token_data, SCOPES)


def _get_or_create_folder(service, name: str, parent_id: str | None) -> str:
    cache_key = f"{parent_id or 'root'}/{name}"
    if cache_key in _folder_cache:
        return _folder_cache[cache_key]

    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields="files(id)", pageSize=1).execute()
    files = results.get("files", [])

    if files:
        folder_id = files[0]["id"]
    else:
        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            meta["parents"] = [parent_id]
        folder = service.files().create(body=meta, fields="id").execute()
        folder_id = folder["id"]
        bot_logger.info(f"[DRIVE] Pasta criada: '{name}' → {folder_id}")

    _folder_cache[cache_key] = folder_id
    return folder_id


def _upload_sync(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    subfolder: str,
) -> dict:
    settings = get_settings()
    services = settings.services
    google_drive = services.google_drive
    root_id = google_drive.root_folder_id or None

    creds = _load_creds()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    folder_id = _get_or_create_folder(service, subfolder, root_id)

    metadata = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=False)
    uploaded = service.files().create(
        body=metadata, media_body=media, fields="id,name,webViewLink"
    ).execute()

    # Link público de leitura
    service.permissions().create(
        fileId=uploaded["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()

    bot_logger.info(f"[DRIVE] Arquivo enviado: '{filename}' → {uploaded.get('webViewLink')}")
    return uploaded


async def upload_file(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    subfolder: str,
) -> dict:
    """Faz upload de arquivo para a subpasta correta. Retorna {id, name, webViewLink}."""
    return await asyncio.to_thread(_upload_sync, file_bytes, filename, mime_type, subfolder)


def make_filename(base: str, extension: str) -> str:
    """Gera nome de arquivo com timestamp: YYYY-MM-DD_HH-MM_base.ext"""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in base)[:40].strip("_")
    return f"{ts}_{slug}.{extension}" if slug else f"{ts}.{extension}"


MIME_TO_SUBFOLDER = {
    "image/": "Imagens",
    "audio/": "Áudios",
    "video/": "Vídeos",
    "application/pdf": "Documentos",
    "application/msword": "Documentos",
    "application/vnd.openxmlformats": "Documentos",
    "application/vnd.ms-": "Documentos",
    "text/plain": "Documentos",
}

MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",
    "audio/mp4": "m4a",
    "video/mp4": "mp4",
    "application/pdf": "pdf",
    "text/plain": "txt",
}


def resolve_subfolder(mime_type: str) -> str:
    for prefix, folder in MIME_TO_SUBFOLDER.items():
        if mime_type.startswith(prefix):
            return folder
    return "Documentos"


def resolve_extension(mime_type: str) -> str:
    return MIME_TO_EXT.get(mime_type, "bin")
