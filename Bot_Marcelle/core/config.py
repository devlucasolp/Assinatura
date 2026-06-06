"""
Configurações centrais — lidas do .env via _Env, expostas como dataclasses imutáveis.

Hierarquia (cada classe tem ≤ 3 campos — R8):
  Settings
  ├── AppConfig          (host, port, env)
  ├── InfraConfig
  │   ├── EvolutionConfig (url, key, instance)
  │   └── StorageConfig   (postgres_url, redis_url)
  ├── ServicesConfig
  │   ├── AiConfig
  │   │   ├── GeminiConfig  (api_key)
  │   │   └── AsanaConfig   (token, workspace_gid, project_gid, section_gid, user_gid)
  │   └── GoogleDriveConfig (token_file, root_folder_id)
  └── BotConfig
      ├── GabiConfig      (primary: PhoneNumber, phones: AuthorizedPhones)
      └── MessagesConfig
          ├── AutoReplyMessages (meeting, event)
          └── StatusMessages    (meeting_on, event_on, off, greeting)
"""

from dataclasses import dataclass
from functools import lru_cache
from pydantic_settings import BaseSettings
from core.domain import PhoneNumber, AuthorizedPhones


# ---------------------------------------------------------------------------
# Leitor de variáveis de ambiente — uso interno apenas
# ---------------------------------------------------------------------------

class _Env(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_ENV: str = "production"

    EVOLUTION_API_URL: str = ""
    EVOLUTION_API_KEY: str = ""
    EVOLUTION_INSTANCE: str = ""

    GABI_PHONE: str = ""
    GABI_PHONE_2: str = ""

    GEMINI_API_KEY: str = ""

    POSTGRES_URL: str = ""
    REDIS_URL: str = ""

    ASANA_ACCESS_TOKEN: str = ""
    ASANA_WORKSPACE_GID: str = ""
    ASANA_PROJECT_GID: str = ""
    ASANA_SECTION_GID: str = ""
    ASANA_USER_GID: str = ""

    GOOGLE_DRIVE_TOKEN_FILE: str = "token.json"
    GOOGLE_DRIVE_ROOT_FOLDER_ID: str = ""

    AUTO_REPLY_MEETING_MSG: str = (
        "Oi! Estou em reunião no momento e não consigo responder agora. "
        "Assim que terminar eu te retorno. 🙏"
    )
    AUTO_REPLY_EVENT_MSG: str = (
        "Oi! Estou em um evento no momento e com atenção limitada. "
        "Vou te responder em breve! 🙏"
    )
    STATUS_MEETING_ON_MSG: str = (
        "✅ *Modo Reunião ativado por 1 hora.*\n"
        "Quem mandar mensagem vai receber aviso automático."
    )
    STATUS_EVENT_ON_MSG: str = (
        "✅ *Modo Evento ativado por 1 hora.*\n"
        "Quem mandar mensagem vai receber aviso automático."
    )
    STATUS_OFF_MSG: str = "❌ *Auto-reply desativado.*\nBem-vinda de volta!"
    BOT_GREETING_MSG: str = (
        "Olá! Sou a *Fernanda*, secretária executiva da Gabriela.\n\n"
        "Posso ajudar com:\n\n"
        "📝 *Atas de reunião no Asana*\n"
        "Envie 'ata [assunto] | [transcrição ou notas]'\n\n"
        "✅ *Tarefas e reuniões no Asana*\n"
        "Ex: 'marca uma reunião com fulano amanhã às 15h'\n\n"
        "🔕 *Modo Ocupada*\n"
        "Envie '/meet' ou '/evento' para ligar a resposta automática, e '/fimmeet' para desligar."
    )

    model_config = {"env_file": ".env", "extra": "ignore"}


# ---------------------------------------------------------------------------
# Config groups
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int
    env: str


@dataclass(frozen=True)
class EvolutionConfig:
    url: str
    key: str
    instance: str


@dataclass(frozen=True)
class StorageConfig:
    postgres_url: str
    redis_url: str


@dataclass(frozen=True)
class InfraConfig:
    evolution: EvolutionConfig
    storage: StorageConfig


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str


@dataclass(frozen=True)
class AsanaConfig:
    token: str
    workspace_gid: str
    project_gid: str
    section_gid: str
    user_gid: str


@dataclass(frozen=True)
class GoogleDriveConfig:
    token_file: str
    root_folder_id: str


@dataclass(frozen=True)
class AiConfig:
    gemini: GeminiConfig
    asana: AsanaConfig


@dataclass(frozen=True)
class ServicesConfig:
    ai: AiConfig
    google_drive: GoogleDriveConfig


@dataclass(frozen=True)
class AutoReplyMessages:
    meeting: str
    event: str


@dataclass(frozen=True)
class StatusMessages:
    meeting_on: str
    event_on: str
    off: str
    greeting: str


@dataclass(frozen=True)
class MessagesConfig:
    auto_reply: AutoReplyMessages
    status: StatusMessages


@dataclass(frozen=True)
class GabiConfig:
    primary: PhoneNumber
    phones: AuthorizedPhones


@dataclass(frozen=True)
class BotConfig:
    gabi: GabiConfig
    messages: MessagesConfig


@dataclass(frozen=True)
class Settings:
    app: AppConfig
    infra: InfraConfig
    services: ServicesConfig
    bot: BotConfig


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

@lru_cache
def get_settings() -> Settings:
    env = _Env()

    app = AppConfig(host=env.APP_HOST, port=env.APP_PORT, env=env.APP_ENV)

    evolution = EvolutionConfig(
        url=env.EVOLUTION_API_URL,
        key=env.EVOLUTION_API_KEY,
        instance=env.EVOLUTION_INSTANCE,
    )
    storage = StorageConfig(postgres_url=env.POSTGRES_URL, redis_url=env.REDIS_URL)
    infra = InfraConfig(evolution=evolution, storage=storage)

    gemini = GeminiConfig(api_key=env.GEMINI_API_KEY)
    asana = AsanaConfig(
        token=env.ASANA_ACCESS_TOKEN,
        workspace_gid=env.ASANA_WORKSPACE_GID,
        project_gid=env.ASANA_PROJECT_GID,
        section_gid=env.ASANA_SECTION_GID,
        user_gid=env.ASANA_USER_GID,
    )
    google_drive = GoogleDriveConfig(
        token_file=env.GOOGLE_DRIVE_TOKEN_FILE,
        root_folder_id=env.GOOGLE_DRIVE_ROOT_FOLDER_ID,
    )
    ai = AiConfig(gemini=gemini, asana=asana)
    services = ServicesConfig(ai=ai, google_drive=google_drive)

    primary = PhoneNumber(env.GABI_PHONE)
    phones = AuthorizedPhones(env.GABI_PHONE, env.GABI_PHONE_2)
    gabi = GabiConfig(primary=primary, phones=phones)
    auto_reply = AutoReplyMessages(meeting=env.AUTO_REPLY_MEETING_MSG, event=env.AUTO_REPLY_EVENT_MSG)
    status_msgs = StatusMessages(
        meeting_on=env.STATUS_MEETING_ON_MSG,
        event_on=env.STATUS_EVENT_ON_MSG,
        off=env.STATUS_OFF_MSG,
        greeting=env.BOT_GREETING_MSG,
    )
    messages = MessagesConfig(auto_reply=auto_reply, status=status_msgs)
    bot = BotConfig(gabi=gabi, messages=messages)

    return Settings(app=app, infra=infra, services=services, bot=bot)
