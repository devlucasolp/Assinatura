"""
Integração com Google Gemini API - processamento de atas e contexto inteligente
"""

import asyncio
import base64
import json
import os
import re
import tempfile
import google.generativeai as genai
from core.config import get_settings
from core.logger import gemini_logger

from core.context import get_current_instance

def _get_model():
    instance = get_current_instance()
    api_key = instance.get("gemini_api_key", "")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT_ATA = """Você é a Fernanda, uma assistente executiva inteligente e organizada.
Sua tarefa é processar transcrições ou notas brutas de reuniões e transformá-las em atas estruturadas em português brasileiro.

Gere a ata usando EXATAMENTE este formato (sem emojis, sem markdown, texto limpo):

Objetivo:
[Descreva o objetivo principal da reunião em 1-2 frases diretas]

Resumo:
[Resuma os principais pontos discutidos de forma clara, objetiva e em parágrafos ou lista. Inclua contexto relevante, decisões tomadas e alinhamentos feitos.]

Próximos passos e definições:
[Liste cada próximo passo em uma linha separada, começando com verbo no infinitivo. Inclua responsável e prazo quando mencionados.]

Regras importantes:
- Não use emojis, asteriscos ou formatação markdown
- Não invente informações que não estejam no texto original
- Seja direto e profissional
- O campo "Resumo" deve ser o mais completo possível com o que foi discutido
- O campo "Próximos passos" deve ser acionável e específico
"""


async def process_meeting_minutes(raw_text: str) -> str:
    """
    Processa transcrição/notas brutas e retorna ata estruturada.
    """
    gemini_logger.info(f"Processando ata via Gemini | tamanho do texto: {len(raw_text)} chars")
    
    model = _get_model()
    if not model:
        return "Erro: Chave do Gemini não configurada nesta instância."

    prompt = f"{SYSTEM_PROMPT_ATA}\n\nPor favor, processe a seguinte transcrição/notas da reunião e gere a ata estruturada:\n\n{raw_text}"

    response = await model.generate_content_async(prompt)
    result = response.text
    
    gemini_logger.info("Ata processada com sucesso via Gemini")
    return result


async def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """
    Transcreve um áudio usando Gemini Files API.
    Suporta formatos: ogg, mp4, mp3, wav, webm.
    Retorna o texto transcrito.
    """
    model = _get_model()
    if not model:
        return ""

    # Normaliza mime_type (Evolution pode retornar "audio/ogg; codecs=opus")
    base_mime = mime_type.split(";")[0].strip()
    ext_map = {
        "audio/ogg": ".ogg",
        "audio/mp4": ".mp4",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/webm": ".webm",
    }
    suffix = ext_map.get(base_mime, ".ogg")

    tmp_path = None
    uploaded = None
    try:
        # Salva em arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        gemini_logger.info(f"Transcrevendo áudio via Gemini | mime: {base_mime} | tamanho: {len(audio_bytes)} bytes")

        # Upload para Gemini (síncrono → executor)
        uploaded = await asyncio.to_thread(
            genai.upload_file, tmp_path, mime_type=base_mime
        )

        response = await model.generate_content_async([
            "Transcreva exatamente o que foi dito neste áudio em português brasileiro. "
            "Retorne apenas a transcrição, sem introduções ou comentários.",
            uploaded,
        ])
        result = response.text.strip()
        gemini_logger.info(f"Áudio transcrito | {len(result)} chars")
        return result

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if uploaded:
            await asyncio.to_thread(genai.delete_file, uploaded.name)


async def describe_image(image_bytes: bytes, mime_type: str = "image/jpeg", caption: str = "") -> str:
    """
    Descreve e lê o conteúdo de uma imagem usando Gemini Vision.
    Se houver legenda (caption), inclui como contexto.
    Retorna descrição detalhada / texto extraído.
    """
    model = _get_model()
    if not model:
        return ""

    base_mime = mime_type.split(";")[0].strip()
    b64_data = base64.b64encode(image_bytes).decode("utf-8")

    prompt_parts = [
        "Analise esta imagem com atenção. "
        "Se contiver texto, transcreva-o integralmente. "
        "Descreva o conteúdo visual de forma clara e completa em português brasileiro.",
    ]
    if caption:
        prompt_parts.append(f"Legenda enviada junto com a imagem: \"{caption}\"")
    prompt_parts.append({"mime_type": base_mime, "data": b64_data})

    gemini_logger.info(f"Descrevendo imagem via Gemini Vision | mime: {base_mime} | tamanho: {len(image_bytes)} bytes")
    response = await model.generate_content_async(prompt_parts)
    result = response.text.strip()
    gemini_logger.info(f"Imagem descrita | {len(result)} chars")
    return result


