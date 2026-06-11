"""
BOT - Handler para criar, atualizar, deletar e concluir tarefas no Asana via WhatsApp

Fluxo de criação:
  Usuário pede para criar tarefa → Gemini extrai dados → cria no Asana → confirma

Fluxo de update/delete/complete:
  Usuário pede ação → Gemini extrai nome da tarefa + ação → busca task → executa

Triggers definidos abaixo para cada ação.
"""

from datetime import date as _date
from core.logger import bot_logger
from integrations.gemini_client import extract_asana_task_info, extract_asana_task_action
from integrations.asana_client import (
    search_project_by_name,
    create_task,
    get_task,
    search_task_by_name,
    update_task,
    delete_task,
    complete_task,
)
from integrations.evolution_api import send_text_message
from integrations.redis_client import (
    save_last_task,
    get_last_task,
    save_asana_pending,
    get_asana_pending,
    clear_asana_pending,
)

ASANA_UPDATE_TRIGGERS = [
    "atualizar a tarefa", "atualiza a tarefa", "atualizar tarefa", "atualiza tarefa",
    "alterar a tarefa", "altera a tarefa", "alterar tarefa", "altera tarefa",
    "modificar a tarefa", "modifica a tarefa", "modificar tarefa",
    "renomear a tarefa", "renomeia a tarefa", "renomear tarefa",
    "muda o prazo", "muda a data", "mudar o prazo", "mudar a data",
    "muda o nome da tarefa", "muda as notas", "atualiza o prazo",
    "editar a tarefa", "editar tarefa", "edita a tarefa",
    "mudar a tarefa", "muda a tarefa",
]

ASANA_DELETE_TRIGGERS = [
    "deletar a tarefa", "deleta a tarefa", "deletar tarefa", "deleta tarefa",
    "apagar a tarefa", "apaga a tarefa", "apagar tarefa",
    "excluir a tarefa", "exclui a tarefa", "excluir tarefa",
    "remover a tarefa", "remove a tarefa", "remover tarefa",
    "delete a tarefa", "delete tarefa",
]

ASANA_COMPLETE_TRIGGERS = [
    "concluir a tarefa", "conclui a tarefa", "concluir tarefa",
    "marcar como concluída", "marca como concluída",
    "marcar como feita", "marca como feita",
    "finalizar a tarefa", "finaliza a tarefa", "finalizar tarefa",
    "terminar a tarefa", "termina a tarefa", "terminar tarefa",
    "fechar a tarefa", "fecha a tarefa", "fechar tarefa",
    "marcar como concluido", "marca como concluido",
    "completar a tarefa", "completa a tarefa",
    "tarefa concluída", "tarefa feita",
]

ASANA_SEARCH_TRIGGERS = [
    "buscar tarefa", "busca tarefa", "procurar tarefa",
    "encontrar tarefa", "encontra a tarefa",
    "qual o link da tarefa", "qual o link da reunião",
    "me manda o link da tarefa", "me passa o link",
    "link da tarefa", "link da reunião",
]

ASANA_TASK_TRIGGERS = [
    # tarefa direta
    "coloque uma tarefa",
    "coloca uma tarefa",
    "criar tarefa",
    "crie uma tarefa",
    "cria uma tarefa",
    "adicionar tarefa",
    "adicione uma tarefa",
    "nova tarefa no asana",
    "tarefa no asana",
    "add task",
    # reunião / agendamento
    "marque uma reunião",
    "marca uma reunião",
    "marcar reunião",
    "agendar reunião",
    "agende uma reunião",
    "agende a reunião",
    "criar uma reunião",
    "crie uma reunião",
    "nova reunião",
    "reunião no asana",
    "adicione uma reunião",
    # ata
    "link da ata",
    "ata no asana",
    "criar ata",
    "crie uma ata",
    "gerar ata",
    # genéricos com asana explícito
    "no asana",
    "no asana.",
    "pro asana",
    "criar no asana",
    "coloca no asana",
    "coloque no asana",
    "adiciona no asana",
]


