"""
Integração com Asana - controle completo de tarefas
Operações: criar, ler, atualizar, deletar, concluir, buscar, listar por assignee
"""

import httpx
from datetime import date
from core.logger import asana_logger
from core.context import get_current_instance

ASANA_BASE_URL = "https://app.asana.com/api/1.0"

_TASK_FIELDS = "gid,name,due_on,notes,completed,assignee.name,projects.name,permalink_url,created_at"


def _headers() -> dict:
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


async def _add_task_to_section(task_gid: str, section_gid: str) -> None:
    """Move a tarefa para a seção correta após criação."""
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{ASANA_BASE_URL}/sections/{section_gid}/addTask",
            json={"data": {"task": task_gid}},
            headers=_headers(),
        )
        response.raise_for_status()
    asana_logger.debug(f"Tarefa {task_gid} movida para seção {section_gid}")


async def create_meeting_minutes_task(ata_content: str, meeting_subject: str, meeting_date: date | None = None) -> dict:
    """
    Cria ata de reunião no Asana seguindo o padrão do projeto REUNIÕES E ATAS.

    - Nome: "DD/MM Assunto: [meeting_subject]"
    - Notes: conteúdo processado pelo ChatGPT (Objetivo / Resumo / Próximos passos)
    - Seção: Reuniões Mensais
    """
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")
    project_gid = instance.get("asana_project_gid", "")
    workspace_gid = instance.get("asana_workspace_gid", "")
    section_gid = instance.get("asana_section_gid", "")

    if not token:
        asana_logger.warning("ASANA_ACCESS_TOKEN não configurado. Ata não criada.")
        return {"error": "Asana não configurado"}

    ref_date = meeting_date or date.today()
    task_name = f"{ref_date.strftime('%d/%m')} Assunto: {meeting_subject}"

    task_data: dict = {
        "name": task_name,
        "notes": ata_content,
        "projects": [project_gid] if project_gid else [],
    }
    if workspace_gid:
        task_data["workspace"] = workspace_gid
    payload = {"data": task_data}

    asana_logger.info(f"Criando ata no Asana: '{task_name}'")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{ASANA_BASE_URL}/tasks",
            json=payload,
            headers=_headers(),
        )
        response.raise_for_status()
        data = response.json()

    task_gid = data.get("data", {}).get("gid")

    # Move para a seção "Reuniões Mensais"
    if task_gid and section_gid:
        await _add_task_to_section(task_gid, section_gid)

    asana_logger.info(f"Ata criada com sucesso | gid: {task_gid} | nome: '{task_name}'")
    return data


async def search_project_by_name(name: str) -> str | None:
    """
    Busca um projeto no workspace pelo nome (match parcial, case-insensitive).
    Retorna o GID do primeiro projeto correspondente ou None.
    """
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")
    workspace_gid = instance.get("asana_workspace_gid", "")

    if not token or not workspace_gid:
        return None

    asana_logger.debug(f"Buscando projeto por nome: '{name}'")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/projects",
            headers=_headers(),
            params={
                "workspace": workspace_gid,
                "opt_fields": "name,gid",
                "limit": 100,
            },
        )
        response.raise_for_status()
        projects = response.json().get("data", [])

    name_lower = name.lower()
    for project in projects:
        if name_lower in project.get("name", "").lower():
            asana_logger.info(f"Projeto encontrado: '{project['name']}' | gid: {project['gid']}")
            return project["gid"]

    asana_logger.warning(f"Projeto não encontrado para o nome: '{name}'")
    return None


async def create_task(
    name: str,
    project_gid: str,
    due_on: str | None = None,
    notes: str = "",
) -> dict:
    """
    Cria uma tarefa genérica no Asana.
    due_on: formato YYYY-MM-DD ou None
    """
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")
    workspace_gid = instance.get("asana_workspace_gid", "")

    if not token:
        asana_logger.warning("ASANA_ACCESS_TOKEN não configurado. Tarefa não criada.")
        return {"error": "Asana não configurado"}

    task_data: dict = {"name": name, "projects": [project_gid] if project_gid else []}
    # workspace só é necessário se não houver projeto; com projeto a API infere
    if workspace_gid:
        task_data["workspace"] = workspace_gid
    if due_on:
        task_data["due_on"] = due_on
    if notes:
        task_data["notes"] = notes

    asana_logger.info(f"Criando tarefa no Asana: '{name}' | projeto: {project_gid}")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{ASANA_BASE_URL}/tasks",
            json={"data": task_data},
            headers=_headers(),
        )
        response.raise_for_status()
        data = response.json()

    task_gid = data.get("data", {}).get("gid")
    asana_logger.info(f"Tarefa criada | gid: {task_gid} | nome: '{name}'")
    return data