async def extract_asana_task_info(text: str) -> dict:
    """
    Extrai dados estruturados para criação de tarefa/reunião no Asana a partir de texto livre.
    Usa Gemini para evitar limites de cota.
    Retorna dict com: task_name, project_name, due_date, due_time, notes.
    """
    from datetime import date, timedelta

    model = _get_model()
    if not model:
        return {}

    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    today_str = today.isoformat()

    prompt = f"""Hoje é {today_str} (amanhã é {tomorrow}). Analise o texto e extraia as informações para criar uma tarefa ou reunião no Asana.

Retorne SOMENTE um JSON válido, sem markdown, sem marcações de bloco de código, sem explicações, com exatamente estas chaves:
- "task_name": nome claro da tarefa ou reunião (string)
- "project_name": nome do projeto no Asana (string ou null)
- "due_date": data no formato YYYY-MM-DD (string ou null). Resolva datas relativas: "hoje"={today_str}, "amanhã"={tomorrow}
- "due_time": horário no formato HH:MM (string ou null). Ex: "15:00", "09:30"
- "notes": participantes, objetivo ou detalhes extras (string, pode ser vazio)

Texto:
{text}"""

    gemini_logger.debug("Extraindo info de tarefa Asana via Gemini")
    
    try:
        response = await model.generate_content_async(prompt)
        raw = response.text.strip()
        
        # Remove possible markdown code block formatting
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
            
        raw = raw.strip()
        
        result = json.loads(raw)
        gemini_logger.info(f"Task info extraída: {result}")
        return result
    except Exception as e:
        gemini_logger.warning(f"Falha ao extrair/parsear JSON do Gemini: {e}")
        return {}


async def extract_asana_task_action(text: str) -> dict:
    """
    Extrai ação e alvo para operações de update/delete/complete em tarefas existentes.

    Retorna dict com:
    - "action": "update" | "delete" | "complete"
    - "task_name": nome da tarefa alvo (para buscar no Asana)
    - "fields": dict com campos novos (somente action=update):
        - "name": novo nome ou null
        - "due_on": nova data YYYY-MM-DD ou null
        - "notes": novas notas ou null
    """
    from datetime import date, timedelta

    model = _get_model()
    if not model:
        return {}

    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    prompt = f"""Hoje é {today} (amanhã é {tomorrow}).
Analise o texto e extraia a ação a ser executada sobre uma tarefa do Asana.

Retorne SOMENTE um JSON válido, sem markdown, com exatamente estas chaves:
- "action": "update" | "delete" | "complete"
- "task_name": nome da tarefa alvo como string (para buscar no Asana)
- "fields": objeto com campos a atualizar (apenas quando action="update"):
  - "name": novo nome da tarefa (string ou null)
  - "due_on": nova data no formato YYYY-MM-DD (string ou null). Resolva datas relativas.
  - "notes": novas notas/descrição (string ou null)

Exemplos de resultado:
{{"action":"complete","task_name":"Reunião com Marcelle","fields":{{}}}}
{{"action":"delete","task_name":"Tarefa X","fields":{{}}}}
{{"action":"update","task_name":"Reunião com Marcelle","fields":{{"due_on":"{tomorrow}","name":null,"notes":null}}}}

Texto: {text}"""

    gemini_logger.debug("Extraindo ação de tarefa Asana via Gemini")
    try:
        response = await model.generate_content_async(prompt)
        raw = response.text.strip()

        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        result = json.loads(raw)
        gemini_logger.info(f"Ação de tarefa extraída: {result}")
        return result
    except Exception as e:
        gemini_logger.warning(f"Falha ao extrair ação de tarefa do Gemini: {e}")
        return {}


async def chat_with_context(messages: list[dict], system_prompt: str | None = None) -> str:
    """
    Chat genérico com contexto. Usado pelo bot para interações livres.
    """
    model = _get_model()
    if not model:
        return "Erro: Chave do Gemini não configurada nesta instância."

    # Gemini usa 'user' e 'model' (ao invés de 'assistant')
    gemini_history = []
    
    # Adiciona o system prompt como a primeira instrução (instruções do sistema)
    # Gemini lida melhor com contexto de sistema no GenerativeModel diretamente, 
    # mas podemos passar como primeira mensagem do usuário se for modelo flash padrão.
    if system_prompt:
        gemini_history.append({"role": "user", "parts": [system_prompt]})
        gemini_history.append({"role": "model", "parts": ["Entendido! Como posso ajudar?"]})

    # Mapeia os roles do padrão OpenAI para o padrão Gemini
    for msg in messages:
        role = msg["role"]
        if role == "system":
            continue  # já lidamos com o system prompt
            
        gemini_role = "user" if role == "user" else "model"
        gemini_history.append({
            "role": gemini_role,
            "parts": [msg["content"]]
        })

    gemini_logger.debug(f"Chamando Gemini com {len(gemini_history)} mensagens de histórico")

    # Inicia o chat com o histórico (excluindo a última mensagem que é a atual)
    chat = model.start_chat(history=gemini_history[:-1])
    
    # Envia a última mensagem do usuário
    last_message = gemini_history[-1]["parts"][0]
    response = await chat.send_message_async(last_message)

    result = response.text
    gemini_logger.info("Resposta do Gemini gerada com sucesso")
    return result