def is_asana_task_request(text: str) -> bool:
    lower = text.lower()
    return any(trigger in lower for trigger in ASANA_TASK_TRIGGERS)


def is_asana_update_request(text: str) -> bool:
    lower = text.lower()
    return any(trigger in lower for trigger in ASANA_UPDATE_TRIGGERS)


def is_asana_delete_request(text: str) -> bool:
    lower = text.lower()
    return any(trigger in lower for trigger in ASANA_DELETE_TRIGGERS)


def is_asana_complete_request(text: str) -> bool:
    lower = text.lower()
    return any(trigger in lower for trigger in ASANA_COMPLETE_TRIGGERS)


def is_asana_search_request(text: str) -> bool:
    lower = text.lower()
    return any(trigger in lower for trigger in ASANA_SEARCH_TRIGGERS)


def _is_affirmative(text: str) -> bool:
    return any(w in text for w in [
        "sim", "pode", "pode ser", "confirma", "confirmo", "ok", "bora",
        "vai", "cria assim", "usa essa", "usa ela", "certo", "perfeito",
        "isso", "exato", "yes", "yep", "é isso", "tá bom", "ta bom",
        "com base", "baseada", "usando ela", "esse padrão", "esse padrao",
    ])


def _is_negative(text: str) -> bool:
    return any(w in text for w in [
        "não", "nao", "nope", "no ", " no", "cancela", "ignora",
        "cria sem", "cria nova", "nova tarefa", "sem template",
        "do zero", "do inicio", "do início", "diferente", "nenhuma",
    ])


async def handle_asana_task_request(sender_phone: str, text: str) -> None:
    """
    Fluxo de criação de tarefa no Asana com verificação de template:
    1. Extrai dados da mensagem
    2. Busca tasks similares no Asana
    3. Se achar → pergunta se cria baseada na estrutura existente (salva estado no Redis)
    4. Se não achar → cria direto
    """
    bot_logger.info(f"[BOT] Solicitação de tarefa Asana de {sender_phone}")

    try:
        await send_text_message(to=sender_phone, text="Anotado, deixa eu checar o Asana...")

        task_info = await extract_asana_task_info(text)
        if not task_info or not task_info.get("task_name"):
            bot_logger.warning(f"[BOT] Não foi possível extrair info da tarefa: {text!r}")
            await send_text_message(
                to=sender_phone,
                text="Não entendi bem. Me passa: nome da tarefa, projeto e data (se tiver).",
            )
            return

        task_name: str = task_info["task_name"]
        bot_logger.info(f"[BOT] Tarefa extraída: '{task_name}' | projeto: '{task_info.get('project_name')}' | data: {task_info.get('due_date')}")

        # ── Busca tasks similares no Asana ──────────────────────────────────
        similar = await search_task_by_name(task_name)

        if similar:
            # Carrega detalhes completos da primeira opção (template)
            template_raw = await get_task(similar[0]["gid"])
            template = {
                "gid": template_raw.get("gid"),
                "name": template_raw.get("name"),
                "notes": template_raw.get("notes", ""),
                "permalink_url": template_raw.get("permalink_url", ""),
                "projects": [
                    {"gid": p.get("gid"), "name": p.get("name")}
                    for p in template_raw.get("projects", [])
                ],
            }

            # Salva estado: esperando escolha do usuário
            pending = {
                "step": "awaiting_template_choice",
                "task_info": task_info,
                "template": template,
            }
            if len(similar) > 1:
                pending["options"] = [
                    {"gid": t["gid"], "name": t["name"], "permalink_url": t.get("permalink_url", "")}
                    for t in similar[:3]
                ]

            await save_asana_pending(sender_phone, pending)

            # Mensagem para o usuário
            project_name = template["projects"][0]["name"] if template["projects"] else None
            lines = [f"Achei uma task bem parecida no Asana: *{template['name']}*"]
            if project_name:
                lines.append(f"Projeto: {project_name}")
            if template["notes"]:
                preview = template["notes"][:200].strip()
                if len(template["notes"]) > 200:
                    preview += "..."
                lines.append(f"\nEstrutura:\n{preview}")

            if len(similar) > 1:
                lines.append(f"\n_(encontrei {len(similar)} tasks parecidas, usando a mais relevante)_")

            lines.append("\nCrio a nova seguindo esse padrão? (confirma ou diz 'não' pra criar do zero)")
            await send_text_message(to=sender_phone, text="\n".join(lines))

        else:
            # Nenhuma similar — cria direto
            await _execute_create_task(sender_phone, task_info)

    except Exception as exc:
        bot_logger.exception(f"[BOT] Falha inesperada ao criar tarefa Asana: {exc}")
        await send_text_message(
            to=sender_phone,
            text="Tive um problema técnico ao processar a tarefa. Tenta de novo em instantes.",
        )