async def get_task(task_gid: str) -> dict:
    """Retorna os detalhes completos de uma tarefa pelo GID."""
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/tasks/{task_gid}",
            headers=_headers(),
            params={"opt_fields": _TASK_FIELDS},
        )
        response.raise_for_status()
        data = response.json().get("data", {})
    asana_logger.debug(f"Tarefa {task_gid} carregada: '{data.get('name')}'")
    return data


async def update_task(task_gid: str, fields: dict) -> dict:
    """
    Atualiza campos de uma tarefa existente.
    fields pode conter: name, due_on, notes, completed, assignee (gid)
    """
    asana_logger.info(f"Atualizando tarefa {task_gid}: {fields}")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.put(
            f"{ASANA_BASE_URL}/tasks/{task_gid}",
            headers=_headers(),
            json={"data": fields},
        )
        response.raise_for_status()
        data = response.json()
    asana_logger.info(f"Tarefa {task_gid} atualizada com sucesso")
    return data


async def delete_task(task_gid: str) -> bool:
    """Deleta (move para lixeira) uma tarefa pelo GID."""
    asana_logger.info(f"Deletando tarefa {task_gid}")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.delete(
            f"{ASANA_BASE_URL}/tasks/{task_gid}",
            headers=_headers(),
        )
        response.raise_for_status()
    asana_logger.info(f"Tarefa {task_gid} deletada")
    return True


async def complete_task(task_gid: str) -> dict:
    """Marca uma tarefa como concluída."""
    return await update_task(task_gid, {"completed": True})


async def get_my_tasks(
    days_ahead: int | None = None,
    overdue_only: bool = False,
) -> list[dict]:
    """
    Retorna tarefas atribuídas ao dono do token (assignee=me) no workspace.

    - days_ahead=None  → todas as incompletas
    - days_ahead=0     → só com prazo hoje
    - days_ahead=N     → hoje até N dias à frente
    - overdue_only=True → apenas vencidas (prazo antes de hoje)
    """
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")
    workspace_gid = instance.get("asana_workspace_gid", "")

    if not token or not workspace_gid:
        asana_logger.warning("ASANA_ACCESS_TOKEN ou ASANA_WORKSPACE_GID não configurados.")
        return []

    asana_logger.debug(f"Buscando tarefas do assignee=me | workspace={workspace_gid}")
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/tasks",
            headers=_headers(),
            params={
                "assignee": "me",
                "workspace": workspace_gid,
                "opt_fields": _TASK_FIELDS,
                "completed_since": "now",
                "limit": 100,
            },
        )
        response.raise_for_status()
        all_tasks = response.json().get("data", [])

    today = date.today()
    today_str = today.isoformat()

    if overdue_only:
        result = [t for t in all_tasks if t.get("due_on") and t["due_on"] < today_str]
        asana_logger.info(f"{len(result)} tarefa(s) atrasada(s) do assignee")
        return result

    if days_ahead is not None:
        from datetime import timedelta
        limit_str = (today + timedelta(days=days_ahead)).isoformat()
        result = [t for t in all_tasks if t.get("due_on") and today_str <= t["due_on"] <= limit_str]
        asana_logger.info(f"{len(result)} tarefa(s) com prazo até {limit_str}")
        return result

    asana_logger.info(f"{len(all_tasks)} tarefa(s) incompleta(s) do assignee")
    return all_tasks