async def handle_asana_pending_response(sender_phone: str, text: str, pending: dict) -> None:
    """
    Continua um fluxo Asana que estava aguardando resposta do usuário.
    Mantém raciocínio e contexto completos — não esquece o que foi dito.
    """
    step = pending.get("step")
    lower = text.lower().strip()

    if step == "awaiting_template_choice":
        task_info = pending["task_info"]
        template = pending.get("template", {})

        if _is_affirmative(lower):
            await clear_asana_pending(sender_phone)
            await _execute_create_task(sender_phone, task_info, template=template)

        elif _is_negative(lower):
            await clear_asana_pending(sender_phone)
            await send_text_message(to=sender_phone, text="Ok, vou criar do zero.")
            await _execute_create_task(sender_phone, task_info)

        else:
            # Usuário pode estar adicionando informações ou modificando algo
            # Mescla o texto novo com o contexto já extraído
            bot_logger.info(f"[BOT] Resposta ambígua no fluxo pendente, tentando mesclar info: {text!r}")
            extra_info = await extract_asana_task_info(
                f"{task_info.get('task_name', '')} {text}"
            )
            if extra_info and extra_info.get("task_name"):
                # Atualiza task_info com novos dados sem perder os originais
                merged = {**task_info, **{k: v for k, v in extra_info.items() if v}}
                pending["task_info"] = merged
                await save_asana_pending(sender_phone, pending)
                task_info = merged

            tname = task_info.get("task_name", "a tarefa")
            due = ""
            if task_info.get("due_date"):
                try:
                    d = _date.fromisoformat(task_info["due_date"])
                    due = f" para {d.strftime('%d/%m/%Y')}"
                except ValueError:
                    due = f" para {task_info['due_date']}"

            lines = [
                f"Confirma: criar *{tname}*{due}",
                f"baseada em *{template.get('name', 'task existente')}*?",
                "(responde 'sim' ou 'não')",
            ]
            await send_text_message(to=sender_phone, text="\n".join(lines))

    elif step == "confirm_ata_drive":
        from bot.handlers.meeting_minutes import handle_ata_drive_upload
        await handle_ata_drive_upload(sender_phone, text, pending)

    else:
        # Step desconhecido — limpa e recomeça
        bot_logger.warning(f"[BOT] Step pendente desconhecido '{step}', limpando estado")
        await clear_asana_pending(sender_phone)
        await send_text_message(
            to=sender_phone,
            text="Perdi o fio. O que você quer fazer no Asana?",
        )