async def search_task_by_name(query: str) -> list[dict]:
    """
    Busca tarefas por nome via typeahead do Asana.
    Retorna até 10 resultados com gid, name, permalink_url.
    """
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")
    workspace_gid = instance.get("asana_workspace_gid", "")

    if not token or not workspace_gid:
        return []

    asana_logger.debug(f"Buscando tarefa por nome: '{query}'")
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/workspaces/{workspace_gid}/typeahead",
            headers=_headers(),
            params={
                "resource_type": "task",
                "query": query,
                "opt_fields": "gid,name,permalink_url",
            },
        )
        response.raise_for_status()
        results = response.json().get("data", [])

    asana_logger.info(f"{len(results)} resultado(s) para busca: '{query}'")
    return results


async def get_project_tasks(project_gid: str | None = None) -> list[dict]:
    """Lista todas as tarefas incompletas de um projeto no Asana."""
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")
    
    if not token:
        asana_logger.warning("ASANA_ACCESS_TOKEN não configurado.")
        return []

    project = project_gid or instance.get("asana_project_gid", "")
    asana_logger.debug(f"Buscando tarefas do projeto Asana: {project}")

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/projects/{project}/tasks",
            headers=_headers(),
            params={
                "opt_fields": "name,due_on,assignee,completed,notes",
                "completed_since": "now",  # apenas incompletas
            },
        )
        response.raise_for_status()
        tasks = response.json().get("data", [])
        asana_logger.info(f"{len(tasks)} tarefas encontradas no projeto Asana")
        return tasks


async def get_tasks_due_soon(days_ahead: int = 1, project_gid: str | None = None) -> list[dict]:
    """
    Retorna tarefas incompletas com vencimento nos próximos N dias (incluindo hoje).
    days_ahead=0 → só hoje | days_ahead=1 → hoje + amanhã
    """
    from datetime import timedelta

    instance = get_current_instance()
    token = instance.get("asana_access_token", "")

    if not token:
        return []

    today = date.today()
    limit_date = today + timedelta(days=days_ahead)
    project = project_gid or instance.get("asana_project_gid", "")

    asana_logger.debug(f"Buscando tarefas vencendo até {limit_date.isoformat()} no projeto {project}")

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/projects/{project}/tasks",
            headers=_headers(),
            params={
                "opt_fields": "name,due_on,assignee.name,completed,gid",
                "completed_since": "now",
            },
        )
        response.raise_for_status()
        all_tasks = response.json().get("data", [])

    due_soon = [
        t for t in all_tasks
        if t.get("due_on") and today.isoformat() <= t["due_on"] <= limit_date.isoformat()
    ]
    asana_logger.info(f"{len(due_soon)} tarefa(s) vencendo nos próximos {days_ahead} dia(s)")
    return due_soon


async def get_overdue_tasks(project_gid: str | None = None) -> list[dict]:
    """Retorna tarefas incompletas com vencimento no passado."""
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")

    if not token:
        return []

    today = date.today().isoformat()
    project = project_gid or instance.get("asana_project_gid", "")

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{ASANA_BASE_URL}/projects/{project}/tasks",
            headers=_headers(),
            params={
                "opt_fields": "name,due_on,assignee.name,completed,gid",
                "completed_since": "now",
            },
        )
        response.raise_for_status()
        all_tasks = response.json().get("data", [])

    overdue = [
        t for t in all_tasks
        if t.get("due_on") and t["due_on"] < today
    ]
    asana_logger.info(f"{len(overdue)} tarefa(s) atrasada(s)")
    return overdue


async def add_comment_to_task(task_gid: str, text: str) -> dict:
    """Adiciona um comentário a uma tarefa no Asana."""
    instance = get_current_instance()
    token = instance.get("asana_access_token", "")

    if not token:
        asana_logger.warning("ASANA_ACCESS_TOKEN não configurado. Comentário não adicionado.")
        return {"error": "Asana não configurado"}

    asana_logger.info(f"Adicionando comentário na tarefa {task_gid}: '{text[:30]}...'")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{ASANA_BASE_URL}/tasks/{task_gid}/stories",
            headers=_headers(),
            json={"data": {"text": text}},
        )
        response.raise_for_status()
        data = response.json()
    asana_logger.info(f"Comentário adicionado na tarefa {task_gid}")
    return data