async def _execute_create_task(
    sender_phone: str,
    task_info: dict,
    template: dict | None = None,
) -> None:
    """
    Cria a tarefa no Asana e confirma para o usuário.
    Se template for passado, usa o projeto e a estrutura de notas como base.
    """
    task_name: str = task_info["task_name"]
    project_name: str | None = task_info.get("project_name")
    due_date: str | None = task_info.get("due_date")
    due_time: str | None = task_info.get("due_time")
    notes: str = task_info.get("notes", "")

    if due_time:
        notes = f"Horário: {due_time}\n{notes}".strip()

    # Herda projeto do template se o usuário não especificou
    template_project_gid: str | None = None
    template_project_name: str | None = None
    if template and template.get("projects"):
        first = template["projects"][0]
        template_project_gid = first.get("gid")
        template_project_name = first.get("name")
        if not project_name:
            project_name = template_project_name

    # Herda estrutura de notas do template (se não tiver notas próprias)
    if template and not notes and template.get("notes"):
        notes = template["notes"]

    # Resolve GID do projeto
    project_gid: str | None = None
    if template_project_gid and (not project_name or project_name == template_project_name):
        project_gid = template_project_gid  # mais confiável que buscar por nome
    elif project_name:
        project_gid = await search_project_by_name(project_name)

    if not project_gid:
        from core.config import get_settings as _gs
        project_gid = _gs().services.ai.asana.project_gid

    if not project_gid:
        bot_logger.error("[BOT] Nenhum projeto Asana disponível")
        await send_text_message(
            to=sender_phone,
            text="Não achei o projeto no Asana. Me diz o nome exato do projeto e tento de novo.",
        )
        return

    result = await create_task(name=task_name, project_gid=project_gid, due_on=due_date, notes=notes)
    task_gid = result.get("data", {}).get("gid")
    task_link = f"https://app.asana.com/0/{project_gid}/{task_gid}" if task_gid else None

    lines = [f"Feito! *{task_name}*"]
    if project_name:
        lines.append(f"Projeto: {project_name}")
    if due_date:
        try:
            d = _date.fromisoformat(due_date)
            lines.append(f"Data: {d.strftime('%d/%m/%Y')}" + (f" às {due_time}" if due_time else ""))
        except ValueError:
            lines.append(f"Data: {due_date}" + (f" às {due_time}" if due_time else ""))
    if template:
        lines.append(f"Baseada em: _{template.get('name', '')}_")
    if task_link:
        lines.append(f"Link: {task_link}")

    await send_text_message(to=sender_phone, text="\n".join(lines))
    bot_logger.info(f"[BOT] Tarefa criada | gid: {task_gid} | nome: '{task_name}' | template: {bool(template)}")

    await save_last_task(sender_phone, {
        "name": task_name,
        "link": task_link,
        "project": project_name,
        "date": due_date,
    })


# ── Helpers compartilhados ───────────────────────────────────────────────────

async def _resolve_task(sender_phone: str, task_name: str | None) -> dict | None:
    """
    Tenta encontrar uma tarefa pelo nome.
    Fallback: última tarefa criada no Redis.
    Retorna o dict da tarefa ou None (já envia mensagem de erro ao usuário).
    """
    if task_name:
        results = await search_task_by_name(task_name)
        if len(results) == 1:
            return results[0]
        if len(results) > 1:
            lines = [f"Encontrei {len(results)} tarefas com esse nome. Qual você quer?"]
            for t in results[:5]:
                lines.append(f"• {t['name']}")
            await send_text_message(to=sender_phone, text="\n".join(lines))
            return None
        # Não achou pelo nome — tenta Redis
        bot_logger.warning(f"[BOT] Tarefa '{task_name}' não encontrada na busca, tentando Redis")

    last = await get_last_task(sender_phone)
    if last and last.get("link"):
        # Extrai o GID da URL salva: .../0/{project_gid}/{task_gid}
        link = last["link"]
        task_gid = link.rstrip("/").split("/")[-1]
        return {"gid": task_gid, "name": last.get("name", "última tarefa"), "permalink_url": link}

    await send_text_message(
        to=sender_phone,
        text="Não achei a tarefa. Me passa o nome exato e tento novamente.",
    )
    return None


# ── Handler: Atualizar tarefa ────────────────────────────────────────────────

async def handle_asana_update_request(sender_phone: str, text: str) -> None:
    """
    Atualiza uma tarefa existente: nome, data ou notas.
    Usa Gemini para extrair qual tarefa e o que muda.
    """
    bot_logger.info(f"[BOT] Solicitação de update Asana de {sender_phone}")
    try:
        info = await extract_asana_task_action(text)
        task_name: str | None = info.get("task_name")
        fields: dict = {k: v for k, v in (info.get("fields") or {}).items() if v is not None}

        if not fields:
            await send_text_message(
                to=sender_phone,
                text="Não entendi o que muda. Me passa: qual tarefa e o que alterar (nome, data ou notas).",
            )
            return

        task = await _resolve_task(sender_phone, task_name)
        if not task:
            return

        await update_task(task["gid"], fields)

        parts = [f"Tarefa *{task['name']}* atualizada:"]
        if "name" in fields:
            parts.append(f"• Novo nome: {fields['name']}")
        if "due_on" in fields:
            try:
                from datetime import date as _date
                d = _date.fromisoformat(fields["due_on"])
                parts.append(f"• Nova data: {d.strftime('%d/%m/%Y')}")
            except ValueError:
                parts.append(f"• Nova data: {fields['due_on']}")
        if "notes" in fields:
            parts.append("• Notas atualizadas")
        if task.get("permalink_url"):
            parts.append(f"Link: {task['permalink_url']}")

        await send_text_message(to=sender_phone, text="\n".join(parts))
        bot_logger.info(f"[BOT] Tarefa {task['gid']} atualizada: {fields}")

    except Exception as exc:
        bot_logger.exception(f"[BOT] Falha ao atualizar tarefa: {exc}")
        await send_text_message(
            to=sender_phone,
            text="Tive um problema técnico ao atualizar a tarefa. Tenta de novo.",
        )


# ── Handler: Deletar tarefa ──────────────────────────────────────────────────

async def handle_asana_delete_request(sender_phone: str, text: str) -> None:
    """Deleta (move para lixeira) uma tarefa pelo nome."""
    bot_logger.info(f"[BOT] Solicitação de delete Asana de {sender_phone}")
    try:
        info = await extract_asana_task_action(text)
        task_name: str | None = info.get("task_name")

        task = await _resolve_task(sender_phone, task_name)
        if not task:
            return

        await delete_task(task["gid"])
        await send_text_message(
            to=sender_phone,
            text=f"Feito. Tarefa *{task['name']}* removida do Asana.",
        )
        bot_logger.info(f"[BOT] Tarefa {task['gid']} deletada")

    except Exception as exc:
        bot_logger.exception(f"[BOT] Falha ao deletar tarefa: {exc}")
        await send_text_message(
            to=sender_phone,
            text="Tive um problema técnico ao deletar a tarefa. Tenta de novo.",
        )


# ── Handler: Concluir tarefa ─────────────────────────────────────────────────

async def handle_asana_complete_request(sender_phone: str, text: str) -> None:
    """Marca uma tarefa como concluída."""
    bot_logger.info(f"[BOT] Solicitação de complete Asana de {sender_phone}")
    try:
        info = await extract_asana_task_action(text)
        task_name: str | None = info.get("task_name")

        task = await _resolve_task(sender_phone, task_name)
        if not task:
            return

        await complete_task(task["gid"])
        await send_text_message(
            to=sender_phone,
            text=f"✅ Tarefa *{task['name']}* marcada como concluída.",
        )
        bot_logger.info(f"[BOT] Tarefa {task['gid']} concluída")

    except Exception as exc:
        bot_logger.exception(f"[BOT] Falha ao concluir tarefa: {exc}")
        await send_text_message(
            to=sender_phone,
            text="Tive um problema técnico ao concluir a tarefa. Tenta de novo.",
        )
